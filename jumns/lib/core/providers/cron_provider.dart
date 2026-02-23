import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../models/cron_job.dart';
import '../services/api_client.dart';

class CronNotifier extends StateNotifier<AsyncValue<List<CronJob>>> {
  final ApiClient _api;

  CronNotifier(this._api) : super(const AsyncValue.loading()) {
    load();
  }

  Future<void> load() async {
    state = const AsyncValue.loading();
    try {
      final json = await _api.get('/api/cron?includeDisabled=true');
      final list = (json as List<dynamic>)
          .map((e) => CronJob.fromJson(e as Map<String, dynamic>))
          .toList();
      state = AsyncValue.data(list);
    } catch (e, st) {
      state = AsyncValue.error(e, st);
    }
  }

  Future<void> create({
    required String name,
    required String scheduleType,
    required String scheduleValue,
    required String actionMessage,
    String description = '',
  }) async {
    await _api.post('/api/cron', body: {
      'name': name,
      'scheduleType': scheduleType,
      'scheduleValue': scheduleValue,
      'actionMessage': actionMessage,
      'description': description,
    });
    await load();
  }

  Future<void> update(String id, Map<String, dynamic> data) async {
    await _api.patch('/api/cron/$id', body: data);
    await load();
  }

  Future<void> toggle(String id, bool enabled) async {
    await _api.patch('/api/cron/$id', body: {'enabled': enabled});
    await load();
  }

  Future<void> delete(String id) async {
    await _api.delete('/api/cron/$id');
    await load();
  }

  Future<void> runNow(String id) async {
    await _api.post('/api/cron/$id/run');
    await load();
  }
}

final cronNotifierProvider =
    StateNotifierProvider<CronNotifier, AsyncValue<List<CronJob>>>((ref) {
  return CronNotifier(ref.watch(apiClientProvider));
});
