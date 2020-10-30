import sys
import json
import logging
import uuid
from datetime import datetime

# FOR REFERENCE
from job import Job, JobType, JobStatus, JobTags
from job_application import JobApplication, JobApplicationStatus
from base import Session, engine, Base
import jwt
import boto3
from role_validation import UserGroups, validate_group

client = boto3.client('cognito-idp')

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def handler(event, context):

    authorized_groups = [
        UserGroups.ADMIN,
        UserGroups.MENTOR,
        UserGroups.PAID
    ]
    err, group_response = validate_group(event['requestContext']['authorizer']['claims'], authorized_groups)
    if err:
        return {
            "statusCode": 401,
            "body": json.dumps({
                "errorMessage": group_response
            })
        }

    access_token = event['headers']['X-Aspire-Access-Token']
    
    id_token = (event['headers']['Authorization']).split('Bearer ')[1]
    user = jwt.decode(id_token, verify=False)

    # FOR REFERENCE
    # # create a new session
    session = Session()
    jobId = event["pathParameters"]["jobId"]
    job = session.query(Job).get(jobId)
    
    if job == None:
        return {
            "statusCode": 404,
            "body": json.dumps({
                "message": "ID not found"
            })
        }
    
    credit = int(user['custom:credits'])
    email = user['email']

    
    applied = False
    for job_app in job.job_applications:
        if job_app.applicant_id == email:
            applied = True
    if not applied:
        return {
            "statusCode": 428,
            "body": json.dumps({
                "message": "You need to apply to the job before requesting contact-information"
            })
        }

    if job.people_contacted >= 4:
        return {
            "statusCode": 417,
            "body": json.dumps({
                "message": "Limit of contact information requests has been exceeded"
            })
        }
    print(credit)
    if int(credit) < 5:
        return {
            "statusCode": 402,
            "body": json.dumps({
                "message": "You do not have enough credits to request contact information"
            })
        }
    response = client.update_user_attributes(
        UserAttributes=[
            {
                'Name': 'custom:credits',
                'Value': str(int(credit) - 5) #deducting credits for requesting contact_info
            },
        ],
        AccessToken=access_token
    )
    job.people_contacted = job.people_contacted + 1
    session.commit()
    return {
        "statusCode": 200,
        "body": json.dumps({
            "contact_details": {
                    "email" : job.posted_by,
                    "given_name" : job.poster_given_name,
                    "family_name" : job.poster_family_name
                }   
        })
    }