"""An AWS Python Pulumi program"""

import json

import pulumi
import pulumi_aws as aws


lambda_role = aws.iam.Role(
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
                }
            ],
        }
    ),
)

role_policy_attachment = aws.iam.RolePolicyAttachment(
    "lambda-role-basic-policy-attachment",
    role=lambda_role,
    policy_arn=aws.iam.ManagedPolicy.AWS_LAMBDA_BASIC_EXECUTION_ROLE,
)

lambda_role_rds_policy_attachment = aws.iam.RolePolicyAttachment(
    "lambda-role-rds-policy-attachment",
    role=lambda_role,
    policy_arn=aws.iam.ManagedPolicy.AMAZON_RDS_DATA_FULL_ACCESS,
)

lambda_packages_bucket = aws.s3.Bucket(
    "lambda-packages-bucket",
    bucket="myfolio-handler-dev-packages",
)

lambda_packages_bucket_object = aws.s3.BucketObject(
    "lambda-packages-bucket-object",
    bucket=lambda_packages_bucket.bucket,
    key="myfolio-handler-packages.zip",
    source=pulumi.FileAsset("../myfolio-handler-packages.zip"),
)

lambda_packages_layer = aws.lambda_.LayerVersion(
    "lambda-packages-layer",
    layer_name="myfolio-handler-dev-packages",
    compatible_runtimes=["python3.9"],
    s3_bucket=lambda_packages_bucket_object.bucket,
    s3_key=lambda_packages_bucket_object.key,
)

lambda_app_layer = aws.lambda_.LayerVersion(
    "lambda-app-layer",
    layer_name="myfolio-handler-dev-app",
    compatible_runtimes=["python3.9"],
    code=pulumi.AssetArchive(
        {
            "python/app/core": pulumi.FileArchive("../../app/core"),
            "python/app/db": pulumi.FileArchive("../../app/db"),
            "python/app/dependencies": pulumi.FileArchive("../../app/dependencies"),
            "python/app/__init__.py": pulumi.FileAsset("../../app/__init__.py"),
            "python/app/application.py": pulumi.FileAsset("../../app/application.py"),
        }
    ),
)

lambda_function = aws.lambda_.Function(
    "lambda-function",
    name="myfolio-handler-dev",
    role=lambda_role.arn,
    code=pulumi.AssetArchive({"app/api_v1": pulumi.FileArchive("../../app/api_v1")}),
    runtime="python3.9",
    handler="app.application.handler",
    layers=[lambda_packages_layer.arn, lambda_app_layer.arn],
)

# pulumi.export("endpoint", lambda_function.url)
