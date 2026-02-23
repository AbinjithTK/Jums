import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../models/task.dart';
import '../services/api_client.dart';

class TasksNotifier extends StateNotifier<AsyncValue<List<Task>>> {
  final ApiClient _api;

  TasksNotifier(this._api) : super(const AsyncValue.loading()) {
    load();
  }

  Future<void> load({String? goalId}) async {
    state = const AsyncValue.loading();
    try {
      final query = goalId != null ? {'goalId': goalId} : null;
      final json = await _api.get('/api/tasks', query: query);
      final list = (json as List<dynamic>)
          .map((e) => Task.fromJson(e as Map<String, dynamic>))
          .toList();
      state = AsyncValue.data(list);
    } catch (e, st) {
      state = AsyncValue.error(e, st);
    }
  }

  Future<Task?> create({
    required String title,
    String time = '',
    String detail = '',
    String type = 'task',
    String? goalId,
    String? dueDate,
    bool requiresProof = false,
  }) async {
    try {
      final json = await _api.post('/api/tasks', body: {
        'title': title,
        'time': time,
        'detail': detail,
        'type': type,
        if (goalId != null) 'goalId': goalId,
        if (dueDate != null) 'dueDate': dueDate,
        'requiresProof': requiresProof,
      });
      final task = Task.fromJson(json as Map<String, dynamic>);
      await load();
      return task;
    } catch (_) {
      return null;
    }
  }

  Future<void> complete(String id, {String? proofUrl, String? proofType}) async {
    await _api.post('/api/tasks/$id/complete', body: {
      if (proofUrl != null) 'proofUrl': proofUrl,
      if (proofType != null) 'proofType': proofType,
    });
    await load();
  }

  Future<void> update(String id, Map<String, dynamic> data) async {
    await _api.patch('/api/tasks/$id', body: data);
    await load();
  }

  Future<void> delete(String id) async {
    await _api.delete('/api/tasks/$id');
    await load();
  }
}

final tasksNotifierProvider =
    StateNotifierProvider<TasksNotifier, AsyncValue<List<Task>>>((ref) {
  return TasksNotifier(ref.watch(apiClientProvider));
});

/// Currently selected date on the Planner date carousel.
final selectedDateProvider = StateProvider<DateTime>((ref) => DateTime.now());

/// Tasks filtered by the selected date.
final tasksForDateProvider = Provider<AsyncValue<List<Task>>>((ref) {
  final selected = ref.watch(selectedDateProvider);
  final tasksAsync = ref.watch(tasksNotifierProvider);
  return tasksAsync.whenData((tasks) {
    final dateStr = _toIso(selected);
    return tasks.where((t) {
      if (t.dueDate == dateStr) return true;
      // Tasks with no dueDate show on today
      if (t.dueDate == null || t.dueDate!.isEmpty) {
        return _toIso(DateTime.now()) == dateStr;
      }
      return false;
    }).toList();
  });
});

/// Overdue tasks (dueDate < today, not completed).
final overdueTasksProvider = Provider<List<Task>>((ref) {
  final tasks = ref.watch(tasksNotifierProvider).valueOrNull ?? [];
  final todayStr = _toIso(DateTime.now());
  return tasks
      .where((t) =>
          !t.completed &&
          t.dueDate != null &&
          t.dueDate!.isNotEmpty &&
          t.dueDate!.compareTo(todayStr) < 0)
      .toList();
});

String _toIso(DateTime dt) =>
    '${dt.year}-${dt.month.toString().padLeft(2, '0')}-${dt.day.toString().padLeft(2, '0')}';
