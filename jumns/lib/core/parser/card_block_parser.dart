import 'dart:convert';
import '../models/agent_card.dart';

/// A segment of a parsed message — either plain text or a card.
sealed class MessageSegment {
  const MessageSegment();
}

class TextSegment extends MessageSegment {
  final String content;
  const TextSegment(this.content);
}

class CardSegment extends MessageSegment {
  final AgentCard card;
  const CardSegment(this.card);
}

/// Parses agent messages containing :::card{type="..."}...:::  blocks.
class CardBlockParser {
  static final _cardBlockRegex = RegExp(
    r':::card\{type="(\w+)"\}\s*\n(.*?)\n:::',
    dotAll: true,
  );

  /// Parse a message string into ordered segments of text and cards.
  static List<MessageSegment> parse(String messageText) {
    final segments = <MessageSegment>[];
    var lastEnd = 0;

    for (final match in _cardBlockRegex.allMatches(messageText)) {
      // Text before this card block
      if (match.start > lastEnd) {
        final text = messageText.substring(lastEnd, match.start).trim();
        if (text.isNotEmpty) segments.add(TextSegment(text));
      }

      // Try to parse the card
      final cardType = match.group(1)!;
      final jsonPayload = match.group(2)!.trim();
      try {
        final json = jsonDecode(jsonPayload) as Map<String, dynamic>;
        json['type'] = cardType;
        final card = AgentCard.fromJson(json);
        if (card != null) {
          segments.add(CardSegment(card));
        } else {
          segments.add(TextSegment(jsonPayload));
        }
      } catch (_) {
        segments.add(TextSegment(jsonPayload));
      }

      lastEnd = match.end;
    }

    // Remaining text after last card block
    if (lastEnd < messageText.length) {
      final text = messageText.substring(lastEnd).trim();
      if (text.isNotEmpty) segments.add(TextSegment(text));
    }

    // No card blocks found — return entire message as text
    if (segments.isEmpty && messageText.trim().isNotEmpty) {
      segments.add(TextSegment(messageText.trim()));
    }

    return segments;
  }

  /// Format a card back into a card block string.
  static String format(AgentCard card) {
    final json = const JsonEncoder.withIndent('  ').convert(card.toJson()..remove('type'));
    return ':::card{type="${card.type}"}\n$json\n:::';
  }
}
