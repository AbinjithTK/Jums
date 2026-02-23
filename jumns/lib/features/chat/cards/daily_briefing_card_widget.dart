import 'dart:math' as math;
import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import '../../../core/models/agent_card.dart';
import '../../../core/theme/jumns_colors.dart';
import '../../../core/theme/charcoal_decorations.dart';

class DailyBriefingCardWidget extends StatelessWidget {
  final DailyBriefingCard card;
  final void Function(String action)? onAction;

  const DailyBriefingCardWidget({
    super.key,
    required this.card,
    this.onAction,
  });

  @override
  Widget build(BuildContext context) {
    return CharcoalCard(
      blobColor: JumnsColors.markerBlue,
      rotation: -1,
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Header
          Row(
            children: [
              const Icon(Icons.wb_sunny,
                  color: JumnsColors.charcoal, size: 18),
              const SizedBox(width: 8),
              Text('DAILY BRIEFING',
                  style: GoogleFonts.architectsDaughter(
                      color: JumnsColors.charcoal,
                      fontSize: 12,
                      fontWeight: FontWeight.w700,
                      letterSpacing: 1)),
            ],
          ),
          const SizedBox(height: 16),
          // Weather + Progress ring row
          Row(
            children: [
              SizedBox(
                width: 64,
                height: 64,
                child: CustomPaint(
                  painter: _ProgressRingPainter(card.goalProgress / 100),
                  child: Center(
                    child: Text('${card.goalProgress}%',
                        style: GoogleFonts.gloriaHallelujah(
                            color: JumnsColors.charcoal,
                            fontWeight: FontWeight.bold,
                            fontSize: 14)),
                  ),
                ),
              ),
              const SizedBox(width: 16),
              Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    children: [
                      Text(card.weather.icon,
                          style: const TextStyle(fontSize: 20)),
                      const SizedBox(width: 8),
                      Text(card.weather.temp,
                          style: GoogleFonts.gloriaHallelujah(
                              color: JumnsColors.charcoal,
                              fontSize: 18,
                              fontWeight: FontWeight.w600)),
                    ],
                  ),
                  Text(card.weather.condition,
                      style: GoogleFonts.architectsDaughter(
                          color: JumnsColors.ink.withAlpha(150),
                          fontSize: 13,
                          fontWeight: FontWeight.w700)),
                ],
              ),
            ],
          ),
          const SizedBox(height: 16),
          // Checklist with hand-drawn checkboxes
          ...card.planItems.map(
            (item) => Padding(
              padding: const EdgeInsets.symmetric(vertical: 4),
              child: Row(
                children: [
                  HandDrawnCheckbox(checked: item.done),
                  const SizedBox(width: 10),
                  Expanded(
                    child: Text(item.title,
                        style: GoogleFonts.architectsDaughter(
                            color: item.done
                                ? JumnsColors.ink.withAlpha(100)
                                : JumnsColors.charcoal,
                            fontSize: 15,
                            fontWeight: FontWeight.w700,
                            decoration: item.done
                                ? TextDecoration.lineThrough
                                : null)),
                  ),
                  Text(item.time,
                      style: GoogleFonts.architectsDaughter(
                          color: JumnsColors.ink.withAlpha(130),
                          fontSize: 12,
                          fontWeight: FontWeight.w700)),
                ],
              ),
            ),
          ),
          const SizedBox(height: 16),
          // Action buttons
          Row(
            children: card.actions.map((action) {
              final isPrimary = action == card.actions.first;
              return Padding(
                padding: const EdgeInsets.only(right: 8),
                child: isPrimary
                    ? ElevatedButton(
                        onPressed: () => onAction?.call(action),
                        style: ElevatedButton.styleFrom(
                          padding: const EdgeInsets.symmetric(
                              horizontal: 16, vertical: 8),
                          minimumSize: Size.zero,
                          tapTargetSize: MaterialTapTargetSize.shrinkWrap,
                        ),
                        child: Text(action,
                            style: const TextStyle(fontSize: 13)),
                      )
                    : OutlinedButton(
                        onPressed: () => onAction?.call(action),
                        style: OutlinedButton.styleFrom(
                          padding: const EdgeInsets.symmetric(
                              horizontal: 16, vertical: 8),
                          minimumSize: Size.zero,
                          tapTargetSize: MaterialTapTargetSize.shrinkWrap,
                        ),
                        child: Text(action,
                            style: const TextStyle(fontSize: 13)),
                      ),
              );
            }).toList(),
          ),
        ],
      ),
    );
  }
}

class _ProgressRingPainter extends CustomPainter {
  final double progress;
  _ProgressRingPainter(this.progress);

  @override
  void paint(Canvas canvas, Size size) {
    final center = Offset(size.width / 2, size.height / 2);
    final radius = size.width / 2 - 4;

    canvas.drawCircle(
      center,
      radius,
      Paint()
        ..color = JumnsColors.ink.withAlpha(60)
        ..style = PaintingStyle.stroke
        ..strokeWidth = 4,
    );

    canvas.drawArc(
      Rect.fromCircle(center: center, radius: radius),
      -math.pi / 2,
      2 * math.pi * progress,
      false,
      Paint()
        ..color = JumnsColors.mint
        ..style = PaintingStyle.stroke
        ..strokeWidth = 4
        ..strokeCap = StrokeCap.round,
    );
  }

  @override
  bool shouldRepaint(_ProgressRingPainter old) => old.progress != progress;
}
