import sys
import json
import logging
import uuid
from datetime import datetime

from job import Job, JobType, JobStatus, JobTags
from job_application import JobApplication, JobApplicationStatus
from base import Session, engine, Base, row2dict
from role_validation import UserType, check_auth
import http_status

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def handler(event, context):
    session = Session()
    page = None
    user_id = None
    status = None
    tag = None
    page_size = 20
    if event["queryStringParameters"]:
        page = event["queryStringParameters"].get('page') #returns None if 'page' not in dict
        user_id = event["queryStringParameters"].get('user_id')
        tag = event["queryStringParameters"].get('tag')
        status = event["queryStringParameters"].get('status')
        page_size = int(event["queryStringParameters"].get('page_size',3))

    jobs = session.query(Job)
    if user_id != None:
        jobs = jobs.filter(Job.posted_by == user_id)
    if status != None:
        status_list = [x.upper() for x in status.split(',')]
        jobs = jobs.filter(Job.job_status.in_(status_list))
    if page != None:
        jobs = jobs.offset((int(page) * page_size) - page_size).limit(page_size)
   
    joblist = []
    for job in jobs:
        job_apps_id = []
        for app in job.job_applications:
            job_apps_id.append(app.job_application_id)
        jobdict = row2dict(job)
        jobdict['job_applications'] = job_apps_id
        if tag == None or tag.upper() in jobdict['job_tags']:
            joblist.append(jobdict)
            
    session.close()

    return http_status.success(json.dumps({
            "jobs": joblist,
            "count": len(joblist)
        }))
