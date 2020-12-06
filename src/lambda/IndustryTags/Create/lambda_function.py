import json
import logging

from industry_tag import IndustryTag
from base import Session
from role_validation import UserType, check_auth

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def handler(event, context):
    # check authorization
    authorized_user_types = [
        UserType.ADMIN,
        UserType.MENTOR,
        UserType.PAID,
        UserType.FREE
    ]
    success, _ = check_auth(event['headers']['Authorization'], authorized_user_types)
    if not success:
        return {
            "statusCode": 401,
            "body": json.dumps({
                "errorMessage": "unauthorized"
            })
        }

    body = json.loads(event["body"])
    tag = body.get("tag") if body else None

    if not tag:
        return {
            "statusCode": 400,
            "body": json.dumps({
                "errorMessage": "missing body attribute(s): 'tag'"
            })
        }

    IndustryTag_new = IndustryTag(tag=tag.lower())

    session = Session()
    session.add(IndustryTag_new)
    session.commit()
    session.close()

    return {
        "statusCode": 201
    }
