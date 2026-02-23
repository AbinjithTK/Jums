class Goal {
  final String id;
  final String userId;
  final String title;
  final String category;
  final int progress;
  final int total;
  final String unit;
  final String insight;
  final String activeAgent;
  final bool completed;
  final String? priority;
  final int streakDays;
  final DateTime? createdAt;

  const Goal({
    required this.id,
    required this.userId,
    required this.title,
    required this.category,
    this.progress = 0,
    this.total = 100,
    this.unit = '',
    this.insight = '',
    this.activeAgent = '',
    this.completed = false,
    this.priority,
    this.streakDays = 0,
    this.createdAt,
  });

  factory Goal.fromJson(Map<String, dynamic> json) => Goal(
        id: json['id'] as String,
        userId: json['userId'] as String? ?? '',
        title: json['title'] as String,
        category: json['category'] as String,
        progress: json['progress'] as int? ?? 0,
        total: json['total'] as int? ?? 100,
        unit: json['unit'] as String? ?? '',
        insight: json['insight'] as String? ?? '',
        activeAgent: json['activeAgent'] as String? ?? '',
        completed: json['completed'] as bool? ?? false,
        priority: json['priority'] as String?,
        streakDays: json['streakDays'] as int? ?? 0,
        createdAt: json['createdAt'] != null
            ? DateTime.tryParse(json['createdAt'] as String)
            : null,
      );

  double get progressFraction =>
      total > 0 ? (progress / total).clamp(0.0, 1.0) : 0.0;

  String get progressText => '$progress/$total $unit'.trim();

  String get categoryEmoji => switch (category.toLowerCase()) {
        'health' || 'fitness' => '🏃',
        'learning' || 'education' => '📚',
        'finance' || 'money' => '💰',
        'mindfulness' || 'meditation' => '🧘',
        'work' || 'career' => '💼',
        _ => '🎯',
      };
}
