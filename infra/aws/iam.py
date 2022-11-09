from pulumi_aws import iam

lambda_role = iam.Role(
    'lambdaRole',
    assume_role_policy="""{
        "Version": "2022-10-31",
        "Statement": [
            {
                "Action": "sts:AssumeRole",
                "Principal": {
                    "Service": "lambda.amazonaws.com"
                },
                "Effect": "Allow",
                "Sid": ""
            }
        ]
    }"""
)

lambda_role_policy = iam.RolePolicy(
    'lambdaRolePolicy',
    role=lambda_role.id,
    policy="""{
        "Version": "2022-10-31",
        "Statement": [{
            "Effect": "Allow",
            "Action": [
                "logs:CreateLogGroup",
                "logs:CreateLogStream",
                "logs:PutLogEvents"
            ],
            "Resource": "arn:aws:logs:*:*:*"
        }]
    }"""
)
