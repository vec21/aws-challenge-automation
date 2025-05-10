"""An AWS Python Pulumi program"""
# Import libraries
import pulumi
from pulumi import Config
import pulumi_aws as aws

config = Config()  # <- This line is required to access stack variables

# Use existing bucket or create a new one
bucket = aws.s3.BucketV2(
    "automation-bucket",
    bucket="vec21-aws-challenge",
    tags={"Name": "AutomationBucket"}
)

# Configure website hosting for web interface
website_config = aws.s3.BucketWebsiteConfigurationV2(
    "website-config",
    bucket=bucket.id,
    index_document={
        "suffix": "index.html",
    },
    error_document={
        "key": "error.html",
    }
)

# Create SNS topic for notifications
notification_topic = aws.sns.Topic(
    "notification-topic",
    name="github-report-notifications",
    tags={"Name": "GithubReportNotifications"}
)

# Configure public policy
bucket_policy = aws.s3.BucketPolicy(
    "bucket-policy",
    bucket=bucket.id,
    policy=pulumi.Output.from_input({
        "Version": "2012-10-17",
        "Statement": [{
            "Effect": "Allow",
            "Principal": "*",
            "Action": ["s3:GetObject"],
            "Resource": [pulumi.Output.concat("arn:aws:s3:::", bucket.bucket, "/*")]
        }]
    })
)

# Create Lambda function
lambda_role = aws.iam.Role(
    "lambda-role",
    assume_role_policy={
        "Version": "2012-10-17",
        "Statement": [{
            "Action": "sts:AssumeRole",
            "Principal": {"Service": "lambda.amazonaws.com"},
            "Effect": "Allow",
        }]
    },
    managed_policy_arns=[
        "arn:aws:iam::aws:policy/AmazonS3FullAccess",
        "arn:aws:iam::aws:policy/AmazonSNSFullAccess"
    ]
)

lambda_function = aws.lambda_.Function(
    "code-review-lambda",
    runtime="python3.9",
    handler="handler.handler",
    role=lambda_role.arn,
    code=pulumi.FileArchive("./src"),
    timeout=300,  # 5 minutes to allow code analysis
    memory_size=512,  # More memory for processing
    environment=aws.lambda_.FunctionEnvironmentArgs(
        variables={
            "BUCKET_NAME": bucket.bucket,
            "GITHUB_TOKEN": config.require_secret("github_token"),
            "SNS_TOPIC_ARN": notification_topic.arn
        }
    )
)

# Create CloudWatch Event for periodic execution (optional)
event_rule = aws.cloudwatch.EventRule(
    "daily-report-rule",
    name="daily-github-report",
    description="Trigger daily GitHub report generation",
    schedule_expression="cron(0 8 * * ? *)"  # 8:00 AM UTC every day
)

event_target = aws.cloudwatch.EventTarget(
    "lambda-event-target",
    rule=event_rule.name,
    arn=lambda_function.arn,
    input=pulumi.Output.from_input({
        "repo": "vec21/aws-challenge-automation",
        "days": 1,
        "analyze": True,
        "state": "all"
    }).apply(lambda x: pulumi.Output.json_dumps(x))
)

event_permission = aws.lambda_.Permission(
    "event-lambda-permission",
    action="lambda:InvokeFunction",
    function=lambda_function.name,
    principal="events.amazonaws.com",
    source_arn=event_rule.arn
)

# Export
pulumi.export("bucket_name", bucket.bucket)
pulumi.export("bucket_website_endpoint", website_config.website_endpoint)
pulumi.export("lambda_arn", lambda_function.arn)
pulumi.export("sns_topic_arn", notification_topic.arn)