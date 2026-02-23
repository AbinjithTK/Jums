import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:google_fonts/google_fonts.dart';
import '../../../core/theme/jumns_colors.dart';

/// Charcoal Sketch composer: wobbly input border, blob add button,
/// charcoal send button with blob shape.
class Composer extends StatefulWidget {
  final void Function(String text) onSend;
  final bool isDisabled;

  const Composer({super.key, required this.onSend, this.isDisabled = false});

  @override
  State<Composer> createState() => _ComposerState();
}

class _ComposerState extends State<Composer> {
  final _controller = TextEditingController();
  bool _hasText = false;

  @override
  void initState() {
    super.initState();
    _controller.addListener(() {
      final hasText = _controller.text.trim().isNotEmpty;
      if (hasText != _hasText) setState(() => _hasText = hasText);
    });
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  void _handleSend() {
    if (widget.isDisabled) return;
    final text = _controller.text.trim();
    if (text.isEmpty) return;
    widget.onSend(text);
    _controller.clear();
  }

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: EdgeInsets.only(
        left: 12,
        right: 12,
        top: 12,
        bottom: MediaQuery.of(context).padding.bottom + 12,
      ),
      decoration: BoxDecoration(
        color: JumnsColors.paper.withAlpha(240),
        border: const Border(
          top: BorderSide(
            color: JumnsColors.ink,
            width: 2,
            style: BorderStyle.solid,
          ),
        ),
      ),
      child: Transform.rotate(
        angle: 0.012, // ~0.7 degrees — subtle tilt like the Stitch design
        child: Container(
          padding: const EdgeInsets.all(6),
          decoration: BoxDecoration(
            color: JumnsColors.surface,
            border: Border.all(color: JumnsColors.ink, width: 2),
            borderRadius: const BorderRadius.only(
              topLeft: Radius.elliptical(20, 48),
              topRight: Radius.elliptical(48, 6),
              bottomLeft: Radius.elliptical(48, 6),
              bottomRight: Radius.elliptical(20, 42),
            ),
            boxShadow: const [
              BoxShadow(
                color: Color(0x18000000),
                offset: Offset(0, -2),
                blurRadius: 8,
              ),
            ],
          ),
          child: Row(
            children: [
              // Add button — blob shape with lavender tint
              GestureDetector(
                onTap: widget.isDisabled ? null : () {},
                child: Container(
                  width: 38,
                  height: 38,
                  decoration: BoxDecoration(
                    color: JumnsColors.lavender.withAlpha(80),
                    borderRadius: const BorderRadius.only(
                      topLeft: Radius.elliptical(64, 55),
                      topRight: Radius.elliptical(36, 58),
                      bottomLeft: Radius.elliptical(27, 42),
                      bottomRight: Radius.elliptical(73, 45),
                    ),
                    border: Border.all(color: JumnsColors.ink, width: 2),
                  ),
                  child: Icon(
                    Icons.add_rounded,
                    size: 20,
                    color: widget.isDisabled
                        ? JumnsColors.ink.withAlpha(80)
                        : JumnsColors.charcoal,
                  ),
                ),
              ),
              const SizedBox(width: 8),
              // Text field
              Expanded(
                child: TextField(
                  controller: _controller,
                  enabled: !widget.isDisabled,
                  style: GoogleFonts.architectsDaughter(
                    color: JumnsColors.charcoal,
                    fontSize: 15,
                    fontWeight: FontWeight.w700,
                  ),
                  decoration: InputDecoration(
                    hintText: widget.isDisabled
                        ? 'Sketching...'
                        : 'Ask anything...',
                    filled: false,
                    border: InputBorder.none,
                    enabledBorder: InputBorder.none,
                    focusedBorder: InputBorder.none,
                    contentPadding: const EdgeInsets.symmetric(
                      horizontal: 8,
                      vertical: 10,
                    ),
                    isDense: true,
                    hintStyle: GoogleFonts.architectsDaughter(
                      color: JumnsColors.ink.withAlpha(100),
                      fontWeight: FontWeight.w700,
                    ),
                  ),
                  textInputAction: TextInputAction.send,
                  onSubmitted: (_) => _handleSend(),
                ),
              ),
              const SizedBox(width: 4),
              // Mic button
              if (!_hasText)
                GestureDetector(
                  onTap: widget.isDisabled ? null : () {},
                  child: const SizedBox(
                    width: 38,
                    height: 38,
                    child: Icon(
                      Icons.mic_rounded,
                      color: JumnsColors.charcoal,
                      size: 22,
                    ),
                  ),
                ),
              // Send button — charcoal blob
              GestureDetector(
                onTap: widget.isDisabled
                    ? null
                    : () {
                        if (_hasText) {
                          _handleSend();
                        } else {
                          context.push('/voice');
                        }
                      },
                child: AnimatedContainer(
                  duration: const Duration(milliseconds: 200),
                  width: 40,
                  height: 40,
                  decoration: BoxDecoration(
                    color: _hasText
                        ? JumnsColors.charcoal
                        : Colors.transparent,
                    borderRadius: const BorderRadius.only(
                      topLeft: Radius.elliptical(64, 55),
                      topRight: Radius.elliptical(36, 58),
                      bottomLeft: Radius.elliptical(27, 42),
                      bottomRight: Radius.elliptical(73, 45),
                    ),
                    border: _hasText
                        ? null
                        : Border.all(color: Colors.transparent),
                  ),
                  child: Center(
                    child: Icon(
                      _hasText ? Icons.edit_rounded : Icons.edit_rounded,
                      color: _hasText
                          ? JumnsColors.paper
                          : JumnsColors.charcoal,
                      size: 18,
                    ),
                  ),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
