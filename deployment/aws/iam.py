import json

from pulumi_aws import iam

# AWS Lambda function을 위한 IAM Role 생성
lambda_role = iam.Role(
    "lambda-role",
    name="myfolio-handler-dev-role",
    assume_role_policy=json.dumps(
        {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Principal": {"Service": "lambda.amazonaws.com"},
                    "Action": "sts:AssumeRole",
                    "Sid": "",
                }
            ],
        }
    ),
)

# lambda_role에 AWS Managed Policy 연결
lambda_role_basic_policy_attachment = iam.RolePolicyAttachment(
    "lambda-role-basic-policy-attachment",
    policy_arn=iam.ManagedPolicy.AWS_LAMBDA_BASIC_EXECUTION_ROLE,
    role=lambda_role.name,
)
lambda_role_rds_policy_attachment = iam.RolePolicyAttachment(
    "lambda-role-rds-policy-attachment",
    policy_arn=iam.ManagedPolicy.AMAZON_RDS_DATA_FULL_ACCESS,
    role=lambda_role.name,
)
lambda_role_secrets_manager_policy_attachment = iam.RolePolicyAttachment(
    "lambda-role-secrets-manager-policy-attachment",
    policy_arn=iam.ManagedPolicy.SECRETS_MANAGER_READ_WRITE,
    role=lambda_role.name,
)

# Cloudwatch logging을 위해 inline policy 추가
lambda_role_policy = iam.RolePolicy(
    "lambda-role-policy",
    name="myfolio-handler-dev-cloudwatch-log",
    policy=json.dumps(
        {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Action": [
                        "logs:CreateLogGroup",
                        "logs:CreateLogStream",
                        "logs:DescribeLogGroups",
                        "logs:DescribeLogStreams",
                        "logs:PutLogEvents",
                        "logs:GetLogEvents",
                        "logs:FilterLogEvents",
                    ],
                    "Resource": "*",
                }
            ],
        }
    ),
    role=lambda_role.name,
)
