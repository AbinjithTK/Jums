import 'dart:math' as math;
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:google_fonts/google_fonts.dart';
import '../../core/providers/auth_provider.dart';
import '../../core/providers/messages_provider.dart';
import '../../core/providers/subscription_provider.dart';
import '../../core/theme/jumns_colors.dart';
import '../../core/theme/charcoal_decorations.dart';

class SettingsScreen extends ConsumerWidget {
  const SettingsScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final authState = ref.watch(authNotifierProvider);
    final settingsAsync = ref.watch(userSettingsProvider);
    final sub = ref.watch(subscriptionNotifierProvider);

    final user = authState.user;
    final name = user?.name ??
        (user?.email != null ? user!.email.split('@').first : 'User');
    final isPro = sub.isPro;

    return SafeArea(
      child: ListView(
        padding: const EdgeInsets.symmetric(horizontal: 16),
        children: [
          // ── Header ──
          Padding(
            padding: const EdgeInsets.fromLTRB(8, 16, 8, 8),
            child: Transform.rotate(
              angle: -1 * math.pi / 180,
              child: Text('Settings',
                  style: GoogleFonts.gloriaHallelujah(
                      fontSize: 24,
                      fontWeight: FontWeight.bold,
                      color: JumnsColors.charcoal)),
            ),
          ),
          const DashedSeparator(),
          const SizedBox(height: 24),

          // ── Profile avatar with overlapping blobs ──
          Center(
            child: Column(
              children: [
                SizedBox(
                  width: 112,
                  height: 112,
                  child: Stack(
                    children: [
                      // Lavender blob behind
                      Positioned.fill(
                        child: Transform.rotate(
                          angle: 12 * math.pi / 180,
                          child: Transform.scale(
                            scale: 1.1,
                            child: Container(
                              decoration: BoxDecoration(
                                color: JumnsColors.lavender.withAlpha(150),
                                borderRadius: const BorderRadius.only(
                                  topLeft: Radius.elliptical(34, 49),
                                  topRight: Radius.elliptical(66, 62),
                                  bottomLeft: Radius.elliptical(70, 38),
                                  bottomRight: Radius.elliptical(30, 51),
                                ),
                              ),
                            ),
                          ),
                        ),
                      ),
                      // Mint blob behind
                      Positioned.fill(
                        child: Transform.rotate(
                          angle: -6 * math.pi / 180,
                          child: Transform.scale(
                            scale: 1.05,
                            child: Container(
                              decoration: BoxDecoration(
                                color: JumnsColors.mint.withAlpha(150),
                                borderRadius: const BorderRadius.only(
                                  topLeft: Radius.elliptical(64, 55),
                                  topRight: Radius.elliptical(36, 58),
                                  bottomLeft: Radius.elliptical(27, 42),
                                  bottomRight: Radius.elliptical(73, 45),
                                ),
                              ),
                            ),
                          ),
                        ),
                      ),
                      // Avatar circle
                      Positioned.fill(
                        child: Container(
                          decoration: BoxDecoration(
                            color: JumnsColors.paperDark,
                            borderRadius: const BorderRadius.only(
                              topLeft: Radius.elliptical(64, 55),
                              topRight: Radius.elliptical(36, 58),
                              bottomLeft: Radius.elliptical(27, 42),
                              bottomRight: Radius.elliptical(73, 45),
                            ),
                            border: Border.all(
                                color: JumnsColors.ink, width: 2),
                          ),
                          child: Center(
                            child: Text(
                              name.isNotEmpty
                                  ? name[0].toUpperCase()
                                  : 'U',
                              style: GoogleFonts.gloriaHallelujah(
                                  fontSize: 40,
                                  fontWeight: FontWeight.bold,
                                  color: JumnsColors.charcoal),
                            ),
                          ),
                        ),
                      ),
                      // Edit button
                      Positioned(
                        bottom: 0,
                        right: 0,
                        child: BlobShape(
                          color: JumnsColors.charcoal,
                          size: 32,
                          child: const Icon(Icons.edit,
                              color: JumnsColors.paper, size: 14),
                        ),
                      ),
                    ],
                  ),
                ),
                const SizedBox(height: 12),
                Text(name,
                    style: GoogleFonts.gloriaHallelujah(
                        fontSize: 22,
                        fontWeight: FontWeight.bold,
                        color: JumnsColors.charcoal)),
                Transform.rotate(
                  angle: -1 * math.pi / 180,
                  child: Text('Making life simpler',
                      style: GoogleFonts.architectsDaughter(
                          fontSize: 14,
                          fontWeight: FontWeight.w700,
                          color: JumnsColors.ink.withAlpha(130))),
                ),
              ],
            ),
          ),
          const SizedBox(height: 28),

          // ── Agent Configuration ──
          Transform.rotate(
            angle: 1 * math.pi / 180,
            child: Container(
              padding: const EdgeInsets.all(20),
              decoration: charcoalBorderDecoration(),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    children: [
                      const Icon(Icons.smart_toy,
                          color: JumnsColors.charcoal, size: 20),
                      const SizedBox(width: 8),
                      Text('Agent Configuration',
                          style: GoogleFonts.gloriaHallelujah(
                              fontSize: 18,
                              fontWeight: FontWeight.bold,
                              color: JumnsColors.charcoal)),
                    ],
                  ),
                  const SizedBox(height: 16),
                  settingsAsync.when(
                    loading: () => const Center(
                        child: CircularProgressIndicator()),
                    error: (_, __) => Text('Could not load settings',
                        style: GoogleFonts.architectsDaughter(
                            color: JumnsColors.ink)),
                    data: (settings) => Column(
                      children: [
                        // Model card
                        Container(
                          padding: const EdgeInsets.all(14),
                          decoration: BoxDecoration(
                            color: JumnsColors.mint.withAlpha(40),
                            borderRadius: const BorderRadius.only(
                              topLeft: Radius.elliptical(34, 49),
                              topRight: Radius.elliptical(66, 62),
                              bottomLeft: Radius.elliptical(70, 38),
                              bottomRight: Radius.elliptical(30, 51),
                            ),
                            border: Border.all(
                                color: JumnsColors.ink, width: 2),
                          ),
                          child: Row(
                            children: [
                              BlobShape(
                                color: JumnsColors.mint.withAlpha(180),
                                size: 40,
                                variant: 1,
                                child: const Icon(Icons.auto_awesome,
                                    color: JumnsColors.charcoal, size: 18),
                              ),
                              const SizedBox(width: 12),
                              Expanded(
                                child: Column(
                                  crossAxisAlignment:
                                      CrossAxisAlignment.start,
                                  children: [
                                    Text('Gemini 2.5 Flash',
                                        style: GoogleFonts.gloriaHallelujah(
                                            fontSize: 16,
                                            fontWeight: FontWeight.bold,
                                            color: JumnsColors.charcoal)),
                                    Text('Active model',
                                        style:
                                            GoogleFonts.architectsDaughter(
                                                fontSize: 12,
                                                fontWeight: FontWeight.w700,
                                                color: JumnsColors.ink
                                                    .withAlpha(130))),
                                  ],
                                ),
                              ),
                              Icon(Icons.swap_horiz,
                                  color: JumnsColors.ink.withAlpha(130),
                                  size: 20),
                            ],
                          ),
                        ),
                        const SizedBox(height: 12),
                        Row(
                          children: [
                            Expanded(
                              child: _ConfigTile(
                                icon: Icons.badge,
                                label: 'Name',
                                value: settings?.agentName ?? 'Jumns',
                              ),
                            ),
                            const SizedBox(width: 12),
                            Expanded(
                              child: _ConfigTile(
                                icon: Icons.psychology,
                                label: 'Personality',
                                value:
                                    settings?.personalityLabel ?? 'Friendly',
                              ),
                            ),
                          ],
                        ),
                      ],
                    ),
                  ),
                ],
              ),
            ),
          ),
          const SizedBox(height: 20),

          // ── Subscription ──
          Transform.rotate(
            angle: -1 * math.pi / 180,
            child: Container(
              padding: const EdgeInsets.all(20),
              decoration: charcoalBorderDecoration(),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    children: [
                      const Icon(Icons.loyalty,
                          color: JumnsColors.charcoal, size: 20),
                      const SizedBox(width: 8),
                      Text('Subscription',
                          style: GoogleFonts.gloriaHallelujah(
                              fontSize: 18,
                              fontWeight: FontWeight.bold,
                              color: JumnsColors.charcoal)),
                    ],
                  ),
                  const SizedBox(height: 16),
                  Container(
                    padding: const EdgeInsets.all(14),
                    decoration: BoxDecoration(
                      color: JumnsColors.lavender.withAlpha(50),
                      borderRadius: const BorderRadius.only(
                        topLeft: Radius.elliptical(34, 49),
                        topRight: Radius.elliptical(66, 62),
                        bottomLeft: Radius.elliptical(70, 38),
                        bottomRight: Radius.elliptical(30, 51),
                      ),
                      border: Border.all(color: JumnsColors.ink, width: 2),
                    ),
                    child: Row(
                      children: [
                        Transform.rotate(
                          angle: -3 * math.pi / 180,
                          child: BlobShape(
                            color: JumnsColors.lavender,
                            size: 40,
                            child: const Icon(Icons.star,
                                color: JumnsColors.charcoal, size: 20),
                          ),
                        ),
                        const SizedBox(width: 12),
                        Expanded(
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Text(
                                isPro ? 'Pro Status' : 'Free Plan',
                                style: GoogleFonts.gloriaHallelujah(
                                    fontSize: 18,
                                    fontWeight: FontWeight.bold,
                                    color: JumnsColors.charcoal),
                              ),
                              Text(
                                isPro ? 'Active' : 'Upgrade for more',
                                style: GoogleFonts.architectsDaughter(
                                    fontSize: 12,
                                    fontWeight: FontWeight.w700,
                                    color: JumnsColors.ink.withAlpha(150)),
                              ),
                            ],
                          ),
                        ),
                        if (isPro)
                          Transform.rotate(
                            angle: 6 * math.pi / 180,
                            child: BlobShape(
                              color: JumnsColors.mint,
                              size: 32,
                              child: const Icon(Icons.check,
                                  color: JumnsColors.charcoal, size: 18),
                            ),
                          )
                        else
                          ElevatedButton(
                            onPressed: () => context.push('/paywall'),
                            style: ElevatedButton.styleFrom(
                              padding: const EdgeInsets.symmetric(
                                  horizontal: 14, vertical: 8),
                              minimumSize: Size.zero,
                            ),
                            child: const Text('Upgrade'),
                          ),
                      ],
                    ),
                  ),
                ],
              ),
            ),
          ),
          const SizedBox(height: 20),

          // ── Data & Privacy ──
          Transform.rotate(
            angle: 0.5 * math.pi / 180,
            child: Container(
              padding: const EdgeInsets.all(20),
              decoration: charcoalBorderDecoration(),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    children: [
                      const Icon(Icons.shield,
                          color: JumnsColors.charcoal, size: 20),
                      const SizedBox(width: 8),
                      Text('Data & Privacy',
                          style: GoogleFonts.gloriaHallelujah(
                              fontSize: 18,
                              fontWeight: FontWeight.bold,
                              color: JumnsColors.charcoal)),
                    ],
                  ),
                  const SizedBox(height: 12),
                  _SettingsNavRow(
                      label: 'Privacy Policy', onTap: () {}),
                  const SizedBox(height: 8),
                  // Clear history — red ink smear
                  GestureDetector(
                    onTap: () => _showClearDialog(context, ref),
                    child: Container(
                      padding: const EdgeInsets.all(14),
                      decoration: BoxDecoration(
                        borderRadius: const BorderRadius.only(
                          topLeft: Radius.elliptical(64, 55),
                          topRight: Radius.elliptical(36, 58),
                          bottomLeft: Radius.elliptical(27, 42),
                          bottomRight: Radius.elliptical(73, 45),
                        ),
                        border: Border.all(
                            color: Colors.red.withAlpha(130),
                            width: 2,
                            style: BorderStyle.none),
                        gradient: LinearGradient(
                          colors: [
                            Colors.transparent,
                            JumnsColors.smearRed.withAlpha(100),
                            Colors.transparent,
                          ],
                          begin: Alignment.centerLeft,
                          end: Alignment.centerRight,
                        ),
                      ),
                      child: Row(
                        mainAxisAlignment: MainAxisAlignment.spaceBetween,
                        children: [
                          Text('Clear Conversation History',
                              style: GoogleFonts.architectsDaughter(
                                  fontSize: 15,
                                  fontWeight: FontWeight.w700,
                                  color: Colors.red.shade900)),
                          Icon(Icons.delete_sweep,
                              color: Colors.red.shade900, size: 20),
                        ],
                      ),
                    ),
                  ),
                ],
              ),
            ),
          ),
          const SizedBox(height: 20),

          // ── Appearance ──
          Transform.rotate(
            angle: -0.5 * math.pi / 180,
            child: Container(
              padding: const EdgeInsets.all(20),
              decoration: charcoalBorderDecoration(),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    children: [
                      const Icon(Icons.palette,
                          color: JumnsColors.charcoal, size: 20),
                      const SizedBox(width: 8),
                      Text('Appearance',
                          style: GoogleFonts.gloriaHallelujah(
                              fontSize: 18,
                              fontWeight: FontWeight.bold,
                              color: JumnsColors.charcoal)),
                    ],
                  ),
                  const SizedBox(height: 12),
                  _SettingsNavRow(
                      label: 'Theme',
                      trailing: 'Charcoal',
                      onTap: () {}),
                  const DashedSeparator(height: 1),
                  _SettingsNavRow(
                      label: 'Paper Texture',
                      trailing: 'Cream',
                      onTap: () {}),
                ],
              ),
            ),
          ),
          const SizedBox(height: 20),

          // ── Notifications ──
          Transform.rotate(
            angle: 0.8 * math.pi / 180,
            child: Container(
              padding: const EdgeInsets.all(20),
              decoration: charcoalBorderDecoration(),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    children: [
                      const Icon(Icons.notifications_active,
                          color: JumnsColors.charcoal, size: 20),
                      const SizedBox(width: 8),
                      Text('Notifications',
                          style: GoogleFonts.gloriaHallelujah(
                              fontSize: 18,
                              fontWeight: FontWeight.bold,
                              color: JumnsColors.charcoal)),
                    ],
                  ),
                  const SizedBox(height: 12),
                  _SettingsNavRow(
                      label: 'Daily Briefing',
                      trailing: '8:00 AM',
                      onTap: () {}),
                  const DashedSeparator(height: 1),
                  _SettingsNavRow(
                      label: 'Journal Prompt',
                      trailing: '9:00 PM',
                      onTap: () {}),
                  const DashedSeparator(height: 1),
                  _SettingsNavRow(
                      label: 'Reminders',
                      trailing: 'On',
                      onTap: () {}),
                ],
              ),
            ),
          ),
          const SizedBox(height: 32),

          // ── Sign Out button (red ink smear) ──
          GestureDetector(
            onTap: () {
              ref.read(authNotifierProvider.notifier).signOut();
              context.go('/login');
            },
            child: Container(
              padding: const EdgeInsets.symmetric(vertical: 16),
              decoration: BoxDecoration(
                color: JumnsColors.surface,
                borderRadius: const BorderRadius.only(
                  topLeft: Radius.elliptical(64, 55),
                  topRight: Radius.elliptical(36, 58),
                  bottomLeft: Radius.elliptical(27, 42),
                  bottomRight: Radius.elliptical(73, 45),
                ),
                border: Border.all(color: JumnsColors.ink, width: 2),
              ),
              child: Stack(
                children: [
                  // Red ink smear behind
                  Positioned.fill(
                    child: Container(
                      decoration: BoxDecoration(
                        gradient: LinearGradient(
                          colors: [
                            Colors.transparent,
                            JumnsColors.smearRed.withAlpha(130),
                            Colors.transparent,
                          ],
                          begin: Alignment.centerLeft,
                          end: Alignment.centerRight,
                        ),
                      ),
                    ),
                  ),
                  Center(
                    child: Row(
                      mainAxisSize: MainAxisSize.min,
                      children: [
                        const Icon(Icons.logout,
                            color: JumnsColors.charcoal, size: 20),
                        const SizedBox(width: 8),
                        Text('Sign Out',
                            style: GoogleFonts.gloriaHallelujah(
                                fontSize: 20,
                                fontWeight: FontWeight.bold,
                                color: JumnsColors.charcoal)),
                      ],
                    ),
                  ),
                ],
              ),
            ),
          ),
          const SizedBox(height: 20),

          // ── Footer ──
          Center(
            child: Column(
              children: [
                Text('Jumns v2.4 (Build 892)',
                    style: GoogleFonts.architectsDaughter(
                        fontSize: 12,
                        color: JumnsColors.ink.withAlpha(100))),
                const SizedBox(height: 4),
                Text('Made with charcoal & pixels',
                    style: GoogleFonts.architectsDaughter(
                        fontSize: 10,
                        color: JumnsColors.ink.withAlpha(80))),
              ],
            ),
          ),
          const SizedBox(height: 100),
        ],
      ),
    );
  }

  void _showClearDialog(BuildContext context, WidgetRef ref) {
    showDialog(
      context: context,
      builder: (ctx) => AlertDialog(
        title: Text('Clear History?',
            style: GoogleFonts.gloriaHallelujah(color: JumnsColors.charcoal)),
        content: Text(
          'This will permanently delete all conversation messages.',
          style: GoogleFonts.patrickHand(color: JumnsColors.ink),
        ),
        actions: [
          TextButton(
              onPressed: () => Navigator.pop(ctx),
              child: const Text('Cancel')),
          ElevatedButton(
            onPressed: () {
              ref.read(messagesNotifierProvider.notifier).clearAll();
              Navigator.pop(ctx);
            },
            style: ElevatedButton.styleFrom(
                backgroundColor: JumnsColors.error),
            child: const Text('Clear'),
          ),
        ],
      ),
    );
  }
}

// ─── Config tile (2-column grid in Agent Config) ───

class _ConfigTile extends StatelessWidget {
  final IconData icon;
  final String label;
  final String value;
  const _ConfigTile(
      {required this.icon, required this.label, required this.value});

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(14),
      decoration: BoxDecoration(
        color: JumnsColors.paperDark.withAlpha(80),
        borderRadius: BorderRadius.circular(12),
        border: Border.all(
            color: JumnsColors.ink.withAlpha(80),
            width: 2,
            style: BorderStyle.none),
      ),
      child: Column(
        children: [
          Icon(icon, color: JumnsColors.charcoal, size: 24),
          const SizedBox(height: 6),
          Text(label,
              style: GoogleFonts.architectsDaughter(
                  fontSize: 14,
                  fontWeight: FontWeight.w700,
                  color: JumnsColors.charcoal)),
          Text(value,
              style: GoogleFonts.architectsDaughter(
                  fontSize: 12,
                  fontWeight: FontWeight.w700,
                  color: JumnsColors.ink.withAlpha(130))),
        ],
      ),
    );
  }
}

// ─── Settings nav row with chevron ───

class _SettingsNavRow extends StatelessWidget {
  final String label;
  final String? trailing;
  final VoidCallback onTap;
  const _SettingsNavRow(
      {required this.label, this.trailing, required this.onTap});

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: onTap,
      child: Padding(
        padding: const EdgeInsets.symmetric(vertical: 10),
        child: Row(
          children: [
            Text(label,
                style: GoogleFonts.architectsDaughter(
                    fontSize: 17,
                    color: JumnsColors.charcoal)),
            const Spacer(),
            if (trailing != null)
              Text(trailing!,
                  style: GoogleFonts.architectsDaughter(
                      fontSize: 14,
                      color: JumnsColors.ink.withAlpha(130))),
            const SizedBox(width: 4),
            Icon(Icons.chevron_right,
                color: JumnsColors.ink.withAlpha(130), size: 20),
          ],
        ),
      ),
    );
  }
}
