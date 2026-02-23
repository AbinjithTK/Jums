import 'dart:math' as math;
import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import '../../core/theme/jumns_colors.dart';

class VoiceModeScreen extends StatefulWidget {
  const VoiceModeScreen({super.key});

  @override
  State<VoiceModeScreen> createState() => _VoiceModeScreenState();
}

class _VoiceModeScreenState extends State<VoiceModeScreen>
    with TickerProviderStateMixin {
  late final AnimationController _orbController;
  late final AnimationController _waveController;

  @override
  void initState() {
    super.initState();
    _orbController = AnimationController(
      vsync: this,
      duration: const Duration(seconds: 3),
    )..repeat();
    _waveController = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 1500),
    )..repeat();
  }

  @override
  void dispose() {
    _orbController.dispose();
    _waveController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: JumnsColors.charcoal,
      body: SafeArea(
        child: Column(
          children: [
            // Top bar
            Padding(
              padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
              child: Row(
                children: [
                  IconButton(
                    icon: const Icon(Icons.close, color: Colors.white70),
                    onPressed: () => Navigator.of(context).pop(),
                  ),
                  const Spacer(),
                  Container(
                    padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                    decoration: BoxDecoration(
                      color: JumnsColors.mint.withAlpha(40),
                      borderRadius: BorderRadius.circular(12),
                    ),
                    child: Row(
                      mainAxisSize: MainAxisSize.min,
                      children: [
                        Container(
                          width: 6, height: 6,
                          decoration: const BoxDecoration(
                              shape: BoxShape.circle, color: JumnsColors.mint),
                        ),
                        const SizedBox(width: 6),
                        Text('LISTENING',
                            style: GoogleFonts.architectsDaughter(
                                color: JumnsColors.mint,
                                fontSize: 11,
                                fontWeight: FontWeight.w700,
                                letterSpacing: 0.5)),
                      ],
                    ),
                  ),
                ],
              ),
            ),
            const Spacer(flex: 2),
            // User transcription
            Padding(
              padding: const EdgeInsets.symmetric(horizontal: 32),
              child: Text(
                '"What\'s on my schedule today?"',
                textAlign: TextAlign.center,
                style: GoogleFonts.gloriaHallelujah(
                  color: JumnsColors.paper,
                  fontSize: 22,
                  fontWeight: FontWeight.w300,
                ),
              ),
            ),
            const SizedBox(height: 40),
            // Animated orb
            SizedBox(
              width: 160,
              height: 160,
              child: AnimatedBuilder(
                animation: _orbController,
                builder: (context, child) {
                  return CustomPaint(
                    painter: _OrbPainter(_orbController.value),
                  );
                },
              ),
            ),
            const SizedBox(height: 24),
            Text('JUMNS',
                style: GoogleFonts.architectsDaughter(
                    color: JumnsColors.mint,
                    fontSize: 12,
                    fontWeight: FontWeight.w700,
                    letterSpacing: 1)),
            const SizedBox(height: 8),
            Padding(
              padding: const EdgeInsets.symmetric(horizontal: 40),
              child: Text(
                'You have 3 meetings today. The first one starts at 9:30 AM...',
                textAlign: TextAlign.center,
                style: GoogleFonts.patrickHand(
                    color: Colors.white60, fontSize: 15, height: 1.4),
              ),
            ),
            const Spacer(flex: 2),
            // Waveform
            SizedBox(
              height: 40,
              child: AnimatedBuilder(
                animation: _waveController,
                builder: (context, child) {
                  return CustomPaint(
                    size: Size(MediaQuery.of(context).size.width, 40),
                    painter: _WaveformPainter(_waveController.value),
                  );
                },
              ),
            ),
            const SizedBox(height: 24),
            // Controls
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceEvenly,
              children: [
                IconButton(
                  icon: const Icon(Icons.keyboard, color: Colors.white60, size: 28),
                  onPressed: () => Navigator.of(context).pop(),
                ),
                Container(
                  width: 64, height: 64,
                  decoration: const BoxDecoration(
                      shape: BoxShape.circle, color: JumnsColors.mint),
                  child: const Icon(Icons.mic,
                      color: JumnsColors.charcoal, size: 32),
                ),
                IconButton(
                  icon: const Icon(Icons.more_horiz, color: Colors.white60, size: 28),
                  onPressed: () {},
                ),
              ],
            ),
            const SizedBox(height: 8),
            Text('TAP TO INTERRUPT',
                style: GoogleFonts.architectsDaughter(
                    color: Colors.white38,
                    fontSize: 11,
                    letterSpacing: 0.5)),
            const SizedBox(height: 24),
          ],
        ),
      ),
    );
  }
}

class _OrbPainter extends CustomPainter {
  final double progress;
  _OrbPainter(this.progress);

  @override
  void paint(Canvas canvas, Size size) {
    final center = Offset(size.width / 2, size.height / 2);
    final radius = size.width / 2 - 10;

    // Glow
    canvas.drawCircle(
      center, radius + 15,
      Paint()
        ..color = JumnsColors.mint.withAlpha(20)
        ..maskFilter = const MaskFilter.blur(BlurStyle.normal, 20),
    );

    // Main orb
    canvas.drawCircle(
      center, radius,
      Paint()
        ..shader = RadialGradient(
          colors: [JumnsColors.mint.withAlpha(180), JumnsColors.mint.withAlpha(40)],
        ).createShader(Rect.fromCircle(center: center, radius: radius)),
    );

    // Orbiting dots
    for (var i = 0; i < 3; i++) {
      final angle = progress * 2 * math.pi + (i * 2 * math.pi / 3);
      final dotCenter = Offset(
        center.dx + (radius + 8) * math.cos(angle),
        center.dy + (radius + 8) * math.sin(angle),
      );
      canvas.drawCircle(dotCenter, 4, Paint()..color = JumnsColors.mint);
    }
  }

  @override
  bool shouldRepaint(_OrbPainter old) => true;
}

class _WaveformPainter extends CustomPainter {
  final double progress;
  _WaveformPainter(this.progress);

  @override
  void paint(Canvas canvas, Size size) {
    final barCount = 40;
    final barWidth = size.width / barCount - 2;
    final rng = math.Random(42);

    for (var i = 0; i < barCount; i++) {
      final baseHeight = rng.nextDouble() * 0.6 + 0.2;
      final wave = math.sin((i / barCount + progress) * 2 * math.pi) * 0.3 + 0.7;
      final height = baseHeight * wave * size.height;
      final x = i * (barWidth + 2);
      final y = (size.height - height) / 2;

      canvas.drawRRect(
        RRect.fromRectAndRadius(
            Rect.fromLTWH(x, y, barWidth, height),
            const Radius.circular(2)),
        Paint()..color = JumnsColors.mint.withAlpha((150 * wave).toInt()),
      );
    }
  }

  @override
  bool shouldRepaint(_WaveformPainter old) => true;
}
