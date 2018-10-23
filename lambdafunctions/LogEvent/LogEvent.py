import sys
import logging
import pymysql
import json
import os

#rds settings - Lambda role must have RDS access
rds_host = os.environ['RDS_HOST']  # Set in Lambda Dashboard
name = os.environ['DB_USERNAME']
password = os.environ['DB_PW']
db_name = os.environ['DB_NAME']
db_table = os.environ['DB_TABLE']

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def connecttodb():
    try:
        conn = pymysql.connect(rds_host, user=name,
                               passwd=password, db=db_name, connect_timeout=5)
        return conn
    except:
        logger.error(
            "ERROR: Unexpected error: Could not connect to MySql instance.")
        sys.exit()
    logger.info("SUCCESS: Connection to RDS mysql instance succeeded")


def writemessagetodb(event):
    conn = connecttodb()
    _eventid = str(event["event_id"])
    _userid = str(event["user"])
    _msgtext = event["text"]
    _timestamp = str(event["event_time"])
    insertstatement = 'INSERT INTO `' + db_table + \
        r"""` (`eventid`, `userid`, `msgtxt`) VALUES (%s, %s, %s)"""

    with conn.cursor() as cur:
        cur.execute(insertstatement, (_eventid, _userid, _msgtext))
        conn.commit()
        print("Message successfully inserted into DB")


def handler(event, context):
    """
    This function handles SNS posts from Amazon SNS. Currently it:
        1) Inserts the request into an RDS MySQL DB
    Current Assumptions: 
        1) Messages don't contain special characters - i.e: '
        2) Requests are correctly formated (contain body and event, and event contains the expected values)
    
    """
    print("In logevent: ", event)
    try:
        slackevent = json.loads(event["Records"][0]["Sns"]["Message"])

        writemessagetodb(slackevent)

        response = response = {
            "statusCode": 200,
            "body": event
        }
    except Exception as e:
        ''' Just a stub. Please make this better in real use :) '''
        logger.error(f"ERROR: {e}")
        response = {
            "statusCode": 400,
            "body": event
        }
    return response
