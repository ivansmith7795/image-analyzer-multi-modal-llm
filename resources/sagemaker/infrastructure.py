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
        self.llama_model_endpoint_config = sagemaker.CfnEndpointConfig(self, f"{constants.CDK_APP_NAME}-7B-image2text-end-config",
            production_variants=[sagemaker.CfnEndpointConfig.ProductionVariantProperty(
                initial_variant_weight=1,
                model_name=self.llama_model.model_name,
                variant_name=f"{constants.CDK_APP_NAME}-7B-image2text-var1",
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
            #   async_inference_config=sagemaker.CfnEndpointConfig.AsyncInferenceConfigProperty(
            #     output_config=sagemaker.CfnEndpointConfig.AsyncInferenceOutputConfigProperty(
            #         s3_failure_path=f's3://{s3_model_bucket_name}/logs',
            #         s3_output_path=f's3://{s3_model_bucket_name}/inference_output'
            #     ),

            #     # the properties below are optional
            #     client_config=sagemaker.CfnEndpointConfig.AsyncInferenceClientConfigProperty(
            #         max_concurrent_invocations_per_instance=2
            #     )
            # ),

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


        # # Image2Text Endpoint -- Autoscale
        # self.variant_name = f"{constants.CDK_APP_NAME}-7B-image2text-var14"

        # self.llama_model = sagemaker_alpha.Model(self, f"{constants.CDK_APP_NAME}-7B-image2text-var14",
          
        #     role=sagemaker_exection_role,
        #     model_name=f"{constants.CDK_APP_NAME}-7B-model-image2text-var14",
        #     containers =[sagemaker_alpha.ContainerDefinition(
        #         image=sagemaker_alpha.ContainerImage.from_ecr_repository(ecr_model_repository, ecr_model_image_tag),
        #         model_data=sagemaker_alpha.ModelData.from_bucket(bucket=s3_models_bucket, object_key='models/vision-model-7b-4bit.tar.gz')

        #     )],
        #     security_groups=[ec2.SecurityGroup.from_security_group_id(self, f"{constants.CDK_APP_NAME}-security-group", "sg-021feb8e91e399eac")],
        #     vpc=self.vpc,
        #     vpc_subnets=ec2.SubnetSelection(
        #         subnets=[ 
        #                     ec2.Subnet.from_subnet_id(self, f"{constants.CDK_APP_NAME}-subnet1", "subnet-077d5743bb28959e9"),
        #                     ec2.Subnet.from_subnet_id(self, f"{constants.CDK_APP_NAME}-subnet2", "subnet-01da66527fd102e95"),
        #                     ec2.Subnet.from_subnet_id(self, f"{constants.CDK_APP_NAME}-subnet3", "subnet-06f96304e57d580b0"),
        #                     ec2.Subnet.from_subnet_id(self, f"{constants.CDK_APP_NAME}-subnet4", "subnet-05ece8d685d9c1174")
        #                 ]
        #     )
        # )
        # self.llama_test_endpoint_config = sagemaker_alpha.EndpointConfig(self, f"{constants.CDK_APP_NAME}-7B-image2text-end-config",
        #     endpoint_config_name=f"{constants.CDK_APP_NAME}-7B-image2text-end-config",
        #     instance_production_variants=[sagemaker_alpha.InstanceProductionVariantProps(
        #         model=self.llama_model,
        #         variant_name=self.variant_name,
        #         initial_instance_count=4,
        #         instance_type= sagemaker_alpha.InstanceType.G5_XLARGE
        #     )
        #     ]
        # )

        # endpoint = sagemaker_alpha.Endpoint(self, f"{constants.CDK_APP_NAME}-7B-image2text-endpoint",
        #     endpoint_config=self.llama_test_endpoint_config, 
        #     endpoint_name=f"{constants.CDK_APP_NAME}-7B-image2text-endpoint"
        # )
        # production_variant = endpoint.find_instance_production_variant(self.variant_name)
        # instance_count = production_variant.auto_scale_instance_count(
        #     max_capacity=5
        # )
        # instance_count.scale_on_invocations("LimitRPS",
        #     max_requests_per_second=1
        # )
