import json
import logging

from connect_se import ConnectSE
from base import Session
# from role_validation import UserType, check_auth

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def handler(event, context):
    # # check authorization
    # authorized_user_types = [
    #     UserType.ADMIN,
    #     UserType.MENTOR,
    #     UserType.FREE,
    #     UserType.PAID
    # ]
    # success, _ = check_auth(event['headers']['Authorization'], authorized_user_types)
    # if not success:
    #     return {
    #         "statusCode": 401,
    #         "body": json.dumps({
    #             "errorMessage": "unauthorized"
    #         })
    #     }

    connectId = event["pathParameters"].get("connectId") if event["pathParameters"] else None
    if not connectId:
        return {
            "statusCode": 400,
            "body": json.dumps({
                "errorMessage": "missing path parameter(s): 'connectId'"
            })
        }

    session = Session()
    connect_se = session.query(ConnectSE).get(connectId)
    if not connect_se:
        session.close()
        return {
            "statusCode": 404,
            "body": json.dumps({
                "errorMessage": "connect senior executive with id '{}' not found".format(connectId)
            })
        }

    session.delete(connect_se)
    session.commit()
    session.close()

    return {
        "statusCode": 200
    }
