/// Proactive insight from the backend engine — mirrors ProactiveInsight schema.
/// Borrowed from OpenClaw's proactive analysis pattern: the backend gathers
/// context (goals, tasks, reminders), detects patterns (at-risk, stale, overload),
/// and generates actionable insight cards.
class ProactiveInsight {
  final String id;
  final String userId;
  final String type;
  final String title;
  final String content;
  final String priority;
  final String? cardType;
  final Map<String, dynamic>? cardData;
  final String? actionTaken;
  final bool read;
  final bool dismissed;
  final DateTime? createdAt;

  const ProactiveInsight({
    required this.id,
    required this.userId,
    required this.type,
    required this.title,
    required this.content,
    this.priority = 'medium',
    this.cardType,
    this.cardData,
    this.actionTaken,
    this.read = false,
    this.dismissed = false,
    this.createdAt,
  });

  factory ProactiveInsight.fromJson(Map<String, dynamic> json) =>
      ProactiveInsight(
        id: json['id'] as String,
        userId: json['userId'] as String? ?? '',
        type: json['type'] as String? ?? 'insight',
        title: json['title'] as String? ?? '',
        content: json['content'] as String? ?? '',
        priority: json['priority'] as String? ?? 'medium',
        cardType: json['cardType'] as String?,
        cardData: json['cardData'] as Map<String, dynamic>?,
        actionTaken: json['actionTaken'] as String?,
        read: json['read'] as bool? ?? false,
        dismissed: json['dismissed'] as bool? ?? false,
        createdAt: json['createdAt'] != null
            ? DateTime.tryParse(json['createdAt'] as String)
            : null,
      );

  bool get isHigh => priority == 'high' || priority == 'critical';

  String get priorityEmoji => switch (priority) {
        'high' || 'critical' => '🔴',
        'medium' => '🟡',
        _ => '🟢',
      };
}
