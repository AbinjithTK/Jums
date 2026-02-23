import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../../features/auth/login_screen.dart';
import '../../features/chat/chat_screen.dart';
import '../../features/tasks/tasks_screen.dart';
import '../../features/goals/goals_screen.dart';
import '../../features/toolkit/toolkit_screen.dart';
import '../../features/settings/settings_screen.dart';
import '../../features/voice/voice_mode_screen.dart';
import '../../features/paywall/paywall_screen.dart';
import '../../features/onboarding/welcome_screen.dart';
import '../../features/onboarding/personality_setup_screen.dart';
import '../../features/splash/splash_screen.dart';
import '../../shell/root_shell.dart';
import '../providers/auth_provider.dart';
import '../services/auth_service.dart';
import '../state/app_state.dart';

final _rootNavigatorKey = GlobalKey<NavigatorState>();
final _shellNavigatorKey = GlobalKey<NavigatorState>();

/// Routes that don't need auth/onboarding redirect checks.
const _noRedirectRoutes = {'/splash', '/welcome', '/personality-setup', '/login'};

final routerProvider = Provider<GoRouter>((ref) {
  final authState = ref.watch(authNotifierProvider);
  final isDemoMode = ref.watch(demoModeProvider);

  return GoRouter(
    navigatorKey: _rootNavigatorKey,
    initialLocation: '/splash',
    redirect: (context, state) {
      final loc = state.matchedLocation;

      // Splash always allowed — it handles its own navigation
      if (loc == '/splash') return null;

      // Demo mode — skip all auth checks
      if (isDemoMode) return null;

      // Let welcome and personality-setup through without auth
      if (loc == '/welcome' || loc == '/personality-setup') return null;

      final isAuth = authState.status == AuthStatus.authenticated;
      final isLoading = authState.status == AuthStatus.unknown;

      // Still resolving auth — stay put
      if (isLoading) return null;

      // Not authenticated and not on login — go to login
      if (!isAuth && loc != '/login') return '/login';

      // Authenticated but on login — go to chat (or onboarding)
      if (isAuth && loc == '/login') {
        final container = ProviderScope.containerOf(context);
        final appState = container.read(appStateProvider);
        return appState.hasCompletedOnboarding ? '/chat' : '/welcome';
      }

      return null;
    },
    routes: [
      // Splash (always first)
      GoRoute(
        path: '/splash',
        parentNavigatorKey: _rootNavigatorKey,
        builder: (context, state) => const SplashScreen(),
      ),
      // Login (no shell)
      GoRoute(
        path: '/login',
        parentNavigatorKey: _rootNavigatorKey,
        builder: (context, state) => const LoginScreen(),
      ),
      // Bottom nav shell
      ShellRoute(
        navigatorKey: _shellNavigatorKey,
        builder: (context, state, child) => RootShell(child: child),
        routes: [
          GoRoute(
            path: '/chat',
            pageBuilder: (context, state) => const NoTransitionPage(
              child: ChatScreen(),
            ),
          ),
          GoRoute(
            path: '/tasks',
            pageBuilder: (context, state) => const NoTransitionPage(
              child: TasksScreen(),
            ),
          ),
          GoRoute(
            path: '/goals',
            pageBuilder: (context, state) => const NoTransitionPage(
              child: GoalsScreen(),
            ),
          ),
          GoRoute(
            path: '/toolkit',
            pageBuilder: (context, state) => const NoTransitionPage(
              child: ToolkitScreen(),
            ),
          ),
          GoRoute(
            path: '/settings',
            pageBuilder: (context, state) => const NoTransitionPage(
              child: SettingsScreen(),
            ),
          ),
        ],
      ),
      // Full-screen overlays (no bottom nav)
      GoRoute(
        path: '/voice',
        parentNavigatorKey: _rootNavigatorKey,
        builder: (context, state) => const VoiceModeScreen(),
      ),
      GoRoute(
        path: '/paywall',
        parentNavigatorKey: _rootNavigatorKey,
        builder: (context, state) => const PaywallScreen(),
      ),
      GoRoute(
        path: '/welcome',
        parentNavigatorKey: _rootNavigatorKey,
        builder: (context, state) => const WelcomeScreen(),
      ),
      GoRoute(
        path: '/personality-setup',
        parentNavigatorKey: _rootNavigatorKey,
        builder: (context, state) => const PersonalitySetupScreen(),
      ),
    ],
  );
});
