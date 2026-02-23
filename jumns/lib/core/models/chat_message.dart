enum MessageRole { user, assistant, system }

enum AgentReadyState { ready, thinking, working }

class ChatMessage {
  final String id;
  final MessageRole role;
  final String content;
  final int timestampMs;

  const ChatMessage({
    required this.id,
    required this.role,
    required this.content,
    required this.timestampMs,
  });

  DateTime get dateTime =>
      DateTime.fromMillisecondsSinceEpoch(timestampMs);
}
