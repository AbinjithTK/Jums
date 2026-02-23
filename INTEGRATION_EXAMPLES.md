# Integration Examples for Life Assistant

## Example 1: Adding Goal Management Feature

### Step 1: Create Goal Data Models

**File**: `app/src/main/java/ai/openclaw/android/models/Goal.kt`

```kotlin
package ai.openclaw.android.models

import kotlinx.serialization.Serializable

@Serializable
data class Goal(
  val id: String,
  val title: String,
  val description: String? = null,
  val deadline: Long? = null,
  val priority: String = "medium",  // low, medium, high
  val status: String = "active",    // active, completed, archived
  val progress: Int = 0,            // 0-100
  val createdAtMs: Long,
  val updatedAtMs: Long,
)

@Serializable
data class GoalUpdate(
  val title: String? = null,
  val description: String? = null,
  val deadline: Long? = null,
  val priority: String? = null,
  val status: String? = null,
  val progress: Int? = null,
)
```

### Step 2: Create Goal Manager

**File**: `app/src/main/java/ai/openclaw/android/node/GoalManager.kt`

```kotlin
package ai.openclaw.android.node

import ai.openclaw.android.gateway.GatewaySession
import ai.openclaw.android.models.Goal
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch
import kotlinx.serialization.json.Json
import kotlinx.serialization.json.JsonPrimitive
import kotlinx.serialization.json.buildJsonObject

class GoalManager(
  private val scope: CoroutineScope,
  private val session: GatewaySession,
  private val json: Json,
) {
  private val _goals = MutableStateFlow<List<Goal>>(emptyList())
  val goals: StateFlow<List<Goal>> = _goals.asStateFlow()

  private val _loading = MutableStateFlow(false)
  val loading: StateFlow<Boolean> = _loading.asStateFlow()

  private val _error = MutableStateFlow<String?>(null)
  val error: StateFlow<String?> = _error.asStateFlow()

  fun loadGoals() {
    scope.launch {
      _loading.value = true
      _error.value = null
      try {
        val response = session.request("goal.list", "{}")
        val payload = json.parseToJsonElement(response).asObjectOrNull()
        val goalsArray = payload?.get("goals")?.asArrayOrNull()
        
        val goalsList = goalsArray?.mapNotNull { element ->
          try {
            json.decodeFromJsonElement<Goal>(element)
          } catch (e: Throwable) {
            null
          }
        } ?: emptyList()
        
        _goals.value = goalsList
      } catch (e: Throwable) {
        _error.value = e.message ?: "Failed to load goals"
      } finally {
        _loading.value = false
      }
    }
  }

  fun createGoal(title: String, description: String? = null, deadline: Long? = null) {
    scope.launch {
      _loading.value = true
      _error.value = null
      try {
        val params = buildJsonObject {
          put("title", JsonPrimitive(title))
          if (description != null) put("description", JsonPrimitive(description))
          if (deadline != null) put("deadline", JsonPrimitive(deadline))
          put("priority", JsonPrimitive("medium"))
        }
        
        val response = session.request("goal.create", params.toString())
        val goal = json.decodeFromJsonElement<Goal>(
          json.parseToJsonElement(response)
        )
        
        _goals.value = _goals.value + goal
      } catch (e: Throwable) {
        _error.value = e.message ?: "Failed to create goal"
      } finally {
        _loading.value = false
      }
    }
  }

  fun updateGoal(goalId: String, update: Map<String, Any>) {
    scope.launch {
      _loading.value = true
      _error.value = null
      try {
        val params = buildJsonObject {
          put("id", JsonPrimitive(goalId))
          update.forEach { (key, value) ->
            when (value) {
              is String -> put(key, JsonPrimitive(value))
              is Int -> put(key, JsonPrimitive(value))
              is Long -> put(key, JsonPrimitive(value))
              is Boolean -> put(key, JsonPrimitive(value))
            }
          }
        }
        
        val response = session.request("goal.update", params.toString())
        val updatedGoal = json.decodeFromJsonElement<Goal>(
          json.parseToJsonElement(response)
        )
        
        _goals.value = _goals.value.map { if (it.id == goalId) updatedGoal else it }
      } catch (e: Throwable) {
        _error.value = e.message ?: "Failed to update goal"
      } finally {
        _loading.value = false
      }
    }
  }

  fun deleteGoal(goalId: String) {
    scope.launch {
      _loading.value = true
      _error.value = null
      try {
        session.request("goal.delete", """{"id":"$goalId"}""")
        _goals.value = _goals.value.filter { it.id != goalId }
      } catch (e: Throwable) {
        _error.value = e.message ?: "Failed to delete goal"
      } finally {
        _loading.value = false
      }
    }
  }

  fun handleGatewayEvent(event: String, payloadJson: String?) {
    if (event == "goal.created" || event == "goal.updated") {
      loadGoals()
    } else if (event == "goal.deleted") {
      loadGoals()
    }
  }
}
```

### Step 3: Integrate into NodeRuntime

**File**: `app/src/main/java/ai/openclaw/android/NodeRuntime.kt`

```kotlin
class NodeRuntime(context: Context) {
  // ... existing code ...
  
  private val goalManager: GoalManager by lazy {
    GoalManager(
      scope = scope,
      session = operatorSession,
      json = json,
    )
  }

  val goals: StateFlow<List<Goal>> = goalManager.goals
  val goalsLoading: StateFlow<Boolean> = goalManager.loading
  val goalsError: StateFlow<String?> = goalManager.error

  init {
    // ... existing init code ...
    
    scope.launch {
      isConnected.collect { connected ->
        if (connected) {
          goalManager.loadGoals()
        }
      }
    }
  }

  fun createGoal(title: String, description: String? = null, deadline: Long? = null) {
    goalManager.createGoal(title, description, deadline)
  }

  fun updateGoal(goalId: String, update: Map<String, Any>) {
    goalManager.updateGoal(goalId, update)
  }

  fun deleteGoal(goalId: String) {
    goalManager.deleteGoal(goalId)
  }

  private fun handleGatewayEvent(event: String, payloadJson: String?) {
    // ... existing event handling ...
    goalManager.handleGatewayEvent(event, payloadJson)
  }
}
```

### Step 4: Expose in ViewModel

**File**: `app/src/main/java/ai/openclaw/android/MainViewModel.kt`

```kotlin
class MainViewModel(app: Application) : AndroidViewModel(app) {
  private val runtime: NodeRuntime = (app as NodeApp).runtime

  // ... existing state flows ...
  
  val goals = runtime.goals
  val goalsLoading = runtime.goalsLoading
  val goalsError = runtime.goalsError

  // ... existing methods ...
  
  fun createGoal(title: String, description: String? = null, deadline: Long? = null) {
    runtime.createGoal(title, description, deadline)
  }

  fun updateGoal(goalId: String, update: Map<String, Any>) {
    runtime.updateGoal(goalId, update)
  }

  fun deleteGoal(goalId: String) {
    runtime.deleteGoal(goalId)
  }
}
```

### Step 5: Create UI Screen

**File**: `app/src/main/java/ai/openclaw/android/ui/GoalsScreen.kt`

```kotlin
package ai.openclaw.android.ui

import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Add
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import ai.openclaw.android.MainViewModel
import ai.openclaw.android.models.Goal
import java.text.SimpleDateFormat
import java.util.*

@Composable
fun GoalsScreen(viewModel: MainViewModel) {
  val goals by viewModel.goals.collectAsState()
  val loading by viewModel.goalsLoading.collectAsState()
  val error by viewModel.goalsError.collectAsState()
  
  var showCreateDialog by remember { mutableStateOf(false) }

  Column(modifier = Modifier.fillMaxSize()) {
    TopAppBar(
      title = { Text("Goals") },
      actions = {
        IconButton(onClick = { showCreateDialog = true }) {
          Icon(Icons.Default.Add, contentDescription = "Add Goal")
        }
      }
    )

    if (error != null) {
      Text(
        text = error ?: "Unknown error",
        color = MaterialTheme.colorScheme.error,
        modifier = Modifier.padding(16.dp)
      )
    }

    if (loading) {
      CircularProgressIndicator(modifier = Modifier.padding(16.dp))
    } else {
      LazyColumn(modifier = Modifier.fillMaxSize()) {
        items(goals) { goal ->
          GoalCard(goal = goal, onUpdate = { update ->
            viewModel.updateGoal(goal.id, update)
          })
        }
      }
    }
  }

  if (showCreateDialog) {
    CreateGoalDialog(
      onDismiss = { showCreateDialog = false },
      onCreate = { title, description, deadline ->
        viewModel.createGoal(title, description, deadline)
        showCreateDialog = false
      }
    )
  }
}

@Composable
fun GoalCard(goal: Goal, onUpdate: (Map<String, Any>) -> Unit) {
  Card(
    modifier = Modifier
      .fillMaxWidth()
      .padding(8.dp)
  ) {
    Column(modifier = Modifier.padding(16.dp)) {
      Text(text = goal.title, style = MaterialTheme.typography.titleMedium)
      
      if (goal.description != null) {
        Text(text = goal.description, style = MaterialTheme.typography.bodySmall)
      }

      LinearProgressIndicator(
        progress = goal.progress / 100f,
        modifier = Modifier
          .fillMaxWidth()
          .padding(top = 8.dp)
      )

      Row(
        modifier = Modifier
          .fillMaxWidth()
          .padding(top = 8.dp),
        horizontalArrangement = Arrangement.SpaceBetween
      ) {
        Text(text = "${goal.progress}%", style = MaterialTheme.typography.labelSmall)
        
        if (goal.deadline != null) {
          val dateFormat = SimpleDateFormat("MMM dd, yyyy", Locale.getDefault())
          Text(
            text = dateFormat.format(Date(goal.deadline)),
            style = MaterialTheme.typography.labelSmall
          )
        }
      }

      Row(
        modifier = Modifier
          .fillMaxWidth()
          .padding(top = 8.dp),
        horizontalArrangement = Arrangement.End
      ) {
        Button(
          onClick = { onUpdate(mapOf("progress" to (goal.progress + 10).coerceAtMost(100))) },
          modifier = Modifier.padding(end = 8.dp)
        ) {
          Text("Progress")
        }

        Button(
          onClick = { onUpdate(mapOf("status" to "completed")) }
        ) {
          Text("Complete")
        }
      }
    }
  }
}

@Composable
fun CreateGoalDialog(
  onDismiss: () -> Unit,
  onCreate: (String, String?, Long?) -> Unit
) {
  var title by remember { mutableStateOf("") }
  var description by remember { mutableStateOf("") }

  AlertDialog(
    onDismissRequest = onDismiss,
    title = { Text("Create Goal") },
    text = {
      Column {
        TextField(
          value = title,
          onValueChange = { title = it },
          label = { Text("Title") },
          modifier = Modifier.fillMaxWidth()
        )
        TextField(
          value = description,
          onValueChange = { description = it },
          label = { Text("Description (optional)") },
          modifier = Modifier
            .fillMaxWidth()
            .padding(top = 8.dp)
        )
      }
    },
    confirmButton = {
      Button(
        onClick = {
          if (title.isNotBlank()) {
            onCreate(title, description.ifBlank { null }, null)
          }
        }
      ) {
        Text("Create")
      }
    },
    dismissButton = {
      Button(onClick = onDismiss) {
        Text("Cancel")
      }
    }
  )
}
```

---

## Example 2: Creating a Cron Job for Daily Reminders

### Backend Skill: `jum/skills/goal-tracker/SKILL.md`

```markdown
---
skillKey: goal-tracker
emoji: 🎯
always: false
requires:
  bins:
    - jq
---

# Goal Tracker Skill

Manage personal goals with tracking and analytics.

## Tools

### goal_get_active
Get all active goals.

\`\`\`bash
goal-tracker list --status active --format json
\`\`\`

### goal_create
Create a new goal.

\`\`\`bash
goal-tracker create --title "$TITLE" --deadline "$DEADLINE" --priority "$PRIORITY"
\`\`\`

### goal_update_progress
Update goal progress.

\`\`\`bash
goal-tracker progress --id "$GOAL_ID" --percent "$PERCENT"
\`\`\`
```

### Cron Job Configuration

**File**: `~/.openclaw/cron-jobs.json`

```json
{
  "version": 1,
  "jobs": [
    {
      "id": "daily-goal-checkin",
      "name": "Daily Goal Check-in",
      "enabled": true,
      "createdAtMs": 1705276800000,
      "updatedAtMs": 1705276800000,
      "schedule": {
        "kind": "cron",
        "expr": "0 9 * * *",
        "tz": "America/New_York"
      },
      "sessionTarget": "main",
      "wakeMode": "now",
      "payload": {
        "kind": "agentTurn",
        "message": "Good morning! Let's review your goals for today. What are your top 3 priorities?",
        "thinking": "medium",
        "deliver": true,
        "channel": "last"
      },
      "state": {
        "nextRunAtMs": 1705320000000
      }
    },
    {
      "id": "weekly-goal-review",
      "name": "Weekly Goal Review",
      "enabled": true,
      "createdAtMs": 1705276800000,
      "updatedAtMs": 1705276800000,
      "schedule": {
        "kind": "cron",
        "expr": "0 19 * * 0",
        "tz": "America/New_York"
      },
      "sessionTarget": "isolated",
      "wakeMode": "next-heartbeat",
      "payload": {
        "kind": "agentTurn",
        "message": "Analyze my goal progress this week. Which goals am I on track for? Which need attention?",
        "thinking": "high",
        "deliver": false
      },
      "isolation": {
        "postToMainPrefix": "📊 Weekly Goal Summary: ",
        "postToMainMode": "summary",
        "postToMainMaxChars": 500
      },
      "state": {
        "nextRunAtMs": 1705924800000
      }
    }
  ]
}
```

---

## Example 3: Journaling with Memory System

### Journal Entry Storage

**File**: `~/.openclaw/workspace/memory/journal/2025-01-15.md`

```markdown
# Journal Entry - January 15, 2025

## Morning Reflection
Started the day with clarity on my goals. Feeling motivated.

## Highlights
- Completed the project milestone ahead of schedule
- Had a productive meeting with the team
- Finished reading the first chapter of the new book

## Challenges
- Struggled with focus in the afternoon
- Skipped my workout due to time constraints
- Felt overwhelmed by email backlog

## Learnings
- Breaking tasks into smaller chunks helps maintain focus
- Need to schedule exercise as a non-negotiable appointment
- Email management needs a better system

## Tomorrow's Focus
- Start the next project phase
- Maintain exercise routine
- Implement email batching strategy

## Gratitude
- Grateful for supportive team members
- Thankful for the opportunity to work on meaningful projects
- Appreciative of good health
```

### Memory Search for Journaling

```kotlin
// In GoalManager or new JournalManager
fun searchJournalEntries(query: String) {
  scope.launch {
    try {
      val results = memoryManager.search(query, maxResults = 20)
      
      val journalEntries = results.filter { result ->
        result.path.contains("journal/")
      }
      
      // Display results to user
      journalEntries.forEach { entry ->
        println("${entry.path}: ${entry.snippet}")
      }
    } catch (e: Throwable) {
      // Handle error
    }
  }
}
```

---

## Example 4: Habit Tracking with Cron

### Habit Data Model

```kotlin
@Serializable
data class Habit(
  val id: String,
  val name: String,
  val description: String? = null,
  val frequency: String,  // daily, weekly, monthly
  val target: Int = 1,    // times per period
  val streak: Int = 0,
  val lastCompletedAtMs: Long? = null,
  val createdAtMs: Long,
)

@Serializable
data class HabitCompletion(
  val habitId: String,
  val completedAtMs: Long,
  val note: String? = null,
)
```

### Cron Job for Habit Tracking

```json
{
  "id": "daily-habit-check",
  "name": "Daily Habit Check",
  "enabled": true,
  "schedule": {
    "kind": "cron",
    "expr": "0 20 * * *",
    "tz": "America/New_York"
  },
  "sessionTarget": "main",
  "wakeMode": "now",
  "payload": {
    "kind": "agentTurn",
    "message": "Time for your daily habit check! Which habits did you complete today?",
    "thinking": "low",
    "deliver": true,
    "channel": "last"
  }
}
```

---

## Example 5: Proactive Cards with A2UI

### Canvas A2UI Action for Goal Suggestion

```kotlin
// In GoalManager or new ProactiveCardsManager
fun suggestGoalCard() {
  scope.launch {
    try {
      val goals = _goals.value.filter { it.status == "active" }
      
      if (goals.isEmpty()) return@launch
      
      // Find goal with lowest progress
      val lowestProgressGoal = goals.minByOrNull { it.progress }
      
      if (lowestProgressGoal != null) {
        val message = OpenClawCanvasA2UIAction.formatAgentMessage(
          actionName = "suggest_goal_action",
          sessionKey = "main",
          surfaceId = "main",
          sourceComponentId = "goal-card",
          host = "Life Assistant",
          instanceId = "android",
          contextJson = """
            {
              "goalId": "${lowestProgressGoal.id}",
              "goalTitle": "${lowestProgressGoal.title}",
              "currentProgress": ${lowestProgressGoal.progress},
              "suggestion": "This goal needs attention. Would you like to work on it now?"
            }
          """.trimIndent()
        )
        
        nodeSession.sendNodeEvent(
          event = "agent.request",
          payloadJson = buildJsonObject {
            put("message", JsonPrimitive(message))
            put("sessionKey", JsonPrimitive("main"))
            put("thinking", JsonPrimitive("low"))
            put("deliver", JsonPrimitive(false))
          }.toString()
        )
      }
    } catch (e: Throwable) {
      // Handle error
    }
  }
}
```

---

## Example 6: Unified Inbox Screen

```kotlin
@Composable
fun UnifiedInboxScreen(viewModel: MainViewModel) {
  val chatMessages by viewModel.chatMessages.collectAsState()
  val goals by viewModel.goals.collectAsState()
  val reminders by viewModel.reminders.collectAsState()
  val habits by viewModel.habits.collectAsState()

  LazyColumn(modifier = Modifier.fillMaxSize()) {
    // Recent messages
    item {
      Text("Recent Messages", style = MaterialTheme.typography.titleMedium)
    }
    items(chatMessages.takeLast(3)) { message ->
      ChatMessageCard(message)
    }

    // Active goals
    item {
      Text("Active Goals", style = MaterialTheme.typography.titleMedium)
    }
    items(goals.filter { it.status == "active" }.take(3)) { goal ->
      GoalCard(goal) { update ->
        viewModel.updateGoal(goal.id, update)
      }
    }

    // Upcoming reminders
    item {
      Text("Upcoming Reminders", style = MaterialTheme.typography.titleMedium)
    }
    items(reminders.filter { it.dueAtMs > System.currentTimeMillis() }.take(3)) { reminder ->
      ReminderCard(reminder)
    }

    // Habit streaks
    item {
      Text("Habit Streaks", style = MaterialTheme.typography.titleMedium)
    }
    items(habits.take(3)) { habit ->
      HabitStreakCard(habit)
    }
  }
}
```

---

## Example 7: Voice Command for Goal Creation

```kotlin
// In VoiceWakeManager or custom voice handler
fun handleVoiceCommand(command: String) {
  scope.launch {
    when {
      command.contains("create goal", ignoreCase = true) -> {
        // Extract goal title from command
        val title = extractGoalTitle(command)
        if (title.isNotEmpty()) {
          nodeSession.sendNodeEvent(
            event = "agent.request",
            payloadJson = buildJsonObject {
              put("message", JsonPrimitive("Create a goal: $title"))
              put("sessionKey", JsonPrimitive("main"))
              put("thinking", JsonPrimitive("low"))
              put("deliver", JsonPrimitive(false))
            }.toString()
          )
        }
      }
      command.contains("what are my goals", ignoreCase = true) -> {
        nodeSession.sendNodeEvent(
          event = "agent.request",
          payloadJson = buildJsonObject {
            put("message", JsonPrimitive("What are my active goals?"))
            put("sessionKey", JsonPrimitive("main"))
            put("thinking", JsonPrimitive("low"))
            put("deliver", JsonPrimitive(false))
          }.toString()
        )
      }
    }
  }
}

private fun extractGoalTitle(command: String): String {
  // Simple extraction: "create goal: Learn Rust" -> "Learn Rust"
  val parts = command.split(":", limit = 2)
  return if (parts.size > 1) parts[1].trim() else ""
}
```

