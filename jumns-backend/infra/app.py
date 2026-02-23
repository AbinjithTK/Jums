"""CDK app entry point — synthesizes dev and prod stacks."""

import aws_cdk as cdk

from stacks.backend_stack import JumnsBackendStack

app = cdk.App()

JumnsBackendStack(
    app,
    "jumns-backend-dev",
    env=cdk.Environment(region="us-east-1"),
    stage="dev",
)

JumnsBackendStack(
    app,
    "jumns-backend-prod",
    env=cdk.Environment(region="us-east-1"),
    stage="prod",
)

app.synth()
