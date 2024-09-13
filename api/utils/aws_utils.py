import os
import boto3
from api import config
from api.utils.logger import LLPackerLogger
logger = LLPackerLogger(os.path.basename(__file__))

try:

    boto3kwargs = {"region_name": "us-east-1"}
    if os.getenv("AWS_ACCESS_KEY", "") != "" and os.getenv("AWS_SECRET_KEY", "") != "":
        # Load environment variables
        boto3kwargs["aws_access_key_id"] = os.getenv("AWS_ACCESS_KEY")
        boto3kwargs["aws_secret_access_key"] = os.getenv("AWS_SECRET_KEY")

    sns_link = config.sns_link
    sqs_link = config.sqs_link
    
    # Initialize AWS SNS client
    sns = boto3.client( "sns", endpoint_url=sns_link(root=True, arn=False), **boto3kwargs)

    # Initialize AWS SQS client
    sqs = boto3.client( "sqs", endpoint_url=sqs_link(root=True, arn=False), **boto3kwargs)

except Exception as e:
    logger.error("Error in initializing AWS SNS and SQS clients")
    print(e)
    raise

def publish_to_sns(context):
    sns = context.get("sns")
    TopicArn = context.get("topic_arn")
    data = context.get("data")

    try:
        sns.publish(
            TopicArn=TopicArn,
            Message=str(data)
        )
    except Exception as e:
        raise e

    logger.good("Published to SNS topic.")

    return data


def publish_to_sqs(context):
    sqs = context.get("sqs")
    QueueUrl = context.get("queue_url")
    data = context.get("data")

    logger.info(f"Publishing {data} to SQS queue {QueueUrl}.", fg='pink')
    try:
        sqs.send_message(
            QueueUrl=QueueUrl,
            MessageBody=str(data),
            MessageGroupId="user456",
        )
    except Exception as e:
        raise e

    logger.good("Published to SQS queue.")

    return data