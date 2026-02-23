import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../models/goal.dart';
import '../services/api_client.dart';

final goalsProvider = FutureProvider<List<Goal>>((ref) async {
  final api = ref.watch(apiClientProvider);
  final json = await api.get('/api/goals');
  final list = json as List<dynamic>;
  return list.map((e) => Goal.fromJson(e as Map<String, dynamic>)).toList();
});

final goalProvider = FutureProvider.family<Goal?, String>((ref, id) async {
  final api = ref.watch(apiClientProvider);
  try {
    final json = await api.get('/api/goals/$id');
    return Goal.fromJson(json as Map<String, dynamic>);
  } on ApiException catch (e) {
    if (e.statusCode == 404) return null;
    rethrow;
  }
});

class GoalsNotifier extends StateNotifier<AsyncValue<List<Goal>>> {
  final ApiClient _api;

  GoalsNotifier(this._api) : super(const AsyncValue.loading()) {
    load();
  }

  Future<void> load() async {
    state = const AsyncValue.loading();
    try {
      final json = await _api.get('/api/goals');
      final list = (json as List<dynamic>)
          .map((e) => Goal.fromJson(e as Map<String, dynamic>))
          .toList();
      state = AsyncValue.data(list);
    } catch (e, st) {
      state = AsyncValue.error(e, st);
    }
  }

  Future<Goal?> create({
    required String title,
    required String category,
    int total = 100,
    String unit = '',
  }) async {
    try {
      final json = await _api.post('/api/goals', body: {
        'title': title,
        'category': category,
        'total': total,
        'unit': unit,
      });
      final goal = Goal.fromJson(json as Map<String, dynamic>);
      await load();
      return goal;
    } catch (_) {
      return null;
    }
  }

  Future<void> update(String id, Map<String, dynamic> data) async {
    await _api.patch('/api/goals/$id', body: data);
    await load();
  }

  Future<void> delete(String id) async {
    await _api.delete('/api/goals/$id');
    await load();
  }
}

final goalsNotifierProvider =
    StateNotifierProvider<GoalsNotifier, AsyncValue<List<Goal>>>((ref) {
  return GoalsNotifier(ref.watch(apiClientProvider));
});

/// Weekly progress data: task completion counts per day (Mon-Sun).
class WeeklyProgress {
  final List<int> counts; // 7 items: Mon=0 .. Sun=6
  final int total;
  final int bestDay; // -1 if no data

  const WeeklyProgress({
    this.counts = const [0, 0, 0, 0, 0, 0, 0],
    this.total = 0,
    this.bestDay = -1,
  });

  factory WeeklyProgress.fromJson(Map<String, dynamic> json) {
    final rawCounts = json['counts'] as List<dynamic>? ?? [];
    final counts = rawCounts.map((e) => (e as num).toInt()).toList();
    while (counts.length < 7) counts.add(0);
    return WeeklyProgress(
      counts: counts,
      total: (json['total'] as num?)?.toInt() ?? 0,
      bestDay: (json['bestDay'] as num?)?.toInt() ?? -1,
    );
  }
}

final weeklyProgressProvider = FutureProvider<WeeklyProgress>((ref) async {
  final api = ref.watch(apiClientProvider);
  try {
    final json = await api.get('/api/goals/weekly-progress');
    return WeeklyProgress.fromJson(json as Map<String, dynamic>);
  } catch (_) {
    return const WeeklyProgress();
  }
});
