from multiprocessing.sharedctypes import Value
from unicodedata import name
import constants

from resources.s3.infrastructure import S3Buckets
from resources.ecr.infrastructure import ECRImages
from resources.iam.infrastructure import IAMRoles
from resources.sagemaker.infrastructure import SageMakerModels

from aws_cdk import (
    Stack, Stage
)

from constructs import Construct

class SolutionResources(Stage):

    def __init__(self, scope: Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)
        
        solution_infrastack = Stack(self, f"infrastructure", env=constants.CDK_ENV)
        s3 = S3Buckets(solution_infrastack, f"{constants.CDK_APP_NAME}-s3-buckets", constants.VPC_ID)
        ecr = ECRImages(solution_infrastack, f"{constants.CDK_APP_NAME}-ecr-images")
        iam = IAMRoles(solution_infrastack, f"{constants.CDK_APP_NAME}-iam-role", s3.s3_model_artifact_bucket.bucket_arn)
        sagemaker = SageMakerModels(solution_infrastack, f"{constants.CDK_APP_NAME}-sagemaker-models", constants.VPC_ID, iam.sagemaker_execution_role.role_arn, iam.sagemaker_execution_role, s3.s3_model_artifact_bucket.bucket_name, ecr.llama_model_endpoint_image.image_uri, ecr.llama_model_endpoint_image.image_tag, ecr.llama_model_endpoint_image.repository, s3.s3_model_artifact_bucket)

        #Dependencies for L1 constructs
        sagemaker.llama_model.node.add_dependency(iam.sagemaker_execution_role)
        