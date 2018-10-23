import sys
import logging
import pymysql
import json
import boto3
import os
from urllib.parse import parse_qsl
import requests
from nltk.sentiment.vader import SentimentIntensityAnalyzer

sid = SentimentIntensityAnalyzer()

logger = logging.getLogger()
logger.setLevel(logging.INFO)

EXAMPLE_COMMAND = "do"
MENTION_REGEX = "^<@(|[WU].+?)>(.*)"
rds_host = os.environ['RDS_HOST'] # Set in Lambda Dashboard
name = os.environ['DB_USERNAME']
password = os.environ['DB_PW']
db_name = os.environ['DB_NAME']
db_table = os.environ['DB_TABLE']

def connecttodb():
    try:
        conn = pymysql.connect(rds_host, user=name, passwd=password, db=db_name, connect_timeout=5)
        logger.info("SUCCESS: Connection to RDS mysql instance succeeded")
        return conn
    except:
        logger.error("ERROR: Unexpected error: Could not connect to MySql instance.")
        sys.exit()
    
def getmessagesforuserfromdb(_userid, _timeframe_in_hours):
    conn = connecttodb()
    
    querystatement = "SELECT msgtxt FROM messages WHERE UserId = %s AND Ts >= DATE_SUB(NOW(),INTERVAL %s HOUR)"
    
    with conn.cursor() as cur:
        cur.execute(querystatement, (_userid, _timeframe_in_hours))
        user_msgs = [msg[0] for msg in cur.fetchall()]
        #conn.commit()
        print("Successfully queried user's messages from DB")
    conn.close()
    return user_msgs
    
def handle_command(_command, _userid, cmd_args=1):
    """
        Executes bot command if the command is known
    """
    # Default response is help text for the user
    default_response = "Not sure what you mean. Try *{}*.".format(EXAMPLE_COMMAND)

    # Finds and executes the given command, filling in response
    response = None
    # This is where you implement more commands:
    if _command.startswith(EXAMPLE_COMMAND):
        response = "Sure...write some more code then I can do that!"
    elif _command.startswith("$"):
        response = sid.polarity_scores(_command)
    elif _command == "sentiment":
        messagesforuser = getmessagesforuserfromdb(_userid, cmd_args)
        if messagesforuser is not None:
            msgcount = len(messagesforuser)
            if msgcount > 0:
                sentimentscore = 0
                for m in range(0, msgcount):
                    print("Analyzing sentiment for message:",messagesforuser[m])
                    sentimentscore += sid.polarity_scores(messagesforuser[m])["compound"]
                response = "Sentiment: "+str(round(sentimentscore, 2))
            else:
                response = "Not enough messages in that timeframe to give a sentiment score, or incorrect command arguments"
        else:
            response = "No messages to analyze for that user."
    return response or default_response


def handler(event, context):
    """
    This function handles from the Slack Events API. It is called by a post to a SNS topic. Currently it:
        1) Parses the SNS message for the command event
        2) Analyzes the command
        3) If the command is recognized, perform the appropriate actions
    Current Assumptions: 
        1) Messages are correctly formated (contain body and event, and event contains the expected values)
    
    """
    print("Event:",event)
    try:
        #Get the args from the command
        message = json.loads(event["Records"][0]["Sns"]["Message"])
        eventdict = dict(parse_qsl(message["body"]))
        print("Eventargs:",eventdict)
        
        responsetext = handle_command(eventdict["command"].strip(r"/"), eventdict["user_id"], eventdict["text"])

        response = {"statusCode": 200,
                    "headers": {"Content-Type": "application/json"},
                    "text": responsetext,
                    "response_type": "ephemeral"}
        print("json response",response)
        print("Here in HandleCommand")
        r = requests.post(eventdict["response_url"], data=json.dumps(response))
        print("Requests response:",r)
        
    except Exception as e:
        ''' Just a stub. Please make this better in real use :) '''
        print("Error:",e)
        logger.error(f"ERROR: {e}")
        response = {
            "statusCode": 200,
            "body": 'Error'
        }
    return response
