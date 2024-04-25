import aws_cdk.aws_signer as signer
import aws_cdk.aws_s3 as s3

import aws_cdk as cdk
import constants

from constructs import Construct

class S3Buckets(Construct):
    def __init__(self, scope: Construct, id_: str, vpcid: str, **kwargs):
        super().__init__(scope, id_)

        self.s3_model_artifact_bucket = s3.Bucket(self, f"{constants.CDK_APP_NAME}-llm-vision-model-bucket",
            bucket_name=constants.S3_MODELS_BUCKET,
            block_public_access=s3.BlockPublicAccess.BLOCK_ALL,
            encryption=s3.BucketEncryption.S3_MANAGED,
            enforce_ssl=True,
            versioned=True,
            removal_policy=cdk.RemovalPolicy.DESTROY
        )
