"""EventBridge Scheduler construct for proactive agent behavior."""

from constructs import Construct

import aws_cdk as cdk
import aws_cdk.aws_events as events
import aws_cdk.aws_events_targets as targets
import aws_cdk.aws_lambda as _lambda


class SchedulingConstruct(Construct):
    """Creates EventBridge rules targeting the Scheduler Lambda."""

    def __init__(
        self,
        scope: Construct,
        id: str,
        scheduler_fn: _lambda.Function,
        stage: str,
    ) -> None:
        super().__init__(scope, id)

        # Morning briefing — hourly (Lambda filters by user timezone)
        events.Rule(
            self, "MorningBriefing",
            rule_name=f"jumns-morning-{stage}",
            schedule=events.Schedule.cron(minute="0"),
            targets=[targets.LambdaFunction(
                scheduler_fn,
                event=events.RuleTargetInput.from_object(
                    {"type": "morning_briefing"}
                ),
            )],
        )

        # Evening journal — hourly
        events.Rule(
            self, "EveningJournal",
            rule_name=f"jumns-evening-{stage}",
            schedule=events.Schedule.cron(minute="30"),
            targets=[targets.LambdaFunction(
                scheduler_fn,
                event=events.RuleTargetInput.from_object(
                    {"type": "evening_journal"}
                ),
            )],
        )

        # Reminder check — every 5 minutes
        events.Rule(
            self, "ReminderCheck",
            rule_name=f"jumns-reminders-{stage}",
            schedule=events.Schedule.rate(cdk.Duration.minutes(5)),
            targets=[targets.LambdaFunction(
                scheduler_fn,
                event=events.RuleTargetInput.from_object(
                    {"type": "reminder_check"}
                ),
            )],
        )
