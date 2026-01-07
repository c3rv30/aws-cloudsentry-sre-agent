import aws_cdk as core
import aws_cdk.assertions as assertions

from cloudsentry_ai.cloudsentry_ai_stack import CloudsentryAiStack

# example tests. To run these tests, uncomment this file along with the example
# resource in cloudsentry_ai/cloudsentry_ai_stack.py
def test_sqs_queue_created():
    app = core.App()
    stack = CloudsentryAiStack(app, "cloudsentry-ai")
    template = assertions.Template.from_stack(stack)

#     template.has_resource_properties("AWS::SQS::Queue", {
#         "VisibilityTimeout": 300
#     })
