class Reminder {
  final String id;
  final String userId;
  final String title;
  final String time;
  final bool active;
  final String? goalId;
  final int snoozeCount;
  final String? snoozedUntil;
  final String? originalTime;
  final DateTime? createdAt;

  const Reminder({
    required this.id,
    required this.userId,
    required this.title,
    required this.time,
    this.active = true,
    this.goalId,
    this.snoozeCount = 0,
    this.snoozedUntil,
    this.originalTime,
    this.createdAt,
  });

  factory Reminder.fromJson(Map<String, dynamic> json) => Reminder(
        id: json['id'] as String,
        userId: json['userId'] as String? ?? '',
        title: json['title'] as String,
        time: json['time'] as String,
        active: json['active'] as bool? ?? true,
        goalId: json['goalId'] as String?,
        snoozeCount: json['snoozeCount'] as int? ?? 0,
        snoozedUntil: json['snoozedUntil'] as String?,
        originalTime: json['originalTime'] as String?,
        createdAt: json['createdAt'] != null
            ? DateTime.tryParse(json['createdAt'] as String)
            : null,
      );

  bool get isSnoozed => snoozeCount > 0;
  bool get isFrequentlySnoozed => snoozeCount >= 3;
}
