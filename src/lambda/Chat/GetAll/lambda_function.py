import json
import logging

from chat import Chat, ChatType, ChatStatus
from base import Session, row2dict
from cognito_helpers import get_users
import http_status

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def handler(event, context):
    status_filter = event["queryStringParameters"].get("status", "") if event["queryStringParameters"] else ""
    type_filter = event["queryStringParameters"].get("type", "") if event["queryStringParameters"] else ""
    user_filter = event["queryStringParameters"].get("email", "") if event["queryStringParameters"] else ""

    session = Session()
    # TODO: more filters? (tags)
    filtered_query = session.query(Chat)
    if status_filter:
        status_filter = [ChatStatus[x.strip()] for x in status_filter.split(',') if x in ChatStatus.__members__]
        filtered_query = filtered_query.filter(Chat.chat_status.in_(status_filter))
    if type_filter:
        type_filter = [ChatType[x.strip()] for x in type_filter.split(',') if x in ChatType.__members__]
        filtered_query = filtered_query.filter(Chat.chat_type.in_(type_filter))
    if user_filter:
        user, _ = get_users(filter_=('email', user_filter), attributes_filter=['custom:user_type'])
        user_type = user['attributes']['custom:user_type']
        if user_type == 'PAID' or user_type == 'FREE':
            filtered_query = filtered_query.filter(Chat.aspiring_professionals.any(user_filter))
        elif user_type == 'MENTOR':
            filtered_query = filtered_query.filter(Chat.senior_executive == user_filter)

    chats = filtered_query.all()
    session.close()

    users, _ = get_users()
    chats_modified = [row2dict(r) for r in chats]
    for chat in chats_modified:
        for user in users:
            if chat['senior_executive'] == user['attributes']['email']:
                chat['se_given_name'] = user['attributes']['given_name']
                chat['se_family_name'] = user['attributes']['family_name']
                chat['se_picture'] = user['attributes']['picture']
                chat['se_company'] = user['attributes']['custom:company']
                chat['se_position'] = user['attributes']['custom:position']
                chat['se_region'] = json.loads(user['attributes']['address'])['region']
                chat['se_industry_tags'] = user['attributes']['custom:industry_tags']
                break

    return http_status.success(json.dumps({
            "chats": chats_modified,
            "count": len(chats_modified)
        }))
