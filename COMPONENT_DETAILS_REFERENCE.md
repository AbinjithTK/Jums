# Component Details Reference

## Android Gateway Communication Deep Dive

### GatewaySession Architecture

**Location**: `jum/apps/android/app/src/main/java/ai/openclaw/android/gateway/GatewaySession.kt`

**Dual Session Pattern**:
```kotlin
// Operator session: UI control, chat, settings
private val operatorSession = GatewaySession(
  onConnected = { name, remote, mainSessionKey -> ... },
  onDisconnected = { message -> ... },
  onEvent = { event, payloadJson -> ... }
)

// Node session: Device capabilities, invoke commands
private val nodeSession = GatewaySession(
  onConnected = { ... },
  onDisconnected = { ... },
  onEvent = { ... },
  onInvoke = { req -> handleInvoke(req.command, req.paramsJson) }
)
```

**Why Dual Sessions**:
- Operator: Receives chat messages, settings updates, events
- Node: Handles device commands (camera, screen, canvas)
- Separation allows independent reconnection and capability negotiation

### Connection Flow

```
1. GatewayDiscovery finds endpoints via Bonjour
2. User selects endpoint or manual host/port
3. connect(endpoint) called
4. Both sessions connect with:
   - Device identity (from DeviceIdentityStore)
   - Auth token/password (from DeviceAuthStore)
   - TLS params (certificate pinning)
   - Client info (version, platform, capabilities)
5. onConnected callbacks fire
6. Ready for chat and invoke commands
```

### Capabilities & Commands

**Capabilities** (what device can do):
```kotlin
private fun buildCapabilities(): List<String> = buildList {
  add(OpenClawCapability.Canvas.rawValue)
  add(OpenClawCapability.Screen.rawValue)
  if (cameraEnabled.value) add(OpenClawCapability.Camera.rawValue)
  if (sms.canSendSms()) add(OpenClawCapability.Sms.rawValue)
  if (voiceWakeMode.value != VoiceWakeMode.Off) add(OpenClawCapability.VoiceWake.rawValue)
  if (locationMode.value != LocationMode.Off) add(OpenClawCapability.Location.rawValue)
}
```

**Invoke Commands** (what agent can request):
```kotlin
private fun buildInvokeCommands(): List<String> = buildList {
  add(OpenClawCanvasCommand.Present.rawValue)
  add(OpenClawCanvasCommand.Hide.rawValue)
  add(OpenClawCanvasCommand.Navigate.rawValue)
  add(OpenClawCanvasCommand.Eval.rawValue)
  add(OpenClawCanvasCommand.Snapshot.rawValue)
  add(OpenClawCanvasA2UICommand.Push.rawValue)
  add(OpenClawCanvasA2UICommand.PushJSONL.rawValue)
  add(OpenClawCanvasA2UICommand.Reset.rawValue)
  add(OpenClawScreenCommand.Record.rawValue)
  if (cameraEnabled.value) {
    add(OpenClawCameraCommand.Snap.rawValue)
    add(OpenClawCameraCommand.Clip.rawValue)
  }
  // ... more commands
}
```

### Invoke Command Handling

```kotlin
private suspend fun handleInvoke(command: String, paramsJson: String?): GatewaySession.InvokeResult {
  // Check foreground requirement
  if (command.startsWith(OpenClawCanvasCommand.NamespacePrefix)) {
    if (!isForeground.value) {
      return GatewaySession.InvokeResult.error(
        code = "NODE_BACKGROUND_UNAVAILABLE",
        message = "canvas commands require foreground"
      )
    }
  }
  
  // Check permissions
  if (command.startsWith(OpenClawCameraCommand.NamespacePrefix) && !cameraEnabled.value) {
    return GatewaySession.InvokeResult.error(
      code = "CAMERA_DISABLED",
      message = "enable Camera in Settings"
    )
  }
  
  // Execute command
  return when (command) {
    OpenClawCanvasCommand.Navigate.rawValue -> {
      val url = CanvasController.parseNavigateUrl(paramsJson)
      canvas.navigate(url)
      GatewaySession.InvokeResult.ok(null)
    }
    // ... more commands
  }
}
```

---

## Chat System Architecture

### Message Flow

```
User Input
    ↓
ChatComposer (UI)
    ↓
MainViewModel.sendChat()
    ↓
NodeRuntime.sendChat()
    ↓
ChatController.sendMessage()
    ↓
GatewaySession.sendNodeEvent("agent.request", payload)
    ↓
Gateway (backend)
    ↓
Agent processes
    ↓
Gateway broadcasts chat events
    ↓
GatewaySession.onEvent("chat.*", payloadJson)
    ↓
ChatController.handleGatewayEvent()
    ↓
Update _messages StateFlow
    ↓
ChatMessageViews recompose
```

### Chat Message Types

**User Message**:
```kotlin
ChatMessage(
  id = "msg-123",
  role = "user",
  content = listOf(
    ChatMessageContent(type = "text", text = "What's my goal for today?")
  ),
  timestampMs = 1234567890
)
```

**Assistant Message with Streaming**:
```kotlin
// Initial
ChatMessage(
  id = "msg-124",
  role = "assistant",
  content = listOf(ChatMessageContent(type = "text", text = "")),
  timestampMs = 1234567900
)

// Streaming updates via _streamingAssistantText
// Final
ChatMessage(
  id = "msg-124",
  role = "assistant",
  content = listOf(ChatMessageContent(type = "text", text = "Your goal is...")),
  timestampMs = 1234567900
)
```

**Tool Call**:
```kotlin
ChatPendingToolCall(
  toolCallId = "call-456",
  name = "goal_get_current",
  args = JsonObject(...),
  startedAtMs = 1234567910,
  isError = false
)
```

### Session Management

**Session Key**: Unique identifier for conversation thread
- Format: `main` (default) or custom key
- Persisted in SecurePrefs
- Used for routing and history

**Session Entry**:
```kotlin
ChatSessionEntry(
  key = "main",
  updatedAtMs = 1234567890,
  displayName = "Today's Goals"
)
```

**Session Switching**:
```kotlin
fun switchChatSession(sessionKey: String) {
  chat.switchSession(sessionKey)  // Load new session
  // UI updates via chatMessages StateFlow
}
```

---

## Cron System for Life Assistant

### Scheduling Examples

**Daily Reminder at 9 AM**:
```typescript
{
  kind: "cron",
  expr: "0 9 * * *",
  tz: "America/New_York"
}
```

**Every 6 Hours**:
```typescript
{
  kind: "every",
  everyMs: 6 * 60 * 60 * 1000,
  anchorMs: Date.now()
}
```

**One-time at specific time**:
```typescript
{
  kind: "at",
  atMs: Date.parse("2025-01-15T14:30:00Z")
}
```

### Cron Job Examples for Life Assistant

**Daily Goal Check-in**:
```typescript
{
  id: "daily-goal-checkin",
  name: "Daily Goal Check-in",
  enabled: true,
  schedule: { kind: "cron", expr: "0 9 * * *", tz: "America/New_York" },
  sessionTarget: "main",
  wakeMode: "now",
  payload: {
    kind: "agentTurn",
    message: "What are my goals for today? Let's review them.",
    thinking: "medium",
    deliver: true,
    channel: "last"
  }
}
```

**Weekly Habit Review**:
```typescript
{
  id: "weekly-habit-review",
  name: "Weekly Habit Review",
  enabled: true,
  schedule: { kind: "cron", expr: "0 19 * * 0", tz: "America/New_York" },
  sessionTarget: "isolated",
  wakeMode: "next-heartbeat",
  payload: {
    kind: "agentTurn",
    message: "Analyze my habit tracking data for the past week and provide insights.",
    thinking: "high",
    deliver: false
  },
  isolation: {
    postToMainPrefix: "📊 Weekly Habit Summary: ",
    postToMainMode: "summary",
    postToMainMaxChars: 500
  }
}
```

**Evening Journal Prompt**:
```typescript
{
  id: "evening-journal-prompt",
  name: "Evening Journal Prompt",
  enabled: true,
  schedule: { kind: "cron", expr: "0 21 * * *", tz: "America/New_York" },
  sessionTarget: "main",
  wakeMode: "now",
  payload: {
    kind: "agentTurn",
    message: "It's time for journaling. What was the highlight of your day?",
    thinking: "low",
    deliver: true,
    channel: "last"
  }
}
```

### Cron Service API

```typescript
class CronService {
  // Add new job
  async add(input: CronJobCreate): Promise<CronAddResult>
  
  // Update existing job
  async update(jobId: string, input: CronJobPatch): Promise<CronUpdateResult>
  
  // List all jobs
  async list(): Promise<CronListResult>
  
  // Remove job
  async remove(jobId: string): Promise<CronRemoveResult>
  
  // Manually trigger job
  async run(jobId: string, mode: "due" | "force"): Promise<CronRunResult>
}
```

---

## Memory System for Journaling

### Search API

```typescript
interface MemorySearchManager {
  search(
    query: string,
    opts?: {
      maxResults?: number;
      minScore?: number;
      sessionKey?: string;
    }
  ): Promise<MemorySearchResult[]>
}
```

**Search Result**:
```typescript
type MemorySearchResult = {
  path: string;                    // File path in memory
  startLine: number;               // Line number
  endLine: number;
  score: number;                   // Relevance score (0-1)
  snippet: string;                 // Excerpt
  source: "memory" | "sessions";   // Where it came from
  citation?: string;               // Attribution
}
```

### Journal Entry Storage

**Recommended Structure**:
```
~/.openclaw/workspace/memory/
├── journal/
│   ├── 2025-01-15.md
│   ├── 2025-01-14.md
│   └── ...
├── goals/
│   ├── active.md
│   ├── completed.md
│   └── ...
└── habits/
    ├── tracking.md
    └── ...
```

**Journal Entry Format**:
```markdown
# 2025-01-15

## Highlights
- Completed project milestone
- Had great conversation with friend

## Challenges
- Struggled with focus in afternoon
- Skipped workout

## Reflections
- Need better time management
- Should schedule breaks

## Tomorrow's Focus
- Start new project phase
- Maintain exercise routine
```

### Search Examples

**Find entries about goals**:
```typescript
const results = await memoryManager.search("goals progress", {
  maxResults: 10,
  sessionKey: "main"
});
```

**Find recent journal entries**:
```typescript
const results = await memoryManager.search("journal 2025-01", {
  maxResults: 30
});
```

**Find habit tracking data**:
```typescript
const results = await memoryManager.search("habit streak", {
  maxResults: 20
});
```

---

## Skills System for Life Assistant

### Skill Definition Format

**File**: `jum/skills/goal-tracker/SKILL.md`

```markdown
---
skillKey: goal-tracker
emoji: 🎯
always: false
requires:
  bins:
    - jq
---

# Goal Tracker

Manage personal goals with tracking and analytics.

## Commands

### Create Goal
\`\`\`bash
goal-tracker create --title "Learn Rust" --deadline "2025-06-01" --priority high
\`\`\`

### List Goals
\`\`\`bash
goal-tracker list --status active
\`\`\`

### Update Progress
\`\`\`bash
goal-tracker progress --id goal-123 --percent 50
\`\`\`

### Get Analytics
\`\`\`bash
goal-tracker analytics --period week
\`\`\`
```

### Skill Metadata

```typescript
type OpenClawSkillMetadata = {
  always?: boolean;              // Always load this skill
  skillKey?: string;             // Unique identifier
  primaryEnv?: string;           // Primary environment variable
  emoji?: string;                // Display emoji
  homepage?: string;             // Documentation URL
  os?: string[];                 // Supported OS: ["darwin", "linux", "win32"]
  requires?: {
    bins?: string[];             // Required binaries
    anyBins?: string[];          // At least one of these
    env?: string[];              // Required env vars
    config?: string[];           // Required config keys
  };
  install?: SkillInstallSpec[];   // Installation instructions
};
```

### Skill Installation

```typescript
type SkillInstallSpec = {
  id?: string;
  kind: "brew" | "node" | "go" | "uv" | "download";
  label?: string;
  bins?: string[];
  os?: string[];
  formula?: string;              // For brew
  package?: string;              // For npm/pip
  module?: string;               // For node
  url?: string;                  // For download
  archive?: string;              // Archive format
  extract?: boolean;
  stripComponents?: number;
  targetDir?: string;
};
```

### Skill Command Specs

```typescript
type SkillCommandSpec = {
  name: string;                  // Command name
  skillName: string;             // Skill name
  description: string;           // Help text
  dispatch?: SkillCommandDispatchSpec;
};

type SkillCommandDispatchSpec = {
  kind: "tool";
  toolName: string;              // Tool to invoke
  argMode?: "raw";               // How to forward args
};
```

---

## Channel System Architecture

### Channel Capabilities

```typescript
type ChannelCapabilities = {
  chatTypes: ("direct" | "group" | "channel" | "thread")[];
  nativeCommands?: boolean;
  blockStreaming?: boolean;
  polls?: boolean;
  reactions?: boolean;
  media?: boolean;
};
```

### Channel Dock Configuration

**Telegram**:
```typescript
{
  id: "telegram",
  capabilities: {
    chatTypes: ["direct", "group", "channel", "thread"],
    nativeCommands: true,
    blockStreaming: true,
  },
  outbound: { textChunkLimit: 4000 },
  config: {
    resolveAllowFrom: ({ cfg, accountId }) => [...],
    formatAllowFrom: ({ allowFrom }) => [...],
  },
  groups: {
    resolveRequireMention: resolveTelegramGroupRequireMention,
    resolveToolPolicy: resolveTelegramGroupToolPolicy,
  },
  threading: {
    resolveReplyToMode: ({ cfg }) => "first",
    buildToolContext: ({ context, hasRepliedRef }) => ({...}),
  },
}
```

### Channel Allowlist

**Purpose**: Control who can message the agent

**Format**:
```typescript
// Telegram
allowFrom: ["123456789", "987654321"]  // User IDs

// WhatsApp
allowFrom: ["+1234567890", "+0987654321"]  // Phone numbers

// Discord
allowFrom: ["user-id-1", "user-id-2"]  // User IDs

// Wildcard
allowFrom: ["*"]  // Allow everyone
```

---

## Message Routing & Session Keys

### Session Key Format

```
{agentId}:{channel}:{accountId}:{peerKind}:{peerId}
```

**Examples**:
```
default:telegram:default:dm:null
default:whatsapp:default:group:120363123456789@g.us
default:discord:default:dm:user-id-123
```

### Route Resolution

```typescript
type ResolvedAgentRoute = {
  agentId: string;
  channel: string;
  accountId: string;
  sessionKey: string;
  mainSessionKey: string;
  matchedBy: "binding.peer" | "binding.guild" | "binding.account" | "default";
};
```

**Resolution Priority**:
1. Peer-specific binding (DM/group/channel)
2. Parent peer binding (for threads)
3. Guild/team binding
4. Account binding
5. Channel binding
6. Default agent

---

## Auto-Reply Dispatch Flow

```
Inbound Message
    ↓
Parse channel, sender, content
    ↓
Resolve agent route
    ↓
Finalize message context
    ↓
Check command detection
    ↓
Dispatch to reply handler
    ↓
Create reply dispatcher
    ↓
Get reply from agent
    ↓
Handle tool calls
    ↓
Send reply to channel
    ↓
Update session state
```

### Message Context

```typescript
type MsgContext = {
  Body?: string;
  BodyStripped?: string;
  From?: string;
  To?: string;
  Channel?: string;
  AccountId?: string;
  SessionId?: string;
  CommandAuthorized?: boolean;
  // ... more fields
};

type FinalizedMsgContext = Omit<MsgContext, "CommandAuthorized"> & {
  CommandAuthorized: boolean;
};
```

---

## Implementation Patterns

### Adding a New Manager to NodeRuntime

```kotlin
class GoalManager(
  private val scope: CoroutineScope,
  private val session: GatewaySession,
  private val json: Json,
) {
  private val _goals = MutableStateFlow<List<Goal>>(emptyList())
  val goals: StateFlow<List<Goal>> = _goals.asStateFlow()
  
  fun createGoal(title: String, deadline: Long) {
    scope.launch {
      try {
        val response = session.request("goal.create", buildJsonObject {
          put("title", JsonPrimitive(title))
          put("deadline", JsonPrimitive(deadline))
        }.toString())
        // Parse and update state
      } catch (e: Throwable) {
        // Handle error
      }
    }
  }
  
  fun handleGatewayEvent(event: String, payloadJson: String?) {
    if (event == "goal.updated") {
      // Update local state
    }
  }
}
```

### Adding to NodeRuntime

```kotlin
class NodeRuntime(context: Context) {
  private val goalManager: GoalManager by lazy {
    GoalManager(scope, operatorSession, json)
  }
  
  val goals: StateFlow<List<Goal>> = goalManager.goals
  
  fun createGoal(title: String, deadline: Long) {
    goalManager.createGoal(title, deadline)
  }
}
```

### Exposing in ViewModel

```kotlin
class MainViewModel(app: Application) : AndroidViewModel(app) {
  private val runtime: NodeRuntime = (app as NodeApp).runtime
  
  val goals = runtime.goals
  
  fun createGoal(title: String, deadline: Long) {
    runtime.createGoal(title, deadline)
  }
}
```

