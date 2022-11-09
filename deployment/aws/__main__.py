"""An AWS Python Pulumi program"""

import json

import pulumi
import pulumi_aws as aws

import iam


# Lambda function의 package 저장을 위한 S3 Bucket과 Object 생성
lambda_packages_bucket = aws.s3.BucketV2(
    "lambda-packages-bucket",
    bucket="myfolio-handler-dev-packages",
)
lambda_packages_bucket_object = aws.s3.BucketObjectv2(
    "lambda-packages-bucket-object",
    bucket=lambda_packages_bucket.bucket,
    key="myfolio-handler-packages.zip",
    source=pulumi.FileAsset("../myfolio-handler-packages.zip"),
)

# Lambda layer 생성 - packages layer, app layer
lambda_packages_layer = aws.lambda_.LayerVersion(
    "lambda-packages-layer",
    layer_name="myfolio-handler-dev-packages",
    compatible_runtimes=["python3.9"],
    s3_bucket=lambda_packages_bucket.bucket,
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

# Lambda function 생성
lambda_function = aws.lambda_.Function(
    "lambda-function",
    name="myfolio-handler-dev",
    role=iam.lambda_role.arn,
    code=pulumi.AssetArchive({"api/v1": pulumi.FileArchive("../../api/v1")}),
    runtime="python3.9",
    handler="app.application.handler",
    layers=[lambda_packages_layer.arn, lambda_app_layer.arn],
    timeout=7,
)

# API Gateway 서비스 생성
http_api = aws.apigatewayv2.Api(
    "http-api",
    protocol_type="HTTP",
    name="myfolio-api-dev",
    route_key="ANY /{proxy+}",
    cors_configuration=aws.apigatewayv2.ApiCorsConfigurationArgs(
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
    ),
    target=lambda_function.arn,
)

# API 배포
http_api_deployment = aws.apigatewayv2.Deployment(
    "http-api-deployment",
    api_id=http_api.id,
)

# API staging
http_api_stage_dev = aws.apigatewayv2.Stage(
    "http-api-stage-dev",
    name="dev",
    api_id=http_api.id,
    deployment_id=http_api_deployment.id,
    auto_deploy=True,
)

# 외부 소스(API Gateway)가 Lambda function에 접근할 수 있도록 권한 부여
http_api_lambda_permission = aws.lambda_.Permission(
    "http-api-lambda-permission",
    action="lambda:InvokeFunction",
    function=lambda_function.name,
    principal="apigateway.amazonaws.com",
    source_arn=http_api.execution_arn.apply(lambda arn: arn + "/*"),
)

pulumi.export("execution_arn", http_api.execution_arn)
pulumi.export("dev_execution_arn", http_api_stage_dev.execution_arn)
pulumi.export("source_arn", http_api_lambda_permission.source_arn)
pulumi.export("endpoint", http_api.api_endpoint)
