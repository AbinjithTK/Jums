class CronJob {
  final String id;
  final String userId;
  final String name;
  final String description;
  final bool enabled;
  final String scheduleType;
  final String scheduleValue;
  final String actionMessage;
  final String? nextRunAt;
  final String? lastRunAt;
  final int runCount;
  final String? lastStatus;
  final DateTime? createdAt;

  const CronJob({
    required this.id,
    this.userId = '',
    required this.name,
    this.description = '',
    this.enabled = true,
    required this.scheduleType,
    required this.scheduleValue,
    required this.actionMessage,
    this.nextRunAt,
    this.lastRunAt,
    this.runCount = 0,
    this.lastStatus,
    this.createdAt,
  });

  factory CronJob.fromJson(Map<String, dynamic> json) => CronJob(
        id: json['id'] as String,
        userId: json['userId'] as String? ?? '',
        name: json['name'] as String? ?? '',
        description: json['description'] as String? ?? '',
        enabled: json['enabled'] as bool? ?? true,
        scheduleType: json['scheduleType'] as String? ?? 'daily',
        scheduleValue: json['scheduleValue'] as String? ?? '',
        actionMessage: json['actionMessage'] as String? ?? '',
        nextRunAt: json['nextRunAt'] as String?,
        lastRunAt: json['lastRunAt'] as String?,
        runCount: json['runCount'] as int? ?? 0,
        lastStatus: json['lastStatus'] as String?,
        createdAt: json['createdAt'] != null
            ? DateTime.tryParse(json['createdAt'] as String)
            : null,
      );

  String get scheduleDisplay {
    switch (scheduleType) {
      case 'daily':
        return 'Daily at $scheduleValue';
      case 'weekly':
        return 'Weekly: $scheduleValue';
      case 'interval':
        return 'Every ${scheduleValue}min';
      case 'once':
        return 'Once: $scheduleValue';
      case 'cron':
        return 'Cron: $scheduleValue';
      default:
        return scheduleValue;
    }
  }
}
