import json
import logging

from chat import Chat
from base import Session, row2dict
# from role_validation import UserGroups, validate_group

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def handler(event, context):
    # # check authorization
    # authorized_groups = [
    #     UserGroups.ADMIN,
    #     UserGroups.MENTOR,
    #     UserGroups.PAID
    # ]
    # err, group_response = validate_group(event['requestContext']['authorizer']['claims'], authorized_groups)
    # if err:
    #     return {
    #         "statusCode": 401,
    #         "body": json.dumps({
    #             "errorMessage": group_response
    #         })
    #     }

    chatId = event["pathParameters"].get("chatId") if event["pathParameters"] else None
    if not chatId:
        return {
            "statusCode": 400,
            "body": json.dumps({
                "errorMessage": "missing path parameter(s): 'chatId'"
            })
        }

    session = Session()
    chat = session.query(Chat).get(chatId)
    session.close()
    if not chat:
        session.close()
        return {
            "statusCode": 404,
            "body": json.dumps({
                "errorMessage": "chat with id '{}' not found".format(chatId)
            })
        }

    return {
        "statusCode": 200,
        "body": json.dumps(
            row2dict(chat)
        )
    }
