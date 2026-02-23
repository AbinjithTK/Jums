"""S3 memory storage construct for vector memory (replaces OpenSearch Serverless)."""

from constructs import Construct

import aws_cdk as cdk
import aws_cdk.aws_s3 as s3


class VectorStoreConstruct(Construct):
    """Creates S3 bucket for per-user memory JSON files + faiss-cpu indexes."""

    def __init__(self, scope: Construct, id: str, stage: str) -> None:
        super().__init__(scope, id)

        removal = cdk.RemovalPolicy.DESTROY if stage == "dev" else cdk.RemovalPolicy.RETAIN

        self.bucket = s3.Bucket(
            self,
            "MemoriesBucket",
            bucket_name=f"jumns-memories-{stage}",
            encryption=s3.BucketEncryption.S3_MANAGED,
            block_public_access=s3.BlockPublicAccess.BLOCK_ALL,
            versioned=False,
            removal_policy=removal,
            auto_delete_objects=(stage == "dev"),
        )

        # Lifecycle: move cold memories to Infrequent Access after 90 days
        self.bucket.add_lifecycle_rule(
            id="ColdMemoryTransition",
            prefix="memories/",
            transitions=[
                s3.Transition(
                    storage_class=s3.StorageClass.INFREQUENT_ACCESS,
                    transition_after=cdk.Duration.days(90),
                )
            ],
        )
