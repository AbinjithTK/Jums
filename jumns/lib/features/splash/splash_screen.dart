import 'dart:math' as math;
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:shared_preferences/shared_preferences.dart';
import '../../core/providers/auth_provider.dart';
import '../../core/services/auth_service.dart';
import '../../core/state/app_state.dart';
import '../../core/theme/jumns_colors.dart';

class SplashScreen extends ConsumerStatefulWidget {
  const SplashScreen({super.key});

  @override
  ConsumerState<SplashScreen> createState() => _SplashScreenState();
}

class _SplashScreenState extends ConsumerState<SplashScreen>
    with TickerProviderStateMixin {
  late final AnimationController _logoController;
  late final AnimationController _fadeController;
  late final Animation<double> _logoScale;
  late final Animation<double> _logoRotation;
  late final Animation<double> _titleOpacity;
  late final Animation<double> _subtitleOpacity;
  bool _navigated = false;

  @override
  void initState() {
    super.initState();

    _logoController = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 1200),
    );
    _logoScale = CurvedAnimation(
      parent: _logoController,
      curve: Curves.elasticOut,
    );
    _logoRotation = Tween<double>(begin: -12, end: 0).animate(
      CurvedAnimation(parent: _logoController, curve: Curves.easeOutBack),
    );

    _fadeController = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 800),
    );
    _titleOpacity = Tween<double>(begin: 0, end: 1).animate(
      CurvedAnimation(
        parent: _fadeController,
        curve: const Interval(0.0, 0.6, curve: Curves.easeIn),
      ),
    );
    _subtitleOpacity = Tween<double>(begin: 0, end: 1).animate(
      CurvedAnimation(
        parent: _fadeController,
        curve: const Interval(0.3, 1.0, curve: Curves.easeIn),
      ),
    );

    _logoController.forward();
    Future.delayed(const Duration(milliseconds: 400), () {
      if (mounted) _fadeController.forward();
    });

    // Start checking auth after minimum splash duration
    _waitAndNavigate();
  }

  Future<void> _waitAndNavigate() async {
    // Show splash for at least 2 seconds
    await Future.delayed(const Duration(milliseconds: 2000));

    // Wait for auth to resolve (up to 5 more seconds)
    for (var i = 0; i < 50; i++) {
      if (!mounted) return;
      final status = ref.read(authNotifierProvider).status;
      if (status != AuthStatus.unknown) break;
      await Future.delayed(const Duration(milliseconds: 100));
    }

    _navigate();
  }

  void _navigate() {
    if (!mounted || _navigated) return;
    _navigated = true;

    final authState = ref.read(authNotifierProvider);
    final appState = ref.read(appStateProvider);
    final isDemoMode = ref.read(demoModeProvider);

    if (isDemoMode) {
      context.go('/chat');
      return;
    }

    if (authState.status == AuthStatus.authenticated) {
      context.go(appState.hasCompletedOnboarding ? '/chat' : '/welcome');
    } else {
      // Not authenticated — check if they've seen onboarding before
      context.go(appState.hasCompletedOnboarding ? '/login' : '/welcome');
    }
  }

  @override
  void dispose() {
    _logoController.dispose();
    _fadeController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: JumnsColors.paper,
      body: Center(
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            AnimatedBuilder(
              animation: _logoController,
              builder: (context, child) {
                return Transform.rotate(
                  angle: _logoRotation.value * math.pi / 180,
                  child: Transform.scale(
                    scale: _logoScale.value,
                    child: child,
                  ),
                );
              },
              child: Stack(
                alignment: Alignment.center,
                children: [
                  Transform.rotate(
                    angle: 8 * math.pi / 180,
                    child: Container(
                      width: 140,
                      height: 140,
                      decoration: BoxDecoration(
                        color: JumnsColors.mint.withAlpha(100),
                        borderRadius: const BorderRadius.only(
                          topLeft: Radius.elliptical(64, 55),
                          topRight: Radius.elliptical(36, 58),
                          bottomLeft: Radius.elliptical(27, 42),
                          bottomRight: Radius.elliptical(73, 45),
                        ),
                      ),
                    ),
                  ),
                  Container(
                    width: 110,
                    height: 110,
                    decoration: BoxDecoration(
                      color: JumnsColors.lavender,
                      borderRadius: const BorderRadius.only(
                        topLeft: Radius.elliptical(64, 55),
                        topRight: Radius.elliptical(36, 58),
                        bottomLeft: Radius.elliptical(27, 42),
                        bottomRight: Radius.elliptical(73, 45),
                      ),
                      border: Border.all(color: JumnsColors.ink, width: 2.5),
                    ),
                    child: Center(
                      child: Text(
                        'J',
                        style: GoogleFonts.gloriaHallelujah(
                          color: JumnsColors.charcoal,
                          fontSize: 52,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                    ),
                  ),
                ],
              ),
            ),
            const SizedBox(height: 28),
            AnimatedBuilder(
              animation: _titleOpacity,
              builder: (context, child) => Opacity(
                opacity: _titleOpacity.value,
                child: child,
              ),
              child: Text(
                'Jumns',
                style: GoogleFonts.gloriaHallelujah(
                  color: JumnsColors.charcoal,
                  fontSize: 38,
                  fontWeight: FontWeight.bold,
                ),
              ),
            ),
            const SizedBox(height: 8),
            AnimatedBuilder(
              animation: _subtitleOpacity,
              builder: (context, child) => Opacity(
                opacity: _subtitleOpacity.value,
                child: child,
              ),
              child: Text(
                'YOUR AI LIFE ASSISTANT',
                style: GoogleFonts.architectsDaughter(
                  color: JumnsColors.ink.withAlpha(150),
                  fontSize: 13,
                  fontWeight: FontWeight.w700,
                  letterSpacing: 2,
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }
}
