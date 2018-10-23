
# HandleCommand Lambda Function

## Deployment package prerequisites
* nltk.sentiment
* pymysql
* urllib3
* requests

## Environment variables to set in Lambda Dashboard
RDS_HOST - the hostname of the mysql rds db instance 
NAME - the mysql rds db username
PASSWORD = the mysql rds db password
DB_NAME = the schema name of the rds db
DB_TABLE = the table name to record messages into

## Description
This function handles slack commands passed to it via a SNS topic. It parses the message and performs the appropriate actions for that command