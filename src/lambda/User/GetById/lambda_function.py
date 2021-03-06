import json
import logging

from cognito_helpers import get_users
import http_status

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def handler(event, context):
    userId = event["pathParameters"].get("userId") if event["pathParameters"] else None
    if not userId:
        return http_status.bad_request()

    user, _ = get_users(filter_=('email', userId))
    if not user:
        return http_status.not_found()

    return http_status.success(json.dumps(user))
