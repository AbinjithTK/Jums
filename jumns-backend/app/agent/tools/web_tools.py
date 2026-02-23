"""Web search tool — internet access via Gemini's Google Search grounding.

Mirrors the Projectj web_search tool: uses Gemini's built-in Google Search
to provide real-time information for goal planning, tips, and research.
"""

from __future__ import annotations

import os

from strands import tool


@tool
def web_search(query: str, context: str = "") -> dict:
    """Search the internet for real-time information using Google Search.

    Use when the user asks about current events, needs tips/advice,
    wants to research something for their goals, or when you need
    up-to-date information to help plan their achievement path.

    Examples:
    - "best training plan for half marathon beginners"
    - "how to learn Spanish in 6 months"
    - "healthy meal prep ideas for weight loss"

    Args:
        query: The search query to look up.
        context: Why you're searching — helps refine results.

    Returns:
        Dict with answer text and source URLs.
    """
    api_key = os.getenv("GEMINI_API_KEY", "")
    if not api_key:
        return {"error": "Web search not configured", "query": query}

    try:
        import httpx

        prompt = (
            f"Search the internet and provide a comprehensive answer about: {query}"
        )
        if context:
            prompt += f"\nContext: {context}"
        prompt += (
            "\n\nProvide specific, actionable information with key facts, "
            "tips, or data points. Include source references when possible."
        )

        resp = httpx.post(
            "https://generativelanguage.googleapis.com/v1beta/models/"
            "gemini-2.5-flash:generateContent",
            params={"key": api_key},
            json={
                "contents": [{"parts": [{"text": prompt}]}],
                "tools": [{"google_search": {}}],
                "generationConfig": {"maxOutputTokens": 2048},
            },
            timeout=30.0,
        )
        resp.raise_for_status()
        data = resp.json()

        text = ""
        candidates = data.get("candidates", [])
        if candidates:
            parts = candidates[0].get("content", {}).get("parts", [])
            text = " ".join(p.get("text", "") for p in parts)

        # Extract grounding sources
        grounding = candidates[0].get("groundingMetadata", {}) if candidates else {}
        chunks = grounding.get("groundingChunks", [])
        sources = [
            {"title": c.get("web", {}).get("title", ""), "url": c.get("web", {}).get("uri", "")}
            for c in chunks[:5]
        ]

        return {"answer": text or "No results found.", "sources": sources, "query": query}

    except Exception as e:
        return {"error": f"Web search failed: {str(e)}", "query": query}
