import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:shared_preferences/shared_preferences.dart';
import '../services/api_client.dart';

/// Lightweight app-wide state — just onboarding gate + tab index.
/// Domain data (messages, goals, tasks, etc.) lives in dedicated providers.
class AppState {
  final bool hasCompletedOnboarding;
  final int currentTabIndex;
  final bool isSeeding;

  const AppState({
    this.hasCompletedOnboarding = false,
    this.currentTabIndex = 0,
    this.isSeeding = false,
  });

  AppState copyWith({
    bool? hasCompletedOnboarding,
    int? currentTabIndex,
    bool? isSeeding,
  }) =>
      AppState(
        hasCompletedOnboarding:
            hasCompletedOnboarding ?? this.hasCompletedOnboarding,
        currentTabIndex: currentTabIndex ?? this.currentTabIndex,
        isSeeding: isSeeding ?? this.isSeeding,
      );
}

class AppStateNotifier extends StateNotifier<AppState> {
  final ApiClient _api;

  AppStateNotifier(this._api) : super(const AppState()) {
    _loadOnboardingState();
  }

  Future<void> _loadOnboardingState() async {
    // Always check local prefs first (instant, no network needed)
    final prefs = await SharedPreferences.getInstance();
    final localCompleted = prefs.getBool('onboarding_completed') ?? false;
    if (localCompleted) {
      state = state.copyWith(hasCompletedOnboarding: true);
      return;
    }

    // If local says not completed, try server (user might have onboarded on another device)
    try {
      final json = await _api.get('/api/user-settings');
      if (json != null) {
        final completed =
            (json as Map<String, dynamic>)['onboardingCompleted'] as bool? ??
                false;
        if (completed) {
          // Sync server state to local
          await prefs.setBool('onboarding_completed', true);
          state = state.copyWith(hasCompletedOnboarding: true);
          return;
        }
      }
    } catch (_) {
      // Server unreachable — stick with local value
    }
  }

  Future<void> completeOnboarding() async {
    state = state.copyWith(hasCompletedOnboarding: true);
    final prefs = await SharedPreferences.getInstance();
    await prefs.setBool('onboarding_completed', true);

    // Persist to server + seed initial data
    try {
      await _api.post('/api/user-settings', body: {
        'onboardingCompleted': true,
      });
      state = state.copyWith(isSeeding: true);
      await _api.post('/api/seed');
      state = state.copyWith(isSeeding: false);
    } catch (_) {
      state = state.copyWith(isSeeding: false);
    }
  }

  void setTabIndex(int index) {
    state = state.copyWith(currentTabIndex: index);
  }
}

final appStateProvider =
    StateNotifierProvider<AppStateNotifier, AppState>((ref) {
  return AppStateNotifier(ref.watch(apiClientProvider));
});
