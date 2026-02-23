class Message {
  final String id;
  final String userId;
  final String role;
  final String type;
  final String? content;
  final String? cardType;
  final Map<String, dynamic>? cardData;
  final String timestamp;
  final DateTime? createdAt;
  final String? imageUrl; // Local file path or network URL

  const Message({
    required this.id,
    required this.userId,
    required this.role,
    required this.type,
    this.content,
    this.cardType,
    this.cardData,
    required this.timestamp,
    this.createdAt,
    this.imageUrl,
  });

  factory Message.fromJson(Map<String, dynamic> json) => Message(
        id: json['id'] as String,
        userId: json['userId'] as String? ?? '',
        role: json['role'] as String,
        type: json['type'] as String,
        content: json['content'] as String?,
        cardType: json['cardType'] as String?,
        cardData: json['cardData'] as Map<String, dynamic>?,
        timestamp: json['timestamp'] as String? ?? '',
        createdAt: json['createdAt'] != null
            ? DateTime.tryParse(json['createdAt'] as String)
            : null,
        imageUrl: json['imageUrl'] as String?,
      );

  bool get isUser => role == 'user';
  bool get isAssistant => role == 'assistant';
  bool get isCard => type == 'card' && cardType != null;
  bool get hasImage => imageUrl != null && imageUrl!.isNotEmpty;
}
