#!/usr/bin/env python3
import os
from pathlib import Path
import aws_cdk as cdk
from dotenv import load_dotenv
from cloudsentry_ai.cloudsentry_ai_stack import CloudsentryAiStack

# 1. Locate the .env file with ultra-precision
base_dir = Path(__file__).resolve().parent
env_file = base_dir / ".env"

# 2. Verify if the file actually exists before loading
if not env_file.exists():
    print(f"⚠️ ALERT: .env file not found at: {env_file}")
else:
    print(f"✅ .env file detected at: {env_file}")

# 3. Load with override=True to force values from the file to take precedence
load_dotenv(dotenv_path=env_file, override=True)

app = cdk.App()

account_id = os.getenv("AWS_ACCOUNT_ID")
region = os.getenv("AWS_REGION")

print(f"Current configuration: AWS_ACCOUNT_ID={account_id}, AWS_REGION={region}")

if not account_id or not region:
    raise ValueError("❌ Error: AWS_ACCOUNT_ID or AWS_REGION missing from .env file")

CloudsentryAiStack(
    app,
    "CloudsentryAiStack",
    env=cdk.Environment(account=account_id, region=region),
)

app.synth()
