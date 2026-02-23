import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../models/message.dart';
import '../services/api_client.dart';
import '../services/chat_storage_service.dart';

/// Messages provider — sends chat to the local backend server.
///
/// Borrowed from OpenClaw's session/transcript pattern: messages are cached
/// locally for instant load, then synced with the server. The backend calls
/// Gemini, parses action blocks (create_goal, create_task, create_reminder),
/// stores everything in memory, and returns the AI response.
class MessagesNotifier extends StateNotifier<AsyncValue<List<Message>>> {
  final ApiClient _api;
  final ChatStorageService _storage = ChatStorageService();

  MessagesNotifier(this._api) : super(const AsyncValue.data([]));

  /// Load messages — local cache first (instant), then server sync.
  Future<void> load() async {
    // 1. Load from local cache immediately
    final cached = await _storage.loadMessages();
    if (cached.isNotEmpty) {
      state = AsyncValue.data(cached);
    }

    // 2. Sync from server in background
    try {
      final json = await _api.get('/api/messages');
      final list = (json as List<dynamic>)
          .map((e) => Message.fromJson(e as Map<String, dynamic>))
          .toList();
      state = AsyncValue.data(list);
      // Persist to local cache
      await _storage.saveMessages(list);
    } catch (e) {
      // If backend is unreachable, keep cached data
      if (state is! AsyncData) {
        state = const AsyncValue.data([]);
      }
    }
  }

  /// Send a message to the backend and get a response.
  /// The backend handles Gemini + action parsing (goals/tasks/reminders).
  /// Returns the AI message so the caller can check for cards/actions.
  Future<Message?> sendChat(String text) async {
    final current = state.valueOrNull ?? [];
    final now = DateTime.now();
    final ts = _formatTime(now);

    // Add user message immediately for instant feedback
    final userMsg = Message(
      id: 'u_${now.millisecondsSinceEpoch}',
      userId: 'local',
      role: 'user',
      type: 'text',
      content: text,
      timestamp: ts,
      createdAt: now,
    );
    state = AsyncValue.data([...current, userMsg]);

    try {
      // POST to backend — it calls Gemini, parses actions, returns response
      final json = await _api.post('/api/chat', body: {'message': text});
      final data = json as Map<String, dynamic>;

      final aiMsg = Message(
        id: data['id'] as String? ?? 'a_${DateTime.now().millisecondsSinceEpoch}',
        userId: 'jumns',
        role: 'assistant',
        type: data['type'] as String? ?? 'text',
        content: data['content'] as String?,
        cardType: data['cardType'] as String?,
        cardData: data['cardData'] as Map<String, dynamic>?,
        timestamp: _formatTime(DateTime.now()),
        createdAt: DateTime.now(),
      );
      state = AsyncValue.data([...state.valueOrNull ?? [], aiMsg]);
      // Persist to local cache
      await _storage.saveMessages(state.valueOrNull ?? []);
      return aiMsg;
    } catch (e) {
      final errMsg = Message(
        id: 'err_${DateTime.now().millisecondsSinceEpoch}',
        userId: 'jumns',
        role: 'assistant',
        type: 'text',
        content: 'Sorry, I couldn\'t connect right now. Please try again.',
        timestamp: _formatTime(DateTime.now()),
        createdAt: DateTime.now(),
      );
      state = AsyncValue.data([...state.valueOrNull ?? [], errMsg]);
      return null;
    }
  }

  /// Clear all messages (server + local cache).
  Future<void> clearAll() async {
    try {
      await _api.delete('/api/messages');
    } catch (_) {}
    await _storage.clear();
    state = const AsyncValue.data([]);
  }

  String _formatTime(DateTime dt) {
    final h = dt.hour > 12 ? dt.hour - 12 : (dt.hour == 0 ? 12 : dt.hour);
    final m = dt.minute.toString().padLeft(2, '0');
    final ampm = dt.hour >= 12 ? 'PM' : 'AM';
    return '$h:$m $ampm';
  }
}

final messagesNotifierProvider =
    StateNotifierProvider<MessagesNotifier, AsyncValue<List<Message>>>((ref) {
  return MessagesNotifier(ref.watch(apiClientProvider));
});

/// Whether the AI is currently processing a response.
final isChatLoadingProvider = StateProvider<bool>((ref) => false);
