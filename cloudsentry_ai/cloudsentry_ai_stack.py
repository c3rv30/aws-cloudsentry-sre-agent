import os
import aws_cdk as cdk
from aws_cdk import (
    Stack,
    Duration,
    aws_lambda as _lambda,
    aws_iam as iam,
    aws_logs as logs,
    aws_logs_destinations as destinations,
)
from constructs import Construct


class CloudsentryAiStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Use variables passed from app.py or fallback to os.getenv
        anthropic_key = os.getenv("ANTHROPIC_API_KEY")
        slack_url = os.getenv("SLACK_WEBHOOK_URL")
        anthropic_ver = os.getenv("ANTHROPIC_VERSION", "2023-06-01")

        # Validation: Ensure critical variables are present during synthesis
        if not anthropic_key:
            print("⚠️ Warning: ANTHROPIC_API_KEY not found in environment. Deployment may fail or Lambda won't work.")

        # 1. IAM ROLE
        lambda_role = iam.Role(
            self,
            "CloudSentryAgentRole",
            assumed_by=iam.ServicePrincipal("lambda.amazonaws.com"),
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name(
                    "service-role/AWSLambdaBasicExecutionRole"
                )
            ],
        )

        # Note: Since we are using Anthropic API directly via HTTP, we don't need Bedrock permissions.
        # If you switch to Amazon Bedrock later, uncomment the following:
        # lambda_role.add_to_policy(
        #     iam.PolicyStatement(actions=["bedrock:InvokeModel"], resources=["*"])
        # )

        # Permission to read Logs (Required for debugging the agent itself if needed)
        lambda_role.add_to_policy(
            iam.PolicyStatement(
                actions=[
                    "logs:StartQuery",
                    "logs:GetQueryResults",
                    "logs:DescribeLogGroups",
                ],
                resources=["*"],
            )
        )

        # 2. LAMBDA: The function that will execute the Python code
        agent_lambda = _lambda.Function(
            self,
            "SRE_Agent_Function",
            runtime=_lambda.Runtime.PYTHON_3_12,
            handler="agent.handler",
            code=_lambda.Code.from_asset("./lambda"),
            role=lambda_role,
            timeout=Duration.seconds(60),
            environment={
                "ANTHROPIC_API_KEY": str(anthropic_key or "").strip(),
                "SLACK_WEBHOOK_URL": str(slack_url or "").strip(),
                "ANTHROPIC_VERSION": str(anthropic_ver).strip(),
            },
        )

        # -----------------------------------------------------------
        # REAL LOGS INFRASTRUCTURE
        # -----------------------------------------------------------

        # 1. Create a "dummy" Log Group simulating a Production App
        app_log_group = logs.LogGroup(
            self,
            "AppProductionLogs",
            log_group_name="prod/payment-service",  # Real name visible in console
            retention=logs.RetentionDays.ONE_WEEK,
            removal_policy=cdk.RemovalPolicy.DESTROY,
        )

        # 2. Create the filter: "Listen for anything containing 'ERROR' and send to Lambda"
        app_log_group.add_subscription_filter(
            "AlertOnErrors",
            destination=destinations.LambdaDestination(agent_lambda),
            filter_pattern=logs.FilterPattern.all_terms(
                "ERROR"
            ),  # Only triggers on ERROR
        )
