# HandleEvent Lambda Function

## Deployment package prerequisites
* nltk.sentiment
* pymysql
* urllib3
* requests

## Environment variables to set in Lambda Dashboard
SNS_TOPIC_ARN - The ARN of the topic to which events will be posted
AWS_REGION - The AWS region that the lambda function resides in

## Description
This function handles any event coming from Slack via the Events API It determines if the event is a command, message, or verification request and forwards the event to SNS accordingly.