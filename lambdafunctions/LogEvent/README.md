# LogEvent Lambda Function

## Deployment package prerequisites
* pymysql

## Environment variables to set in Lambda Dashboard
RDS_HOST - the hostname of the mysql rds db instance 
NAME - the mysql rds db username
PASSWORD = the mysql rds db password
DB_NAME = the schema name of the rds db
DB_TABLE = the table name to record messages into

## Description
This function simply logs any message to the database. ToDo: add logging of reactions