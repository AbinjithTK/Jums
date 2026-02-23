/// Local chat session metadata — borrowed from OpenClaw's session management.
/// OpenClaw tracks sessions per channel with transcripts, model overrides,
/// and send policies. We simplify to: one session = one conversation thread
/// with local persistence for offline access and quick reload.
class ChatSession {
  final String id;
  final String title;
  final int messageCount;
  final DateTime createdAt;
  final DateTime lastMessageAt;

  const ChatSession({
    required this.id,
    required this.title,
    required this.messageCount,
    required this.createdAt,
    required this.lastMessageAt,
  });

  Map<String, dynamic> toJson() => {
        'id': id,
        'title': title,
        'messageCount': messageCount,
        'createdAt': createdAt.toIso8601String(),
        'lastMessageAt': lastMessageAt.toIso8601String(),
      };

  factory ChatSession.fromJson(Map<String, dynamic> json) => ChatSession(
        id: json['id'] as String,
        title: json['title'] as String? ?? 'Chat',
        messageCount: json['messageCount'] as int? ?? 0,
        createdAt: DateTime.tryParse(json['createdAt'] as String? ?? '') ??
            DateTime.now(),
        lastMessageAt:
            DateTime.tryParse(json['lastMessageAt'] as String? ?? '') ??
                DateTime.now(),
      );
}
