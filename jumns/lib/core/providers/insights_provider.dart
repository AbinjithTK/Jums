import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../models/proactive_insight.dart';
import '../services/api_client.dart';

/// Proactive insights provider — mirrors the backend's proactive engine.
///
/// The backend (proactive-engine.ts) runs on a 30-min interval, gathering
/// context about goals/tasks/reminders, detecting patterns (at-risk goals,
/// task overload, missing reminders, stale goals), and generating AI insights.
/// This provider fetches those insights and exposes them to the UI.
class InsightsNotifier extends StateNotifier<AsyncValue<List<ProactiveInsight>>> {
  final ApiClient _api;

  InsightsNotifier(this._api) : super(const AsyncValue.loading()) {
    load();
  }

  Future<void> load() async {
    try {
      final json = await _api.get('/api/insights');
      final list = (json as List<dynamic>)
          .map((e) => ProactiveInsight.fromJson(e as Map<String, dynamic>))
          .toList();
      state = AsyncValue.data(list);
    } catch (e, st) {
      state = AsyncValue.error(e, st);
    }
  }

  Future<int> unreadCount() async {
    try {
      final json = await _api.get('/api/insights/unread');
      return (json as Map<String, dynamic>)['count'] as int? ?? 0;
    } catch (_) {
      return 0;
    }
  }

  Future<void> markRead(String id) async {
    try {
      await _api.post('/api/insights/$id/read');
      // Optimistic update
      final current = state.valueOrNull ?? [];
      state = AsyncValue.data(
        current.map((i) => i.id == id
            ? ProactiveInsight(
                id: i.id, userId: i.userId, type: i.type,
                title: i.title, content: i.content, priority: i.priority,
                cardType: i.cardType, cardData: i.cardData,
                actionTaken: i.actionTaken, read: true,
                dismissed: i.dismissed, createdAt: i.createdAt,
              )
            : i).toList(),
      );
    } catch (_) {}
  }

  Future<void> dismiss(String id) async {
    try {
      await _api.post('/api/insights/$id/dismiss');
      final current = state.valueOrNull ?? [];
      state = AsyncValue.data(
        current.where((i) => i.id != id).toList(),
      );
    } catch (_) {}
  }

  /// Trigger a manual proactive engine run.
  Future<void> runEngine() async {
    try {
      await _api.post('/api/insights/run');
      await load();
    } catch (_) {}
  }
}

final insightsNotifierProvider =
    StateNotifierProvider<InsightsNotifier, AsyncValue<List<ProactiveInsight>>>(
        (ref) {
  return InsightsNotifier(ref.watch(apiClientProvider));
});

/// Unread insight count for badge display.
final unreadInsightCountProvider = FutureProvider<int>((ref) async {
  final api = ref.watch(apiClientProvider);
  try {
    final json = await api.get('/api/insights/unread');
    return (json as Map<String, dynamic>)['count'] as int? ?? 0;
  } catch (_) {
    return 0;
  }
});
