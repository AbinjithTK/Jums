import 'package:flutter/material.dart';
import '../../../core/models/agent_card.dart';
import 'daily_briefing_card_widget.dart';
import 'reminder_card_widget.dart';
import 'goal_checkin_card_widget.dart';
import 'journal_prompt_card_widget.dart';
import 'health_snapshot_card_widget.dart';
import 'insight_card_widget.dart';

class CardRenderer extends StatelessWidget {
  final AgentCard card;
  final void Function(String action)? onAction;

  const CardRenderer({super.key, required this.card, this.onAction});

  @override
  Widget build(BuildContext context) {
    return switch (card) {
      DailyBriefingCard c => DailyBriefingCardWidget(card: c, onAction: onAction),
      ReminderCard c => ReminderCardWidget(card: c, onAction: onAction),
      GoalCheckInCard c => GoalCheckInCardWidget(card: c, onAction: onAction),
      JournalPromptCard c => JournalPromptCardWidget(card: c, onAction: onAction),
      HealthSnapshotCard c => HealthSnapshotCardWidget(card: c, onAction: onAction),
      InsightCard c => InsightCardWidget(card: c),
    };
  }
}
