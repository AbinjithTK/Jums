import 'dart:math' as math;
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:google_fonts/google_fonts.dart';
import '../../core/models/goal.dart';
import '../../core/providers/goals_provider.dart';
import '../../core/theme/jumns_colors.dart';
import '../../core/theme/charcoal_decorations.dart';

class GoalsScreen extends ConsumerWidget {
  const GoalsScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final goalsAsync = ref.watch(goalsNotifierProvider);

    return SafeArea(
      child: RefreshIndicator(
        onRefresh: () => ref.read(goalsNotifierProvider.notifier).load(),
        child: CustomScrollView(
          slivers: [
            // ── Header ──
            SliverToBoxAdapter(
              child: Padding(
                padding: const EdgeInsets.fromLTRB(24, 16, 24, 8),
                child: Row(
                  children: [
                    Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Transform.rotate(
                          angle: -1 * math.pi / 180,
                          child: Text('My Goals',
                              style: GoogleFonts.gloriaHallelujah(
                                  fontSize: 28,
                                  fontWeight: FontWeight.bold,
                                  color: JumnsColors.charcoal)),
                        ),
                        Transform.rotate(
                          angle: 1 * math.pi / 180,
                          child: Text('Focus on what matters',
                              style: GoogleFonts.architectsDaughter(
                                  fontSize: 14,
                                  fontWeight: FontWeight.w700,
                                  color: JumnsColors.ink.withAlpha(130))),
                        ),
                      ],
                    ),
                    const Spacer(),
                    GestureDetector(
                      onTap: () => _showAddGoalDialog(context, ref),
                      child: BlobShape(
                        color: JumnsColors.surface,
                        size: 40,
                        child: const Icon(Icons.add,
                            color: JumnsColors.charcoal, size: 22),
                      ),
                    ),
                  ],
                ),
              ),
            ),

            const SliverToBoxAdapter(
              child: Padding(
                padding: EdgeInsets.symmetric(horizontal: 24),
                child: DashedSeparator(),
              ),
            ),

            // ── Active Goals section ──
            SliverToBoxAdapter(
              child: Padding(
                padding: const EdgeInsets.fromLTRB(24, 20, 24, 12),
                child: CharcoalSectionHeader(
                  title: 'Active Goals',
                  trailing: goalsAsync.whenOrNull(
                    data: (g) => '${g.where((x) => !x.completed).length} In Progress',
                  ),
                ),
              ),
            ),

            // ── Goal cards ──
            SliverToBoxAdapter(
              child: goalsAsync.when(
                loading: () => const Center(
                    child: Padding(
                        padding: EdgeInsets.all(40),
                        child: CircularProgressIndicator())),
                error: (_, __) => Padding(
                  padding: const EdgeInsets.all(20),
                  child: Center(
                    child: Text('Could not load goals',
                        style: GoogleFonts.architectsDaughter(
                            color: JumnsColors.ink.withAlpha(130),
                            fontSize: 16,
                            fontWeight: FontWeight.w700)),
                  ),
                ),
                data: (goals) {
                  final active = goals.where((g) => !g.completed).toList();
                  if (active.isEmpty) {
                    return Padding(
                      padding: const EdgeInsets.all(40),
                      child: Center(
                        child: Text('No active goals yet',
                            style: GoogleFonts.architectsDaughter(
                                color: JumnsColors.ink.withAlpha(130),
                                fontSize: 16,
                                fontWeight: FontWeight.w700)),
                      ),
                    );
                  }
                  return Padding(
                    padding: const EdgeInsets.symmetric(horizontal: 12),
                    child: Column(
                      children: active.indexed.map((e) {
                        final (i, goal) = e;
                        return _GoalCard(goal: goal, index: i);
                      }).toList(),
                    ),
                  );
                },
              ),
            ),

            // ── Weekly Progress section ──
            SliverToBoxAdapter(
              child: Padding(
                padding: const EdgeInsets.fromLTRB(24, 28, 24, 12),
                child: CharcoalSectionHeader(
                  title: 'Weekly Progress',
                  rotation: 1,
                ),
              ),
            ),

            SliverToBoxAdapter(
              child: Padding(
                padding: const EdgeInsets.symmetric(horizontal: 16),
                child: _WeeklyProgressChart(),
              ),
            ),

            const SliverToBoxAdapter(child: SizedBox(height: 100)),
          ],
        ),
      ),
    );
  }

  void _showAddGoalDialog(BuildContext context, WidgetRef ref) {
    final titleCtrl = TextEditingController();
    final categoryCtrl = TextEditingController();
    showDialog(
      context: context,
      builder: (ctx) => AlertDialog(
        title: Text('New Goal',
            style: GoogleFonts.gloriaHallelujah(color: JumnsColors.charcoal)),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            TextField(
              controller: titleCtrl,
              decoration: const InputDecoration(labelText: 'Title'),
            ),
            const SizedBox(height: 8),
            TextField(
              controller: categoryCtrl,
              decoration:
                  const InputDecoration(labelText: 'Category (e.g. Health)'),
            ),
          ],
        ),
        actions: [
          TextButton(
              onPressed: () => Navigator.pop(ctx),
              child: const Text('Cancel')),
          ElevatedButton(
            onPressed: () {
              if (titleCtrl.text.isNotEmpty) {
                ref.read(goalsNotifierProvider.notifier).create(
                      title: titleCtrl.text,
                      category: categoryCtrl.text.isEmpty
                          ? 'General'
                          : categoryCtrl.text,
                    );
                Navigator.pop(ctx);
              }
            },
            child: const Text('Create'),
          ),
        ],
      ),
    );
  }
}

// ─── Goal Card with blob behind + charcoal border ───

class _GoalCard extends StatelessWidget {
  final Goal goal;
  final int index;
  const _GoalCard({required this.goal, required this.index});

  static const _blobColors = [
    JumnsColors.mint,
    JumnsColors.markerBlue,
    JumnsColors.amber,
    JumnsColors.lavender,
    JumnsColors.coral,
  ];

  @override
  Widget build(BuildContext context) {
    final blobColor = _blobColors[index % _blobColors.length];
    final rotation = index.isEven ? -1.0 : 1.0;

    return CharcoalCard(
      blobColor: blobColor,
      rotation: rotation,
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              BlobShape(
                color: blobColor.withAlpha(130),
                size: 40,
                variant: index % 4,
                child: Text(goal.categoryEmoji,
                    style: const TextStyle(fontSize: 20)),
              ),
              if (goal.priority != null)
                Container(
                  padding: const EdgeInsets.symmetric(
                      horizontal: 8, vertical: 4),
                  decoration: BoxDecoration(
                    color: JumnsColors.charcoal,
                    borderRadius: BorderRadius.circular(12),
                  ),
                  child: Text(goal.priority!,
                      style: GoogleFonts.architectsDaughter(
                          fontSize: 11,
                          fontWeight: FontWeight.w700,
                          color: JumnsColors.paper)),
                ),
            ],
          ),
          const SizedBox(height: 12),
          Text(goal.title,
              style: GoogleFonts.gloriaHallelujah(
                  fontSize: 20,
                  fontWeight: FontWeight.bold,
                  color: JumnsColors.charcoal)),
          const SizedBox(height: 4),
          Text(goal.progressText,
              style: GoogleFonts.architectsDaughter(
                  fontSize: 14,
                  fontWeight: FontWeight.w700,
                  color: JumnsColors.ink.withAlpha(150))),
          const SizedBox(height: 14),
          CharcoalProgressBar(
            progress: goal.progressFraction,
            fillColor: blobColor,
          ),
          const SizedBox(height: 8),
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Text('${goal.progress}%',
                  style: GoogleFonts.architectsDaughter(
                      fontSize: 12,
                      fontWeight: FontWeight.w700,
                      color: JumnsColors.charcoal)),
              if (goal.streakDays > 0)
                Text('${goal.streakDays} days streak!',
                    style: GoogleFonts.architectsDaughter(
                        fontSize: 12,
                        fontWeight: FontWeight.w700,
                        color: JumnsColors.charcoal)),
            ],
          ),
        ],
      ),
    );
  }
}

// ─── Weekly Progress Chart (real data from API) ───

class _WeeklyProgressChart extends ConsumerWidget {
  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final progressAsync = ref.watch(weeklyProgressProvider);

    return progressAsync.when(
      loading: () => Container(
        height: 200,
        padding: const EdgeInsets.all(16),
        decoration: charcoalBorderDecoration(fill: JumnsColors.paper),
        child: const Center(child: CircularProgressIndicator()),
      ),
      error: (_, __) => Container(
        height: 200,
        padding: const EdgeInsets.all(16),
        decoration: charcoalBorderDecoration(fill: JumnsColors.paper),
        child: Center(
          child: Text('Could not load progress',
              style: GoogleFonts.architectsDaughter(
                  color: JumnsColors.ink.withAlpha(130),
                  fontSize: 14,
                  fontWeight: FontWeight.w700)),
        ),
      ),
      data: (wp) => _buildChart(wp),
    );
  }

  Widget _buildChart(WeeklyProgress wp) {
    const days = ['M', 'T', 'W', 'T', 'F', 'S', 'S'];
    final maxCount = wp.counts.reduce((a, b) => a > b ? a : b);

    return Container(
      padding: const EdgeInsets.all(16),
      decoration: charcoalBorderDecoration(fill: JumnsColors.paper),
      child: Column(
        children: [
          SizedBox(
            height: 130,
            child: Row(
              crossAxisAlignment: CrossAxisAlignment.end,
              children: List.generate(7, (i) {
                final isBest = i == wp.bestDay && wp.total > 0;
                final heightFactor =
                    maxCount > 0 ? wp.counts[i] / maxCount : 0.0;

                return Expanded(
                  child: Padding(
                    padding: const EdgeInsets.symmetric(horizontal: 4),
                    child: Column(
                      mainAxisAlignment: MainAxisAlignment.end,
                      children: [
                        if (isBest)
                          Container(
                            padding: const EdgeInsets.symmetric(
                                horizontal: 6, vertical: 2),
                            decoration: BoxDecoration(
                              color: JumnsColors.charcoal,
                              borderRadius: BorderRadius.circular(4),
                            ),
                            child: Text('Best!',
                                style: GoogleFonts.architectsDaughter(
                                    fontSize: 10,
                                    fontWeight: FontWeight.w700,
                                    color: JumnsColors.paper)),
                          ),
                        if (isBest) const SizedBox(height: 4),
                        if (wp.counts[i] > 0)
                          Padding(
                            padding: const EdgeInsets.only(bottom: 2),
                            child: Text('${wp.counts[i]}',
                                style: GoogleFonts.gloriaHallelujah(
                                    fontSize: 10,
                                    color: JumnsColors.charcoal)),
                          ),
                        Flexible(
                          child: FractionallySizedBox(
                            heightFactor: heightFactor.clamp(0.0, 1.0),
                            child: Container(
                              decoration: BoxDecoration(
                                color: isBest
                                    ? JumnsColors.mint
                                    : JumnsColors.lavender.withAlpha(130),
                                borderRadius: BorderRadius.circular(6),
                                border: Border.all(
                                    color: JumnsColors.ink, width: 2),
                                boxShadow: isBest
                                    ? const [
                                        BoxShadow(
                                          color: JumnsColors.borderShadow,
                                          offset: Offset(2, 2),
                                        )
                                      ]
                                    : null,
                              ),
                            ),
                          ),
                        ),
                        const SizedBox(height: 4),
                        Text(days[i],
                            style: GoogleFonts.architectsDaughter(
                                fontSize: 12,
                                fontWeight: FontWeight.w700,
                                color: JumnsColors.ink)),
                      ],
                    ),
                  ),
                );
              }),
            ),
          ),
          const SizedBox(height: 4),
          const DashedSeparator(),
          const SizedBox(height: 10),
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              RichText(
                text: TextSpan(
                  style: GoogleFonts.architectsDaughter(
                      fontSize: 14,
                      fontWeight: FontWeight.w700,
                      color: JumnsColors.ink.withAlpha(150)),
                  children: [
                    const TextSpan(text: 'Total tasks: '),
                    TextSpan(
                      text: '${wp.total}',
                      style: GoogleFonts.gloriaHallelujah(
                          fontSize: 18, color: JumnsColors.charcoal),
                    ),
                  ],
                ),
              ),
              Text('View Report',
                  style: GoogleFonts.architectsDaughter(
                      fontSize: 12,
                      fontWeight: FontWeight.w700,
                      color: JumnsColors.charcoal,
                      decoration: TextDecoration.underline)),
            ],
          ),
        ],
      ),
    );
  }
}
