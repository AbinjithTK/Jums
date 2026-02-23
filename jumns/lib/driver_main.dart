import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_driver/driver_extension.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'core/navigation/router.dart';
import 'core/services/auth_service.dart';
import 'core/services/revenuecat_service.dart';
import 'core/theme/jumns_theme.dart';

void main() async {
  enableFlutterDriverExtension();
  WidgetsFlutterBinding.ensureInitialized();

  SystemChrome.setSystemUIOverlayStyle(const SystemUiOverlayStyle(
    statusBarColor: Colors.transparent,
    statusBarIconBrightness: Brightness.dark,
    systemNavigationBarColor: Colors.white,
    systemNavigationBarIconBrightness: Brightness.dark,
  ));

  final authService = AuthService();
  final rc = RevenueCatService();
  final restoredUser = await authService.restoreSession();
  try {
    await rc.init(userId: restoredUser?.sub);
  } catch (_) {}

  runApp(ProviderScope(
    overrides: [
      authServiceProvider.overrideWithValue(authService),
      revenueCatServiceProvider.overrideWithValue(rc),
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
