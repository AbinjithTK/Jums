import 'dart:convert';
import 'package:shared_preferences/shared_preferences.dart';
import '../models/message.dart';
import '../models/chat_session.dart';

/// Local chat storage — borrowed from OpenClaw's memory/session patterns.
///
/// OpenClaw uses SQLite-vec for vector memory with hybrid search. We keep it
/// simpler: SharedPreferences for message cache + session metadata. This gives
/// us offline access, instant load on app start, and background sync with the
/// server. Messages are keyed by session ID so we can support multiple
/// conversation threads later (like OpenClaw's multi-channel sessions).
class ChatStorageService {
  static const _messagesKey = 'chat_messages';
  static const _sessionKey = 'chat_session';
  static const _maxCachedMessages = 200;

  /// Save messages to local storage.
  Future<void> saveMessages(List<Message> messages) async {
    final prefs = await SharedPreferences.getInstance();
    final trimmed = messages.length > _maxCachedMessages
        ? messages.sublist(messages.length - _maxCachedMessages)
        : messages;
    final jsonList = trimmed.map((m) => _messageToJson(m)).toList();
    await prefs.setString(_messagesKey, jsonEncode(jsonList));

    // Update session metadata
    if (trimmed.isNotEmpty) {
      final last = trimmed.last;
      final session = ChatSession(
        id: 'default',
        title: _inferTitle(trimmed),
        messageCount: trimmed.length,
        createdAt: trimmed.first.createdAt ?? DateTime.now(),
        lastMessageAt: last.createdAt ?? DateTime.now(),
      );
      await prefs.setString(_sessionKey, jsonEncode(session.toJson()));
    }
  }

  /// Load cached messages (instant, no network).
  Future<List<Message>> loadMessages() async {
    final prefs = await SharedPreferences.getInstance();
    final raw = prefs.getString(_messagesKey);
    if (raw == null) return [];
    try {
      final list = jsonDecode(raw) as List<dynamic>;
      return list
          .map((e) => Message.fromJson(e as Map<String, dynamic>))
          .toList();
    } catch (_) {
      return [];
    }
  }

  /// Load session metadata.
  Future<ChatSession?> loadSession() async {
    final prefs = await SharedPreferences.getInstance();
    final raw = prefs.getString(_sessionKey);
    if (raw == null) return null;
    try {
      return ChatSession.fromJson(
          jsonDecode(raw) as Map<String, dynamic>);
    } catch (_) {
      return null;
    }
  }

  /// Clear local cache.
  Future<void> clear() async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.remove(_messagesKey);
    await prefs.remove(_sessionKey);
  }

  /// Infer a session title from the first user message.
  String _inferTitle(List<Message> messages) {
    final firstUser = messages.where((m) => m.isUser).firstOrNull;
    if (firstUser == null || firstUser.content == null) return 'Chat';
    final text = firstUser.content!;
    return text.length > 40 ? '${text.substring(0, 40)}...' : text;
  }

  Map<String, dynamic> _messageToJson(Message m) => {
        'id': m.id,
        'userId': m.userId,
        'role': m.role,
        'type': m.type,
        'content': m.content,
        'cardType': m.cardType,
        'cardData': m.cardData,
        'timestamp': m.timestamp,
        'createdAt': m.createdAt?.toIso8601String(),
        'imageUrl': m.imageUrl,
      };
}
