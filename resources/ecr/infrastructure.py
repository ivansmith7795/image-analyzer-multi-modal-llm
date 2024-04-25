from aws_cdk import aws_ecr_assets as ecr

import aws_cdk as cdk
import constants

from constructs import Construct

class ECRImages(Construct):
    def __init__(self, scope: Construct, id_: str,  **kwargs):
        super().__init__(scope, id_)

        self.llama_model_endpoint_image = ecr.DockerImageAsset(self, f"{constants.CDK_APP_NAME}-llama-ecr-image",
            directory="resources/ecr/runtime/vision_model",
            network_mode=ecr.NetworkMode.HOST
        )