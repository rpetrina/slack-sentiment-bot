import sys
import logging
import json
import hashlib
import hmac
import boto3
import os
from urllib.parse import parse_qsl
from concurrent.futures import ThreadPoolExecutor

sns_topic_arn = os.environ['SNS_TOPIC_ARN']
aws_region = os.environ['AWS_REGION']

client = boto3.client('sns', region_name=aws_region)
logger = logging.getLogger()
logger.setLevel(logging.INFO)

''' Verify the POST request. '''
''' https://janikarhunen.fi/verify-slack-requests-in-aws-lambda-and-python.html '''
def verify_slack_request(slack_signature=None, slack_request_timestamp=None, request_body=None):
    ''' Form the basestring as stated in the Slack API docs. We need to make a bytestring. '''
    basestring = f"v0:{slack_request_timestamp}:{request_body}".encode('utf-8')

    ''' Make the Signing Secret a bytestring too. '''
    slack_signing_secret = os.environ['SLACK_SIGNING_SECRET']
    slack_signing_secret = bytes(slack_signing_secret, 'utf-8')

    ''' Create a new HMAC "signature", and return the string presentation. '''
    my_signature = 'v0=' + hmac.new(slack_signing_secret, basestring, hashlib.sha256).hexdigest()

    ''' Compare the the Slack provided signature to ours.
    If they are equal, the request should be verified successfully.
    Log the unsuccessful requests for further analysis
    (along with another relevant info about the request). '''
    if hmac.compare_digest(my_signature, slack_signature):
        print("Request verification successful")
        return True
    else:
        logger.warning(f"Verification failed. my_signature: {my_signature}")
        return False

def tryparsebody(body):
    try:
        return json.loads(body)
    except:
        return dict(parse_qsl(body))

def handler(event, context):
    """
    This function handles POST requests from the Slack Events API. Currently it:
        1) Verifies the request is from a trusted source (Slack)
        2) Inserts the request into an RDS MySQL DB if it's a message
    Current Assumptions: 
        1) The API endpoint has already been verified
        2) Messages don't contain special characters - i.e: '
        3) Requests are correctly formated (contain body and event, and event contains the expected values)
    
    """
    print("Event:", event)
    try:
        apievent = tryparsebody(event["body"])
        if 'type' in apievent:
            if apievent["type"] == "url_verification":
                response = {"statusCode": 200,
                            "headers": {"Content-Type": "application/json"},
                            "body": "{\"challenge\": " + str(apievent["challenge"]) + "}"}
                return response

        ''' Capture the necessary data. '''
        slack_signature = event['headers']['X-Slack-Signature']
        slack_request_timestamp = event['headers']['X-Slack-Request-Timestamp']

        ''' Verify the request. '''
        if not verify_slack_request(slack_signature, slack_request_timestamp, event['body']):
            logger.info('Bad request.')
            response = {
                "statusCode": 400,
                "body": "Bad request"
            }
            return response
        
        ''' Handle a command '''
        if not "event" in apievent:
            print("Invoking handlecommand function:", json.dumps(event))
            with ThreadPoolExecutor(max_workers=1) as executor:
                executor.submit(client.publish,
                    TopicArn=sns_topic_arn,
                    Message=json.dumps({'default': json.dumps(event)}),
                    MessageStructure='json',
                    MessageAttributes= {
                        "event_type" : {
                            "DataType":"String",
                            "StringValue":"Simple_Command"
                        }
                    }
                )
            
            print("Successfully invoked handlecommand function")
            response = {"statusCode": 200,
                    "headers": {"Content-Type": "application/json"},
                    "body": json.dumps({
                        "text": "Give me a minute...",
                        "response_type": "ephemeral"
                    })}
            return response
        
        slackevent = apievent["event"]
        slackevent ["event_id"] = apievent["event_id"]
        slackevent ["event_time"] = apievent ["event_time"]
        
        ''' Handle a message posted to a channel '''
        if slackevent["type"]=="message" and not "subtype" in slackevent:
            print("Invoking DB write function")
            print("Slackevent going to SNS:",json.dumps({'default': json.dumps(slackevent)}))
            client.publish(
                TopicArn=sns_topic_arn,
                Message=json.dumps({'default': json.dumps(slackevent)}),
                MessageStructure='json',
                MessageAttributes= {
                    "event_type" : {
                        "DataType":"String",
                        "StringValue":"Simple_Message"
                    }
                }
            )
            print("Successfully invoked logevent function")
        else:
            print("Event not inserted into DB")
        response = {
            "statusCode": 200,
            "body": "Successful request"
        }
    except Exception as e:
        ''' Just a stub. Please make this better in real use :) '''
        logger.error(f"ERROR: {e}")
        response = {
            "statusCode": 400,
            "body": "Bad request"
        }
    return response
