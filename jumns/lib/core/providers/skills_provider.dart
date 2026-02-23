import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../models/skill.dart';
import '../services/api_client.dart';

class SkillsNotifier extends StateNotifier<AsyncValue<List<Skill>>> {
  final ApiClient _api;

  SkillsNotifier(this._api) : super(const AsyncValue.loading()) {
    load();
  }

  Future<void> load() async {
    state = const AsyncValue.loading();
    try {
      final json = await _api.get('/api/skills');
      final list = (json as List<dynamic>)
          .map((e) => Skill.fromJson(e as Map<String, dynamic>))
          .toList();
      state = AsyncValue.data(list);
    } catch (e, st) {
      state = AsyncValue.error(e, st);
    }
  }

  Future<void> create({
    required String name,
    required String type,
    String description = '',
    String category = 'mcp',
  }) async {
    await _api.post('/api/skills', body: {
      'name': name,
      'type': type,
      'description': description,
      'category': category,
    });
    await load();
  }

  Future<void> update(String id, Map<String, dynamic> data) async {
    await _api.patch('/api/skills/$id', body: data);
    await load();
  }

  Future<void> delete(String id) async {
    await _api.delete('/api/skills/$id');
    await load();
  }
}

final skillsNotifierProvider =
    StateNotifierProvider<SkillsNotifier, AsyncValue<List<Skill>>>((ref) {
  return SkillsNotifier(ref.watch(apiClientProvider));
});
