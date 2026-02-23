class Task {
  final String id;
  final String userId;
  final String title;
  final String time;
  final String detail;
  final String type;
  final bool completed;
  final bool active;
  final String? goalId;
  final String priority;
  final bool requiresProof;
  final String? dueDate;
  final String? proofUrl;
  final String? proofType;
  final String proofStatus;
  final DateTime? completedAt;
  final DateTime? createdAt;

  const Task({
    required this.id,
    required this.userId,
    required this.title,
    this.time = '',
    this.detail = '',
    this.type = 'task',
    this.completed = false,
    this.active = false,
    this.goalId,
    this.priority = 'medium',
    this.requiresProof = false,
    this.dueDate,
    this.proofUrl,
    this.proofType,
    this.proofStatus = 'pending',
    this.completedAt,
    this.createdAt,
  });

  factory Task.fromJson(Map<String, dynamic> json) => Task(
        id: json['id'] as String,
        userId: json['userId'] as String? ?? '',
        title: json['title'] as String,
        time: json['time'] as String? ?? '',
        detail: json['detail'] as String? ?? '',
        type: json['type'] as String? ?? 'task',
        completed: json['completed'] as bool? ?? false,
        active: json['active'] as bool? ?? false,
        goalId: json['goalId'] as String?,
        priority: json['priority'] as String? ?? 'medium',
        requiresProof: json['requiresProof'] as bool? ?? false,
        dueDate: json['dueDate'] as String?,
        proofUrl: json['proofUrl'] as String?,
        proofType: json['proofType'] as String?,
        proofStatus: json['proofStatus'] as String? ?? 'pending',
        completedAt: json['completedAt'] != null
            ? DateTime.tryParse(json['completedAt'] as String)
            : null,
        createdAt: json['createdAt'] != null
            ? DateTime.tryParse(json['createdAt'] as String)
            : null,
      );
}
