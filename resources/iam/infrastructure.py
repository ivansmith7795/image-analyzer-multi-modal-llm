import aws_cdk.aws_signer as signer
import aws_cdk.aws_iam as iam

import aws_cdk as cdk
import constants

from constructs import Construct

class IAMRoles(Construct):
    def __init__(self, scope: Construct, id_: str, s3_model_bucket_arn: str,  **kwargs):
        super().__init__(scope, id_)

        self.sagemaker_execution_role = iam.Role(self, f"{constants.CDK_APP_NAME}-sagemaker-execution-role",
            role_name=f"{constants.CDK_APP_NAME}-sagemaker-execution-role",
            assumed_by=iam.AccountRootPrincipal(),
            description="Role for model endpoint hosting via sagemaker"
        )
       
        sagemaker_iam_policy = self.sagemaker_execution_role.assume_role_policy
        sagemaker_iam_policy.add_statements(
            iam.PolicyStatement(
                actions=["sts:AssumeRole"],
                effect=iam.Effect.ALLOW,
                principals=[
                    iam.ServicePrincipal("sagemaker.amazonaws.com")
                ]
            )
        )

        self.sagemaker_execution_role.add_to_policy(
            iam.PolicyStatement( 
                actions=[
                    "s3:Get*", 
                    "s3:List*", 
                    "s3:Put*", 
                    "s3:DeleteObject*",  
                    "s3:Abort*"
                    ],
                resources=[
                    s3_model_bucket_arn +'/*',
                    s3_model_bucket_arn
                ])
            )

        self.sagemaker_execution_role.add_to_policy(
            iam.PolicyStatement( 
                actions=[
                    "sagemaker:*", 
                    "cloudwatch:PutMetricData", 
                    "logs:CreateLogGroup", 
                    "logs:CreateLogStream", 
                    "logs:DescribeLogStreams", 
                    "logs:PutLogEvents"
                    ],
                resources=["*"])
            )
        
        self.sagemaker_execution_role.add_to_policy(
            iam.PolicyStatement( 
                actions=[
                        "ecr:BatchGetImage",
                        "ecr:BatchCheckLayerAvailability",
                        "ecr:CompleteLayerUpload",
                        "ecr:GetDownloadUrlForLayer",
                        "ecr:InitiateLayerUpload",
                        "ecr:PutImage",
                        "ecr:UploadLayerPart"
                        ],
                resources=["*"])
            )
        
        self.sagemaker_execution_role.add_to_policy(
            iam.PolicyStatement( 
                actions=[
                        "cloudformation:GetTemplateSummary",
                        "cloudwatch:DeleteAlarms",
                        "cloudwatch:DescribeAlarms",
                        "cloudwatch:GetMetricData",
                        "cloudwatch:GetMetricStatistics",
                        "cloudwatch:ListMetrics",
                        "cloudwatch:PutMetricAlarm",
                        "cloudwatch:PutMetricData",
                        "logs:CreateLogDelivery",
                        "logs:CreateLogGroup",
                        "logs:CreateLogStream",
                        "logs:DeleteLogDelivery",
                        "logs:Describe*",
                        "logs:GetLogDelivery",
                        "logs:GetLogEvents",
                        "logs:ListLogDeliveries",
                        "logs:PutLogEvents",
                        "logs:PutResourcePolicy",
                        "logs:UpdateLogDelivery",
                        "ec2:CreateNetworkInterface",
                        "ec2:DescribeNetworkInterfaces",
                        "ec2:DeleteNetworkInterface",
                        "ec2:AssignPrivateIpAddresses",
                        "ec2:UnassignPrivateIpAddresses",
                        "ec2:CreateNetworkInterface",
                        "ec2:CreateNetworkInterfacePermission",
                        "ec2:CreateVpcEndpoint",
                        "ec2:DeleteNetworkInterface",
                        "ec2:DeleteNetworkInterfacePermission",
                        "ec2:DescribeDhcpOptions",
                        "ec2:DescribeNetworkInterfaces",
                        "ec2:DescribeRouteTables",
                        "ec2:DescribeSecurityGroups",
                        "ec2:DescribeSubnets",
                        "ec2:DescribeVpcEndpoints",
                        "ec2:DescribeVpcs",
                        "ecr:BatchCheckLayerAvailability",
                        "ecr:BatchGetImage",
                        "ecr:CreateRepository",
                        "ecr:Describe*",
                        "ecr:GetAuthorizationToken",
                        "ecr:GetDownloadUrlForLayer",
                        "ecr:StartImageScan",
                        "elastic-inference:Connect",
                        "elasticfilesystem:DescribeFileSystems",
                        "elasticfilesystem:DescribeMountTargets"
                        ],
                resources=["*"])
            )

    