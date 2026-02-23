class Skill {
  final String id;
  final String userId;
  final String name;
  final String type;
  final String description;
  final String status;
  final String category;
  final DateTime? createdAt;

  const Skill({
    required this.id,
    required this.userId,
    required this.name,
    required this.type,
    this.description = '',
    this.status = 'disconnected',
    this.category = 'mcp',
    this.createdAt,
  });

  factory Skill.fromJson(Map<String, dynamic> json) => Skill(
        id: json['id'] as String,
        userId: json['userId'] as String? ?? '',
        name: json['name'] as String,
        type: json['type'] as String,
        description: json['description'] as String? ?? '',
        status: json['status'] as String? ?? 'disconnected',
        category: json['category'] as String? ?? 'mcp',
        createdAt: json['createdAt'] != null
            ? DateTime.tryParse(json['createdAt'] as String)
            : null,
      );

  bool get isConnected => status == 'connected' || status == 'active';
  bool get isMcp => category == 'mcp';
  bool get isAgent => category == 'agent';
}
