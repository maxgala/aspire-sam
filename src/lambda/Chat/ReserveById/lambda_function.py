import json
import logging
from botocore.exceptions import ClientError
from datetime import datetime, date, timedelta, time

from chat import Chat, ChatType, ChatStatus, credit_mapping
from base import Session
from role_validation import UserType, check_auth
from cognito_helpers import get_users, admin_update_credits
from send_email import send_email, build_calendar_invite
import http_status

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def handler(event, context):
    authorized_user_types = [
        UserType.FREE,
        UserType.PAID
    ]
    success, user = check_auth(event['headers']['Authorization'], authorized_user_types)

    if not success:
        return http_status.unauthorized()

    chatId = event["pathParameters"].get("chatId") if event["pathParameters"] else None
    if not chatId:
        return http_status.bad_request("missing path parameter(s): 'chatId'")
    
    logging.info(event['headers'])
    #timezone_offset_min = event['headers']['Aspire-Client-Timezone-Offset']
    #if timezone_offset_min is None:
    #FIXME
    timezone_offset_min = -300 # default to EST

    session = Session()
    chat = session.query(Chat).get(chatId)
    if not chat:
        session.close()
        return http_status.not_found("chat with id '{}' not found".format(chatId))

    # ACTIVE Chats are available for booking
    # User must not have booked this Chat and must have sufficient funds
    if chat.chat_status != ChatStatus.ACTIVE:
        session.close()
        return http_status.forbidden("Chat is not available for booking")

    if chat.aspiring_professionals and user['email'] in chat.aspiring_professionals:
        session.close()
        return http_status.forbidden("user '{}' already reserved chat with id '{}'".format(user['email'], chatId))

    user_credits = int(get_users(filter_=("email", user['email']), \
        attributes_filter=["custom:credits"])[0]['attributes'].get('custom:credits'))
    if user_credits < credit_mapping[chat.chat_type]:
        session.close()
        return http_status.forbidden("You don't have sufficient credits to reserve a chat")

    chat.aspiring_professionals = [user['email']]
    chat.chat_status = ChatStatus.RESERVED

    try:
        prepare_and_send_emails(chat, timezone_offset_min)
    except ClientError as e:
        session.rollback()
        session.close()
        logging.info(e)
        if int(e.response['ResponseMetadata']['HTTPStatusCode']) >= 500:
            return http_status.server_error()
        else:
            return http_status.bad_request()
    else:
        admin_update_credits(user['email'], (-credit_mapping[chat.chat_type]))

        session.commit()
        session.close()
        return http_status.success()

def prepare_and_send_emails(chat, timezone_offset_min):
    mentee_IDs = chat.aspiring_professionals # FIXME mentee is now only a single element list
    mentor_ID = chat.senior_executive

    event_name = '[MAX Aspire] Coffee Chat with Senior Executive'
    event_description = chat.description

    if chat.fixed_date:
        chat_date = chat.fixed_date
    else:
        today = date.today()
        day_idx = (today.weekday() + 1) % 7 # today.weekday() is 0 for Monday
        chat_date = today + timedelta(days=7-day_idx)
    chat_date = chat_date + timedelta(minutes=timezone_offset_min)
    chat_time = time(14,0,0)
    event_start = datetime.combine(chat_date,chat_time)
    chat_date = f'{chat_date:%b %d, %Y}'
    event_end = event_start + timedelta(hours=12)

    mentees = []
    for m in mentee_IDs:
        m_User, _ = get_users(filter_=("email", m), attributes_filter=["given_name", "family_name"])
        mentees.append("%s %s" % (m_User['attributes']['given_name'], m_User['attributes']['family_name']))
    mentee_name = mentees[0]

    mentor, _ = get_users(filter_=("email", mentor_ID), attributes_filter=["given_name", "family_name"])
    mentor_name = "%s %s" % (mentor['attributes']['given_name'], mentor['attributes']['family_name'])

    chat_type = ''
    if chat.chat_type == ChatType.MOCK_INTERVIEW:
        chat_type = 'Mock Interview'
    else:
        chat_type = 'One-on-One coffee chat'

    subject = f"[MAX Aspire] Your coffee chat with {mentor_name} is confirmed!"
    body = f"Salaam {mentee_name}!\n\nWe are delighted to confirm your {chat_type} with {mentor_name}.\n\nYour coffee chat will take place on: {chat_date}. Please connect with the Senior Executive to determine the virtual or physical venue.\n\nPlease ensure your punctuality and professionalism. This could be the beginning of a special journey.\n\nKind regards,\n\nThe MAX Aspire Team"
    all_attendees = list(mentee_IDs)
    all_attendees.append(mentor_ID)

    ics = build_calendar_invite(event_name, event_description, event_start, event_end, all_attendees)
    send_email(all_attendees, subject, body, ics=ics)
