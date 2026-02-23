import 'dart:math' as math;
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:shared_preferences/shared_preferences.dart';
import '../../core/state/app_state.dart';
import '../../core/providers/auth_provider.dart';
import '../../core/theme/jumns_colors.dart';
import '../../core/theme/charcoal_decorations.dart';

class WelcomeScreen extends ConsumerWidget {
  const WelcomeScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    return Scaffold(
      backgroundColor: JumnsColors.paper,
      body: SafeArea(
        child: Padding(
          padding: const EdgeInsets.symmetric(horizontal: 32),
          child: Column(
            children: [
              const Spacer(flex: 2),
              // Logo blob
              Stack(
                alignment: Alignment.center,
                children: [
                  Transform.rotate(
                    angle: 8 * math.pi / 180,
                    child: Container(
                      width: 120,
                      height: 120,
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
                  BlobShape(
                    color: JumnsColors.lavender,
                    size: 100,
                    child: Text('J',
                        style: GoogleFonts.gloriaHallelujah(
                            color: JumnsColors.charcoal,
                            fontSize: 48,
                            fontWeight: FontWeight.bold)),
                  ),
                ],
              ),
              const SizedBox(height: 24),
              Text('Jumns',
                  style: GoogleFonts.gloriaHallelujah(
                      color: JumnsColors.charcoal,
                      fontSize: 36,
                      fontWeight: FontWeight.bold)),
              const SizedBox(height: 8),
              Text('YOUR AI LIFE ASSISTANT',
                  style: GoogleFonts.architectsDaughter(
                      color: JumnsColors.ink.withAlpha(150),
                      fontSize: 13,
                      fontWeight: FontWeight.w700,
                      letterSpacing: 2)),
              const Spacer(),
              // Feature rows
              _FeatureRow(
                icon: Icons.chat_bubble_outline,
                title: 'Smart Conversations',
                description: 'AI-powered assistant that understands your life context',
                color: JumnsColors.markerBlue,
              ),
              const SizedBox(height: 20),
              _FeatureRow(
                icon: Icons.track_changes,
                title: 'Goal Tracking',
                description: 'Set goals, track progress, and build streaks',
                color: JumnsColors.mint,
              ),
              const SizedBox(height: 20),
              _FeatureRow(
                icon: Icons.extension,
                title: 'Extensible Toolkit',
                description: 'Connect MCP servers, agents, and skills',
                color: JumnsColors.lavender,
              ),
              const Spacer(),
              // CTA — go to personality setup
              SizedBox(
                width: double.infinity,
                height: 52,
                child: ElevatedButton(
                  onPressed: () => context.go('/personality-setup'),
                  child: const Text('Get Started', style: TextStyle(fontSize: 17)),
                ),
              ),
              const SizedBox(height: 16),
              Row(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  Text('Already have an account? ',
                      style: GoogleFonts.architectsDaughter(
                          color: JumnsColors.ink.withAlpha(150), fontSize: 14)),
                  GestureDetector(
                    onTap: () => context.go('/login'),
                    child: Text('Sign In',
                        style: GoogleFonts.architectsDaughter(
                            color: JumnsColors.charcoal,
                            fontSize: 14,
                            fontWeight: FontWeight.w700,
                            decoration: TextDecoration.underline)),
                  ),
                ],
              ),
              const SizedBox(height: 8),
              GestureDetector(
                onTap: () async {
                  final prefs = await SharedPreferences.getInstance();
                  await prefs.setBool('demo_mode', true);
                  ref.read(appStateProvider.notifier).completeOnboarding();
                  ref.read(demoModeProvider.notifier).state = true;
                  if (context.mounted) context.go('/chat');
                },
                child: Text('Skip for now',
                    style: GoogleFonts.architectsDaughter(
                        color: JumnsColors.ink.withAlpha(120),
                        fontSize: 13,
                        decoration: TextDecoration.underline)),
              ),
              const SizedBox(height: 16),
              Row(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  TextButton(
                    onPressed: () {},
                    child: Text('Privacy Policy',
                        style: GoogleFonts.architectsDaughter(
                            color: JumnsColors.ink.withAlpha(100), fontSize: 11)),
                  ),
                  Text('·', style: TextStyle(color: JumnsColors.ink.withAlpha(100))),
                  TextButton(
                    onPressed: () {},
                    child: Text('Terms of Service',
                        style: GoogleFonts.architectsDaughter(
                            color: JumnsColors.ink.withAlpha(100), fontSize: 11)),
                  ),
                ],
              ),
              const SizedBox(height: 8),
            ],
          ),
        ),
      ),
    );
  }
}

class _FeatureRow extends StatelessWidget {
  final IconData icon;
  final String title;
  final String description;
  final Color color;

  const _FeatureRow({
    required this.icon,
    required this.title,
    required this.description,
    required this.color,
  });

  @override
  Widget build(BuildContext context) {
    return Row(
      children: [
        BlobShape(
          color: color.withAlpha(130),
          size: 44,
          child: Icon(icon, color: JumnsColors.charcoal, size: 22),
        ),
        const SizedBox(width: 16),
        Expanded(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(title,
                  style: GoogleFonts.architectsDaughter(
                      color: JumnsColors.charcoal,
                      fontSize: 15,
                      fontWeight: FontWeight.w700)),
              const SizedBox(height: 2),
              Text(description,
                  style: GoogleFonts.patrickHand(
                      color: JumnsColors.ink.withAlpha(150), fontSize: 13)),
            ],
          ),
        ),
      ],
    );
  }
}
