import json
import pulumi
import pulumi_aws as aws

import iam

region = aws.config.region
stage_name = "v1"


bucket = aws.s3.Bucket("myfolio_libraries")
