import 'dart:convert';

/// Base sealed class for all agent card types.
sealed class AgentCard {
  String get type;
  Map<String, dynamic> toJson();

  static AgentCard? fromJson(Map<String, dynamic> json) {
    return switch (json['type']) {
      'daily_briefing' => DailyBriefingCard.fromJson(json),
      'goal_check_in' => GoalCheckInCard.fromJson(json),
      'reminder' => ReminderCard.fromJson(json),
      'journal_prompt' => JournalPromptCard.fromJson(json),
      'health_snapshot' => HealthSnapshotCard.fromJson(json),
      'insight' || 'proactive' => InsightCard.fromJson(json),
      _ => null,
    };
  }

  static AgentCard? fromJsonString(String jsonStr) {
    try {
      return fromJson(jsonDecode(jsonStr) as Map<String, dynamic>);
    } catch (_) {
      return null;
    }
  }
}

class WeatherInfo {
  final String temp;
  final String icon;
  final String condition;
  const WeatherInfo({
    required this.temp,
    required this.icon,
    required this.condition,
  });
  factory WeatherInfo.fromJson(Map<String, dynamic> json) => WeatherInfo(
    temp: json['temp'] as String? ?? '',
    icon: json['icon'] as String? ?? '☀️',
    condition: json['condition'] as String? ?? '',
  );
  Map<String, dynamic> toJson() => {
    'temp': temp,
    'icon': icon,
    'condition': condition,
  };
}

class PlanItem {
  final String title;
  final String time;
  final String category;
  final bool done;
  const PlanItem({
    required this.title,
    required this.time,
    required this.category,
    this.done = false,
  });
  factory PlanItem.fromJson(Map<String, dynamic> json) => PlanItem(
    title: json['title'] as String? ?? '',
    time: json['time'] as String? ?? '',
    category: json['category'] as String? ?? '',
    done: json['done'] as bool? ?? false,
  );
  Map<String, dynamic> toJson() => {
    'title': title,
    'time': time,
    'category': category,
    'done': done,
  };
}


// --- Card subclasses ---

class DailyBriefingCard extends AgentCard {
  @override
  String get type => 'daily_briefing';
  final WeatherInfo weather;
  final int goalProgress;
  final String goalSummary;
  final List<PlanItem> planItems;
  final List<String> actions;

  DailyBriefingCard({
    required this.weather,
    required this.goalProgress,
    required this.goalSummary,
    required this.planItems,
    this.actions = const ['Start Day', 'Edit'],
  });

  factory DailyBriefingCard.fromJson(Map<String, dynamic> json) =>
      DailyBriefingCard(
        weather: WeatherInfo.fromJson(
          json['weather'] as Map<String, dynamic>? ?? {},
        ),
        goalProgress: json['goalProgress'] as int? ?? 0,
        goalSummary: json['goalSummary'] as String? ?? '',
        planItems: (json['planItems'] as List<dynamic>?)
                ?.map((e) => PlanItem.fromJson(e as Map<String, dynamic>))
                .toList() ??
            [],
        actions: (json['actions'] as List<dynamic>?)
                ?.map((e) => e as String)
                .toList() ??
            const ['Start Day', 'Edit'],
      );

  @override
  Map<String, dynamic> toJson() => {
    'type': type,
    'weather': weather.toJson(),
    'goalProgress': goalProgress,
    'goalSummary': goalSummary,
    'planItems': planItems.map((e) => e.toJson()).toList(),
    'actions': actions,
  };
}

class GoalCheckInCard extends AgentCard {
  @override
  String get type => 'goal_check_in';
  final String goalTitle;
  final String categoryIcon;
  final int streakDays;
  final String streakText;
  final String progressLabel;
  final double progressCurrent;
  final double progressTarget;
  final String progressUnit;
  final List<String> actions;

  GoalCheckInCard({
    required this.goalTitle,
    this.categoryIcon = '🏃',
    this.streakDays = 0,
    this.streakText = '',
    required this.progressLabel,
    required this.progressCurrent,
    required this.progressTarget,
    required this.progressUnit,
    this.actions = const ['Log Progress', 'More'],
  });

  factory GoalCheckInCard.fromJson(Map<String, dynamic> json) =>
      GoalCheckInCard(
        goalTitle: json['goalTitle'] as String? ?? '',
        categoryIcon: json['categoryIcon'] as String? ?? '🏃',
        streakDays: json['streakDays'] as int? ?? 0,
        streakText: json['streakText'] as String? ?? '',
        progressLabel: json['progressLabel'] as String? ?? '',
        progressCurrent: (json['progressCurrent'] as num?)?.toDouble() ?? 0,
        progressTarget: (json['progressTarget'] as num?)?.toDouble() ?? 0,
        progressUnit: json['progressUnit'] as String? ?? '',
        actions: (json['actions'] as List<dynamic>?)
                ?.map((e) => e as String)
                .toList() ??
            const ['Log Progress', 'More'],
      );

  @override
  Map<String, dynamic> toJson() => {
    'type': type,
    'goalTitle': goalTitle,
    'categoryIcon': categoryIcon,
    'streakDays': streakDays,
    'streakText': streakText,
    'progressLabel': progressLabel,
    'progressCurrent': progressCurrent,
    'progressTarget': progressTarget,
    'progressUnit': progressUnit,
    'actions': actions,
  };
}

class ReminderCard extends AgentCard {
  @override
  String get type => 'reminder';
  final String title;
  final String time;
  final String? linkedGoal;
  final List<String> actions;

  ReminderCard({
    required this.title,
    required this.time,
    this.linkedGoal,
    this.actions = const ['Done', 'Snooze 30m', 'Snooze 1h', 'Skip'],
  });

  factory ReminderCard.fromJson(Map<String, dynamic> json) => ReminderCard(
    title: json['title'] as String? ?? '',
    time: json['time'] as String? ?? '',
    linkedGoal: json['linkedGoal'] as String?,
    actions: (json['actions'] as List<dynamic>?)
            ?.map((e) => e as String)
            .toList() ??
        const ['Done', 'Snooze 30m', 'Snooze 1h', 'Skip'],
  );

  @override
  Map<String, dynamic> toJson() => {
    'type': type,
    'title': title,
    'time': time,
    'linkedGoal': linkedGoal,
    'actions': actions,
  };
}

class JournalPromptCard extends AgentCard {
  @override
  String get type => 'journal_prompt';
  final String promptText;
  final List<String> daySummary;

  JournalPromptCard({
    required this.promptText,
    this.daySummary = const [],
  });

  factory JournalPromptCard.fromJson(Map<String, dynamic> json) =>
      JournalPromptCard(
        promptText: json['promptText'] as String? ?? '',
        daySummary: (json['daySummary'] as List<dynamic>?)
                ?.map((e) => e as String)
                .toList() ??
            const [],
      );

  @override
  Map<String, dynamic> toJson() => {
    'type': type,
    'promptText': promptText,
    'daySummary': daySummary,
  };
}

class HealthSnapshotCard extends AgentCard {
  @override
  String get type => 'health_snapshot';
  final int steps;
  final String sleep;
  final int? heartRate;
  final Map<String, String> trends;
  final String? aiNote;

  HealthSnapshotCard({
    this.steps = 0,
    this.sleep = '',
    this.heartRate,
    this.trends = const {},
    this.aiNote,
  });

  factory HealthSnapshotCard.fromJson(Map<String, dynamic> json) =>
      HealthSnapshotCard(
        steps: json['steps'] as int? ?? 0,
        sleep: json['sleep'] as String? ?? '',
        heartRate: json['heartRate'] as int?,
        trends: (json['trends'] as Map<String, dynamic>?)?.map(
              (k, v) => MapEntry(k, v.toString()),
            ) ??
            const {},
        aiNote: json['aiNote'] as String?,
      );

  @override
  Map<String, dynamic> toJson() => {
    'type': type,
    'steps': steps,
    'sleep': sleep,
    'heartRate': heartRate,
    'trends': trends,
    'aiNote': aiNote,
  };
}


/// Proactive insight card — generated by the backend's proactive engine.
/// Borrowed from OpenClaw's proactive analysis: detects at-risk goals,
/// task overload, missing reminders, and generates AI-powered suggestions.
class InsightCard extends AgentCard {
  @override
  String get type => 'insight';
  final String title;
  final String content;
  final String priority;
  final String? suggestedAction;
  final String? relatedGoalId;

  InsightCard({
    required this.title,
    required this.content,
    this.priority = 'medium',
    this.suggestedAction,
    this.relatedGoalId,
  });

  factory InsightCard.fromJson(Map<String, dynamic> json) => InsightCard(
        title: json['title'] as String? ?? '',
        content: json['content'] as String? ?? '',
        priority: json['priority'] as String? ?? 'medium',
        suggestedAction: json['suggestedAction'] as String?,
        relatedGoalId: json['relatedGoalId'] as String?,
      );

  @override
  Map<String, dynamic> toJson() => {
        'type': type,
        'title': title,
        'content': content,
        'priority': priority,
        'suggestedAction': suggestedAction,
        'relatedGoalId': relatedGoalId,
      };
}
