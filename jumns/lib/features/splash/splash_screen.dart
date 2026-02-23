import 'dart:math' as math;
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:google_fonts/google_fonts.dart';
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

  @override
  void initState() {
    super.initState();

    // Logo blob: scale up + gentle wobble
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

    // Text fade-in
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

    // Navigate after splash
    Future.delayed(const Duration(milliseconds: 2200), _navigate);
  }

  void _navigate() {
    if (!mounted) return;

    final authState = ref.read(authNotifierProvider);
    final appState = ref.read(appStateProvider);
    final isDemoMode = ref.read(demoModeProvider);

    if (isDemoMode) {
      context.go('/chat');
      return;
    }

    if (authState.status == AuthStatus.authenticated) {
      // Logged in — check onboarding
      if (appState.hasCompletedOnboarding) {
        context.go('/chat');
      } else {
        context.go('/welcome');
      }
    } else {
      // Not logged in — check if first time
      if (appState.hasCompletedOnboarding) {
        // Returning user, just needs to log in
        context.go('/login');
      } else {
        // Brand new user — show welcome first
        context.go('/welcome');
      }
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
            // Animated logo blob
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
                  // Background blob
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
                  // Main blob with J
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
            // Title
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
            // Subtitle
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
