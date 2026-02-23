import 'dart:math' as math;
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:google_fonts/google_fonts.dart';
import '../../core/providers/auth_provider.dart';
import '../../core/services/api_client.dart';
import '../../core/state/app_state.dart';
import '../../core/theme/jumns_colors.dart';
import '../../core/theme/charcoal_decorations.dart';

/// Personality onboarding — 3 steps:
///   1. Name your agent
///   2. Pick a personality
///   3. Confirm & go
class PersonalitySetupScreen extends ConsumerStatefulWidget {
  const PersonalitySetupScreen({super.key});

  @override
  ConsumerState<PersonalitySetupScreen> createState() =>
      _PersonalitySetupScreenState();
}

class _PersonalitySetupScreenState
    extends ConsumerState<PersonalitySetupScreen> {
  final _pageController = PageController();
  int _currentPage = 0;

  // Step 1: Agent name
  final _nameController = TextEditingController(text: 'Jumns');

  // Step 2: Personality
  String _selectedPersonality = 'friendly';

  bool _saving = false;

  static const _personalities = [
    (
      key: 'friendly',
      emoji: '😊',
      label: 'Friendly',
      desc: 'Warm, encouraging, celebrates your wins',
      color: JumnsColors.mint,
    ),
    (
      key: 'coach',
      emoji: '💪',
      label: 'Coach',
      desc: 'Motivating, pushes you to do better',
      color: JumnsColors.coral,
    ),
    (
      key: 'professional',
      emoji: '📋',
      label: 'Professional',
      desc: 'Clear, structured, no fluff',
      color: JumnsColors.markerBlue,
    ),
    (
      key: 'zen',
      emoji: '🧘',
      label: 'Zen',
      desc: 'Calm, mindful, reflective',
      color: JumnsColors.lavender,
    ),
    (
      key: 'creative',
      emoji: '✨',
      label: 'Creative',
      desc: 'Playful, quirky, makes tasks fun',
      color: JumnsColors.amber,
    ),
  ];

  @override
  void dispose() {
    _pageController.dispose();
    _nameController.dispose();
    super.dispose();
  }

  void _nextPage() {
    if (_currentPage < 2) {
      _pageController.nextPage(
        duration: const Duration(milliseconds: 300),
        curve: Curves.easeInOut,
      );
    }
  }

  void _prevPage() {
    if (_currentPage > 0) {
      _pageController.previousPage(
        duration: const Duration(milliseconds: 300),
        curve: Curves.easeInOut,
      );
    }
  }

  Future<void> _finish() async {
    setState(() => _saving = true);
    try {
      final api = ref.read(apiClientProvider);
      await api.post('/api/user-settings', body: {
        'agentName': _nameController.text.trim().isEmpty
            ? 'Jumns'
            : _nameController.text.trim(),
        'agentBehavior': _selectedPersonality,
        'onboardingCompleted': true,
      });
    } catch (_) {
      // Local server might not be running — that's fine, proceed anyway
    }
    if (!mounted) return;
    ref.read(appStateProvider.notifier).completeOnboarding();
    // After onboarding, go to login so user creates an account
    context.go('/login');
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: JumnsColors.paper,
      body: SafeArea(
        child: Column(
          children: [
            // Progress dots
            Padding(
              padding: const EdgeInsets.symmetric(vertical: 16),
              child: Row(
                mainAxisAlignment: MainAxisAlignment.center,
                children: List.generate(3, (i) {
                  final isActive = i == _currentPage;
                  final isDone = i < _currentPage;
                  return Padding(
                    padding: const EdgeInsets.symmetric(horizontal: 6),
                    child: AnimatedContainer(
                      duration: const Duration(milliseconds: 200),
                      width: isActive ? 28 : 10,
                      height: 10,
                      decoration: BoxDecoration(
                        color: isActive
                            ? JumnsColors.charcoal
                            : isDone
                                ? JumnsColors.mint
                                : JumnsColors.ink.withAlpha(60),
                        borderRadius: BorderRadius.circular(5),
                        border: Border.all(
                          color: JumnsColors.ink.withAlpha(100),
                          width: 1.5,
                        ),
                      ),
                    ),
                  );
                }),
              ),
            ),
            // Pages
            Expanded(
              child: PageView(
                controller: _pageController,
                physics: const NeverScrollableScrollPhysics(),
                onPageChanged: (i) => setState(() => _currentPage = i),
                children: [
                  _NamePage(
                    controller: _nameController,
                    onNext: _nextPage,
                  ),
                  _PersonalityPage(
                    selected: _selectedPersonality,
                    personalities: _personalities,
                    onSelect: (key) =>
                        setState(() => _selectedPersonality = key),
                    onNext: _nextPage,
                    onBack: _prevPage,
                  ),
                  _ConfirmPage(
                    name: _nameController.text,
                    personality: _selectedPersonality,
                    personalities: _personalities,
                    saving: _saving,
                    onFinish: _finish,
                    onBack: _prevPage,
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }
}


// ─── Step 1: Name your agent ───

class _NamePage extends StatelessWidget {
  final TextEditingController controller;
  final VoidCallback onNext;

  const _NamePage({required this.controller, required this.onNext});

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 32),
      child: Column(
        children: [
          const Spacer(flex: 2),
          // Big blob with pencil icon
          Stack(
            alignment: Alignment.center,
            children: [
              Transform.rotate(
                angle: 8 * math.pi / 180,
                child: Container(
                  width: 100,
                  height: 100,
                  decoration: BoxDecoration(
                    color: JumnsColors.lavender.withAlpha(120),
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
                color: JumnsColors.mint.withAlpha(180),
                size: 80,
                child: const Icon(Icons.edit, color: JumnsColors.charcoal, size: 36),
              ),
            ],
          ),
          const SizedBox(height: 24),
          Text(
            'Name your assistant',
            style: GoogleFonts.gloriaHallelujah(
              fontSize: 24,
              fontWeight: FontWeight.bold,
              color: JumnsColors.charcoal,
            ),
          ),
          const SizedBox(height: 8),
          Text(
            'Give it a name that feels right to you',
            style: GoogleFonts.architectsDaughter(
              fontSize: 14,
              fontWeight: FontWeight.w700,
              color: JumnsColors.ink.withAlpha(150),
            ),
          ),
          const SizedBox(height: 32),
          Container(
            decoration: charcoalBorderDecoration(),
            padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 4),
            child: TextField(
              controller: controller,
              textAlign: TextAlign.center,
              style: GoogleFonts.gloriaHallelujah(
                fontSize: 28,
                color: JumnsColors.charcoal,
              ),
              decoration: InputDecoration(
                border: InputBorder.none,
                hintText: 'Jumns',
                hintStyle: GoogleFonts.gloriaHallelujah(
                  fontSize: 28,
                  color: JumnsColors.ink.withAlpha(80),
                ),
              ),
            ),
          ),
          const Spacer(flex: 3),
          SizedBox(
            width: double.infinity,
            height: 52,
            child: ElevatedButton(
              onPressed: onNext,
              child: const Text('Next', style: TextStyle(fontSize: 17)),
            ),
          ),
          const SizedBox(height: 32),
        ],
      ),
    );
  }
}

// ─── Step 2: Pick a personality ───

class _PersonalityPage extends StatelessWidget {
  final String selected;
  final List<
      ({
        String key,
        String emoji,
        String label,
        String desc,
        Color color,
      })> personalities;
  final ValueChanged<String> onSelect;
  final VoidCallback onNext;
  final VoidCallback onBack;

  const _PersonalityPage({
    required this.selected,
    required this.personalities,
    required this.onSelect,
    required this.onNext,
    required this.onBack,
  });

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 24),
      child: Column(
        children: [
          const SizedBox(height: 8),
          Text(
            'Pick a vibe',
            style: GoogleFonts.gloriaHallelujah(
              fontSize: 24,
              fontWeight: FontWeight.bold,
              color: JumnsColors.charcoal,
            ),
          ),
          const SizedBox(height: 4),
          Text(
            'How should your assistant talk to you?',
            style: GoogleFonts.architectsDaughter(
              fontSize: 14,
              fontWeight: FontWeight.w700,
              color: JumnsColors.ink.withAlpha(150),
            ),
          ),
          const SizedBox(height: 20),
          Expanded(
            child: ListView.separated(
              itemCount: personalities.length,
              separatorBuilder: (_, __) => const SizedBox(height: 12),
              itemBuilder: (_, i) {
                final p = personalities[i];
                final isSelected = p.key == selected;
                return GestureDetector(
                  onTap: () => onSelect(p.key),
                  child: AnimatedContainer(
                    duration: const Duration(milliseconds: 200),
                    padding: const EdgeInsets.all(16),
                    decoration: BoxDecoration(
                      color: isSelected
                          ? p.color.withAlpha(60)
                          : JumnsColors.surface,
                      borderRadius: const BorderRadius.only(
                        topLeft: Radius.elliptical(34, 49),
                        topRight: Radius.elliptical(66, 62),
                        bottomLeft: Radius.elliptical(70, 38),
                        bottomRight: Radius.elliptical(30, 51),
                      ),
                      border: Border.all(
                        color: isSelected
                            ? JumnsColors.charcoal
                            : JumnsColors.ink.withAlpha(80),
                        width: isSelected ? 2.5 : 1.5,
                      ),
                    ),
                    child: Row(
                      children: [
                        BlobShape(
                          color: p.color.withAlpha(isSelected ? 200 : 120),
                          size: 48,
                          variant: i % 4,
                          child: Text(p.emoji,
                              style: const TextStyle(fontSize: 24)),
                        ),
                        const SizedBox(width: 14),
                        Expanded(
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Text(
                                p.label,
                                style: GoogleFonts.gloriaHallelujah(
                                  fontSize: 18,
                                  fontWeight: FontWeight.bold,
                                  color: JumnsColors.charcoal,
                                ),
                              ),
                              Text(
                                p.desc,
                                style: GoogleFonts.architectsDaughter(
                                  fontSize: 13,
                                  fontWeight: FontWeight.w700,
                                  color: JumnsColors.ink.withAlpha(150),
                                ),
                              ),
                            ],
                          ),
                        ),
                        if (isSelected)
                          const Icon(Icons.check_circle,
                              color: JumnsColors.charcoal, size: 24),
                      ],
                    ),
                  ),
                );
              },
            ),
          ),
          const SizedBox(height: 12),
          Row(
            children: [
              TextButton(
                onPressed: onBack,
                child: Text('Back',
                    style: GoogleFonts.architectsDaughter(
                        color: JumnsColors.ink, fontWeight: FontWeight.w700)),
              ),
              const Spacer(),
              SizedBox(
                width: 160,
                height: 48,
                child: ElevatedButton(
                  onPressed: onNext,
                  child: const Text('Next', style: TextStyle(fontSize: 16)),
                ),
              ),
            ],
          ),
          const SizedBox(height: 24),
        ],
      ),
    );
  }
}

// ─── Step 3: Confirm ───

class _ConfirmPage extends StatelessWidget {
  final String name;
  final String personality;
  final List<
      ({
        String key,
        String emoji,
        String label,
        String desc,
        Color color,
      })> personalities;
  final bool saving;
  final VoidCallback onFinish;
  final VoidCallback onBack;

  const _ConfirmPage({
    required this.name,
    required this.personality,
    required this.personalities,
    required this.saving,
    required this.onFinish,
    required this.onBack,
  });

  @override
  Widget build(BuildContext context) {
    final p = personalities.firstWhere((x) => x.key == personality,
        orElse: () => personalities.first);
    final displayName = name.trim().isEmpty ? 'Jumns' : name.trim();

    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 32),
      child: Column(
        children: [
          const Spacer(flex: 2),
          // Big avatar blob
          Stack(
            alignment: Alignment.center,
            children: [
              Transform.rotate(
                angle: -6 * math.pi / 180,
                child: Container(
                  width: 120,
                  height: 120,
                  decoration: BoxDecoration(
                    color: p.color.withAlpha(100),
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
                color: p.color.withAlpha(200),
                size: 90,
                child: Text(p.emoji, style: const TextStyle(fontSize: 44)),
              ),
            ],
          ),
          const SizedBox(height: 20),
          Text(
            'Meet $displayName',
            style: GoogleFonts.gloriaHallelujah(
              fontSize: 28,
              fontWeight: FontWeight.bold,
              color: JumnsColors.charcoal,
            ),
          ),
          const SizedBox(height: 8),
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 6),
            decoration: BoxDecoration(
              color: p.color.withAlpha(80),
              borderRadius: BorderRadius.circular(20),
              border: Border.all(color: JumnsColors.ink.withAlpha(80)),
            ),
            child: Text(
              '${p.emoji} ${p.label}',
              style: GoogleFonts.architectsDaughter(
                fontSize: 16,
                fontWeight: FontWeight.w700,
                color: JumnsColors.charcoal,
              ),
            ),
          ),
          const SizedBox(height: 16),
          Text(
            p.desc,
            textAlign: TextAlign.center,
            style: GoogleFonts.architectsDaughter(
              fontSize: 15,
              fontWeight: FontWeight.w700,
              color: JumnsColors.ink.withAlpha(180),
            ),
          ),
          const SizedBox(height: 24),
          Container(
            padding: const EdgeInsets.all(16),
            decoration: charcoalBorderDecoration(),
            child: Text(
              '"You can always change my personality later in Settings."',
              textAlign: TextAlign.center,
              style: GoogleFonts.patrickHand(
                fontSize: 14,
                color: JumnsColors.ink.withAlpha(150),
                fontStyle: FontStyle.italic,
              ),
            ),
          ),
          const Spacer(flex: 3),
          SizedBox(
            width: double.infinity,
            height: 52,
            child: ElevatedButton(
              onPressed: saving ? null : onFinish,
              child: saving
                  ? const SizedBox(
                      width: 20,
                      height: 20,
                      child: CircularProgressIndicator(
                        strokeWidth: 2,
                        color: JumnsColors.paper,
                      ),
                    )
                  : Text("Let's go!",
                      style: const TextStyle(fontSize: 17)),
            ),
          ),
          const SizedBox(height: 12),
          TextButton(
            onPressed: onBack,
            child: Text('Go back',
                style: GoogleFonts.architectsDaughter(
                    color: JumnsColors.ink, fontWeight: FontWeight.w700)),
          ),
          const SizedBox(height: 24),
        ],
      ),
    );
  }
}
