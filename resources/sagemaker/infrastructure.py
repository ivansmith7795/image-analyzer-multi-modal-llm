import aws_cdk.aws_signer as signer
import aws_cdk.aws_sagemaker as sagemaker
import aws_cdk.aws_ecr as ecr
import aws_cdk.aws_ec2 as ec2
import aws_cdk.aws_iam as iam
import aws_cdk.aws_s3 as s3

import aws_cdk as cdk
import constants

from constructs import Construct

class SageMakerModels(Construct):
    def __init__(self, scope: Construct, id_: str, vpcid: str, sagemaker_exection_role_arn: str, sagemaker_exection_role: iam.IRole,   s3_model_bucket_name: str, ecr_model_image: str, ecr_model_image_tag: str, ecr_model_repository: ecr.IRepository, s3_models_bucket: s3.IBucket, **kwargs):
        super().__init__(scope, id_)

        self.vpc = ec2.Vpc.from_lookup(self, "VPC",
            vpc_id =vpcid
        )

        # Image2Text Endpoint
        self.llama_model = sagemaker.CfnModel(self, f"{constants.CDK_APP_NAME}-7B-image2text-model",
            execution_role_arn=sagemaker_exection_role_arn,
            enable_network_isolation=False,
            model_name=f"{constants.CDK_APP_NAME}-7B-image2text-model",
            primary_container=sagemaker.CfnModel.ContainerDefinitionProperty(
                image=ecr_model_image,
                image_config=sagemaker.CfnModel.ImageConfigProperty(
                    repository_access_mode="Platform"
                ),
                mode="SingleModel",
                model_data_url=f's3://{s3_model_bucket_name}/models/vision-model-7b-4bit.tar.gz'
            ),
            vpc_config=sagemaker.CfnModel.VpcConfigProperty(
                security_group_ids=["sg-05e37584f45adf768"],
                subnets=["subnet-027380b6088dfef9e", "subnet-0bdead50e27556216", "subnet-046747e9d4b88c083"]
            )
        )

        # Endpoint configuration
        self.llama_model_endpoint_config = sagemaker.CfnEndpointConfig(self, f"{constants.CDK_APP_NAME}-7B-image2text",
            production_variants=[sagemaker.CfnEndpointConfig.ProductionVariantProperty(
                initial_variant_weight=1,
                model_name=self.llama_model.model_name,
                variant_name=f"{constants.CDK_APP_NAME}-7B-image2text",
                container_startup_health_check_timeout_in_seconds=120,
                enable_ssm_access=False,
                initial_instance_count=1,
                instance_type="ml.g5.xlarge",
                managed_instance_scaling=sagemaker.CfnEndpointConfig.ManagedInstanceScalingProperty(
                    max_instance_count=3,
                    min_instance_count=1,
                    status="ENABLED"
                ),
                model_data_download_timeout_in_seconds=1800
            )],
         

            endpoint_config_name=f"{constants.CDK_APP_NAME}-7B-image2text-endpoint-config"
        )
        self.llama_model_endpoint_config.add_dependency(self.llama_model)

        # Endpoint
        self.llama_model_endpoint = sagemaker.CfnEndpoint(self, f"{constants.CDK_APP_NAME}-7B-image2text-endpoint",
            endpoint_config_name=self.llama_model_endpoint_config.attr_endpoint_config_name,
            endpoint_name=f"{constants.CDK_APP_NAME}-7B-image2text-endpoint-var1",
            retain_all_variant_properties=False,
            retain_deployment_config=False
        )
        self.llama_model_endpoint.add_dependency(self.llama_model_endpoint_config)


      