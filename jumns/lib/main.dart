import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'core/navigation/router.dart';
import 'core/providers/auth_provider.dart';
import 'core/services/auth_service.dart';
import 'core/services/revenuecat_service.dart';
import 'core/theme/jumns_theme.dart';

void main() async {
  WidgetsFlutterBinding.ensureInitialized();

  // Light status bar and nav bar
  SystemChrome.setSystemUIOverlayStyle(const SystemUiOverlayStyle(
    statusBarColor: Colors.transparent,
    statusBarIconBrightness: Brightness.dark,
    systemNavigationBarColor: Colors.white,
    systemNavigationBarIconBrightness: Brightness.dark,
  ));

  // Initialize services before the app renders
  final authService = AuthService();
  final rc = RevenueCatService();

  // Try to restore a previous Cognito session (so the user stays logged in)
  final restoredUser = await authService.restoreSession();

  // Check if demo mode was previously enabled
  final prefs = await SharedPreferences.getInstance();
  final wasDemoMode = prefs.getBool('demo_mode') ?? false;

  // Initialize RevenueCat — pass the user ID if we have one
  // Wrapped in try-catch: emulators without Play Store will fail here
  try {
    await rc.init(userId: restoredUser?.sub);
  } catch (_) {
    // RevenueCat not available (emulator, no Play Store) — continue without it
  }

  runApp(ProviderScope(
    overrides: [
      authServiceProvider.overrideWithValue(authService),
      revenueCatServiceProvider.overrideWithValue(rc),
      if (wasDemoMode) demoModeProvider.overrideWith((ref) => true),
    ],
    child: const JumnsApp(),
  ));
}

class JumnsApp extends ConsumerWidget {
  const JumnsApp({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final router = ref.watch(routerProvider);
    return MaterialApp.router(
      title: 'Jumns',
      debugShowCheckedModeBanner: false,
      theme: jumnsTheme(),
      routerConfig: router,
    );
  }
}
