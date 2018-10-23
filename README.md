
# SentimentBot - A Serverless Sentiment Analysis Bot for Slack
Would you like to analyze the sentiment of messages posted to your slack workspace? Would you also like to avoid running the bot on your own hardware - and avoid paying for hosting elsewhere? This repository lays out a framework and set of features for doing sentiment analysis of Slack data using AWS Lambda - allowing you to keep costs low.

## Setup
Lambda does not have repositories for all python packages, in some cases you may need to include the dependencies for your function with the code. To do so:

[How to create a deployment package](https://docs.aws.amazon.com/lambda/latest/dg/lambda-python-how-to-create-deployment-package.html)

### AWS Prerequisites
* An AWS Account
* An RDS Instance
* SNS Topics (details to come)

### Step 1 - Install the required modules per lambda function

```bash
$ cd lambdafunctions
$ mkdir [lambdafunctionname]
$ cd [lambdafunctionname]
$ pip install module-name -t .
```

### Step 2 - Zip the contents of the _lambdafunctionname_ folder into an archive

### Step 3 - Upload the archive to AWS Lambda/S3

### Step 4 - Set the code entry type in Lambda function dashboard to upload from Zip

### Step 5 - Set the handler function and runtime on the Lambda function dashboard appropriately
* The function name to set is typically called 'handler' for this project for each lambda function

### Step 6 - Create SNS topic and subscriptions
* As of this writing, one topic is needed - name of your choosing
* Add subscriptions for HandleCommand and LogEvent
* Add filters to your subscriptions to route events correctly [SNS Topic Filters](SNS_Sub_Filters)

### Step 7 - Set the environment variables per function
