import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../models/reminder.dart';
import '../services/api_client.dart';

class RemindersNotifier extends StateNotifier<AsyncValue<List<Reminder>>> {
  final ApiClient _api;

  RemindersNotifier(this._api) : super(const AsyncValue.loading()) {
    load();
  }

  Future<void> load() async {
    state = const AsyncValue.loading();
    try {
      final json = await _api.get('/api/reminders');
      final list = (json as List<dynamic>)
          .map((e) => Reminder.fromJson(e as Map<String, dynamic>))
          .toList();
      state = AsyncValue.data(list);
    } catch (e, st) {
      state = AsyncValue.error(e, st);
    }
  }

  Future<void> create({
    required String title,
    required String time,
    String? goalId,
  }) async {
    await _api.post('/api/reminders', body: {
      'title': title,
      'time': time,
      if (goalId != null) 'goalId': goalId,
    });
    await load();
  }

  Future<void> update(String id, Map<String, dynamic> data) async {
    await _api.patch('/api/reminders/$id', body: data);
    await load();
  }

  /// Snooze a reminder by N minutes (default 30).
  Future<void> snooze(String id, {int minutes = 30}) async {
    try {
      await _api.post('/api/reminders/$id/snooze', body: {
        'minutes': minutes,
      });
      await load();
    } catch (_) {}
  }

  Future<void> delete(String id) async {
    await _api.delete('/api/reminders/$id');
    await load();
  }
}

final remindersNotifierProvider =
    StateNotifierProvider<RemindersNotifier, AsyncValue<List<Reminder>>>((ref) {
  return RemindersNotifier(ref.watch(apiClientProvider));
});
