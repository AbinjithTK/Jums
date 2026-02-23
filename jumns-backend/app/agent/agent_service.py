"""Strands Agent service — orchestrates AI model invocation with 25 tools.

Uses the Strands Agents SDK with GeminiModel. Tools are @tool-decorated
functions that receive user_id via functools.partial injection.
Supports failover (primary Gemini → retry → failover provider),
conversation history via SlidingWindowConversationManager,
and card block parsing for structured UI responses.

Architecture borrowed from OpenClaw's Pi Agent runtime:
- Tool policy: all tools available per session (single-user app)
- Failover: primary → retry → failover provider
- Context: memory search + conversation history injected into system prompt
- Proactive: scheduled invocations for briefings, plan reviews, suggestions
"""

from __future__ import annotations

import functools
import inspect
import json
import logging
import os
import re
from typing import Any

from app.agent.system_prompt import build_system_prompt
from app.agent.tools import ALL_TOOLS
from app.db.repositories.messages import MessagesRepository
from app.db.repositories.users import UsersRepository
from app.exceptions import AgentUnavailableError
from app.memory.memory_service import MemoryService

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Card block parser — extracts :::card{type="X"} ... ::: from agent output
# ---------------------------------------------------------------------------

_CARD_PATTERN = re.compile(
    r':::card\{type="([^"]+)"\}\s*(.*?)\s*:::', re.DOTALL
)


def parse_card_blocks(text: str) -> tuple[str, str | None, dict | None]:
    """Parse card blocks from agent response text.

    Returns (clean_text, card_type, card_data).
    """
    match = _CARD_PATTERN.search(text)
    if not match:
        return text, None, None

    card_type = match.group(1)
    card_body = match.group(2).strip()

    card_data: dict | None = None
    try:
        card_data = json.loads(card_body)
    except (json.JSONDecodeError, ValueError):
        card_data = {"content": card_body}

    clean_text = text[: match.start()].strip()
    trailing = text[match.end() :].strip()
    if trailing:
        clean_text = f"{clean_text}\n{trailing}" if clean_text else trailing

    return clean_text, card_type, card_data


# ---------------------------------------------------------------------------
# Tool binding — inject user_id into @tool-decorated functions
# ---------------------------------------------------------------------------


def _bind_tools(user_id: str) -> list:
    """Create user-bound copies of all @tool-decorated functions.

    Strands @tool functions declare user_id as a parameter so the LLM
    sees it in the schema. We use functools.partial to pre-fill it,
    then copy over __name__, __doc__, and the tool metadata attributes
    that Strands uses for tool registration.
    """
    bound = []
    for fn in ALL_TOOLS:
        sig = inspect.signature(fn)
        if "user_id" in sig.parameters:
            wrapper = functools.partial(fn, user_id=user_id)
            functools.update_wrapper(wrapper, fn)
            # Preserve Strands tool metadata
            for attr in ("_tool_spec", "tool_spec", "TOOL_SPEC"):
                val = getattr(fn, attr, None)
                if val is not None:
                    setattr(wrapper, attr, val)
            bound.append(wrapper)
        else:
            bound.append(fn)
    return bound


# ---------------------------------------------------------------------------
# AgentService
# ---------------------------------------------------------------------------


class AgentService:
    """Wraps the Strands Agents SDK for chat and proactive invocations.

    Each call creates a fresh Agent instance with user-bound tools.
    Conversation history is loaded from DynamoDB and fed as messages.
    """

    def __init__(self):
        self._users_repo = UsersRepository()
        self._messages_repo = MessagesRepository()
        self._memory_service = MemoryService()

    # -- public API ----------------------------------------------------------

    async def invoke(self, user_id: str, message: str) -> dict[str, Any]:
        """Run a chat turn. Returns dict with content, cardType, cardData."""
        settings = self._users_repo.get_settings(user_id)
        system_prompt = build_system_prompt(settings)

        # Enrich system prompt with relevant memories
        system_prompt += self._build_memory_context(user_id, message)

        # Load conversation history for context
        history_messages = self._load_history(user_id)

        # Invoke with failover
        try:
            response_text = self._invoke_with_failover(
                system_prompt, history_messages, message, user_id,
            )
        except Exception as exc:
            logger.exception("Agent invocation failed for user %s", user_id)
            raise AgentUnavailableError() from exc

        # Parse card blocks
        clean_text, card_type, card_data = parse_card_blocks(response_text)

        # Persist messages
        self._messages_repo.create_message(user_id, {
            "role": "user",
            "type": "text",
            "content": message,
        })
        assistant_msg: dict[str, Any] = {
            "role": "assistant",
            "type": "card" if card_type else "text",
            "content": clean_text or response_text,
        }
        if card_type:
            assistant_msg["cardType"] = card_type
            assistant_msg["cardData"] = card_data
        self._messages_repo.create_message(user_id, assistant_msg)

        # Store memory (best-effort)
        try:
            self._memory_service.extract_and_store(
                user_id,
                f"User: {message}\nAssistant: {clean_text or response_text}",
            )
        except Exception:
            pass

        return {
            "content": clean_text or response_text,
            "cardType": card_type,
            "cardData": card_data,
        }

    async def invoke_proactive(
        self, user_id: str, prompt_type: str,
    ) -> dict[str, Any] | None:
        """Proactive invocation for scheduled briefings, plan reviews, etc."""
        prompts = {
            "morning_briefing": (
                "Generate a morning briefing. Use get_daily_summary to check "
                "the user's goals, tasks, and reminders. Create a briefing card "
                "using :::card{type=\"daily_briefing\"} format with JSON payload: "
                "title, greeting, tasks (array), goals (array), reminders (array). "
                "If nothing meaningful, respond with __SILENT__."
            ),
            "evening_journal": (
                "Generate an evening journal prompt. Use get_daily_summary to "
                "review the day. Create a journal card using "
                ":::card{type=\"journal_prompt\"} format with JSON payload: "
                "title, reflection_questions (array), accomplishments (array). "
                "If nothing meaningful, respond with __SILENT__."
            ),
            "reminder_check": (
                "Check for active reminders due now. Use get_reminders. "
                "For each due reminder, create a :::card{type=\"reminder\"} block. "
                "If none due, respond with __SILENT__."
            ),
            "plan_review": (
                "Review all active goals. Use get_goals to find active goals, "
                "then call adapt_plan for each. If any have overdue tasks, call "
                "reschedule_failed_tasks. Summarize findings using "
                ":::card{type=\"progress_report\"} format. "
                "If nothing to report, respond with __SILENT__."
            ),
            "smart_suggestions": (
                "Generate proactive suggestions. Call smart_suggest with "
                "focus='all'. Present the top suggestions using "
                ":::card{type=\"suggestion\"} format. "
                "If no suggestions, respond with __SILENT__."
            ),
        }

        prompt = prompts.get(prompt_type)
        if not prompt:
            return None

        try:
            result = await self.invoke(user_id, prompt)
            if "__SILENT__" in result.get("content", ""):
                return None
            return result
        except AgentUnavailableError:
            return None

    # -- private helpers -----------------------------------------------------

    def _build_memory_context(self, user_id: str, message: str) -> str:
        """Search vector memory and return a context block for the prompt."""
        try:
            memories = self._memory_service.search(user_id, message, top_k=3)
            if memories:
                snippets = [m.get("content", "") for m in memories if m.get("content")]
                if snippets:
                    return (
                        "\n\n## Relevant Memories\n"
                        + "\n".join(f"- {s}" for s in snippets)
                    )
        except Exception:
            pass
        return ""

    def _load_history(self, user_id: str) -> list[dict]:
        """Load recent conversation history from DynamoDB."""
        history = self._messages_repo.list_messages(user_id)
        recent = history[-20:] if len(history) > 20 else history
        messages = []
        for msg in recent:
            role = msg.get("role", "user")
            content = msg.get("content", "")
            if role in ("user", "assistant") and content:
                messages.append({"role": role, "content": [{"text": content}]})
        return messages

    def _invoke_with_failover(
        self,
        system_prompt: str,
        history: list[dict],
        user_message: str,
        user_id: str,
    ) -> str:
        """Try primary model, retry once, then failover model."""
        gemini_key = os.getenv("GEMINI_API_KEY", "")

        # Attempt 1 & 2: primary Gemini
        for attempt in range(2):
            try:
                return self._call_agent(
                    system_prompt, history, user_message, user_id,
                    model_id="gemini-2.5-flash",
                    api_key=gemini_key,
                )
            except Exception:
                if attempt == 0:
                    logger.warning("Primary model attempt 1 failed, retrying...")
                    continue
                logger.warning("Primary model attempt 2 failed, trying failover...")
                break

        # Attempt 3: failover provider
        failover_provider = os.getenv("FAILOVER_MODEL_ID", "")
        failover_key = os.getenv("FAILOVER_API_KEY", "")
        if failover_provider and failover_key:
            try:
                return self._call_agent(
                    system_prompt, history, user_message, user_id,
                    model_id=failover_provider,
                    api_key=failover_key,
                )
            except Exception:
                logger.exception("Failover model also failed")

        raise AgentUnavailableError()

    def _call_agent(
        self,
        system_prompt: str,
        history: list[dict],
        user_message: str,
        user_id: str,
        model_id: str,
        api_key: str,
    ) -> str:
        """Create a Strands Agent and invoke it with the user's message."""
        try:
            from strands import Agent
            from strands.models.gemini import GeminiModel

            model = GeminiModel(
                client_args={"api_key": api_key},
                model_id=model_id,
                params={
                    "temperature": 0.7,
                    "max_output_tokens": 4096,
                    "top_p": 0.9,
                },
            )

            tools = _bind_tools(user_id)

            agent = Agent(
                model=model,
                system_prompt=system_prompt,
                tools=tools,
                messages=history,
                callback_handler=None,  # no streaming in Lambda
            )

            # Invoke — Strands Agent accepts a string prompt
            result = agent(user_message)
            return str(result)

        except ImportError:
            # Strands not installed — dev mode fallback
            logger.warning("Strands SDK not installed, using dev fallback")
            return (
                f"I received your message: '{user_message}'. "
                "The AI agent is running in dev mode without the Strands SDK. "
                "Deploy to Lambda with strands-agents[gemini] for full tool access."
            )
