import json
import logging
import enum
from datetime import datetime

from industry_tag import IndustryTag
from base import Session, engine, Base, row2dict

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def handler(event, context):
    body = event["body"]
    search = event["queryStringParameters"].get("search", "") if event["queryStringParameters"] else ""
    fuzzy = event["queryStringParameters"].get("fuzzy", "") if event["queryStringParameters"] else ""

    session = Session()
    if fuzzy.lower() == "true":
        industry_tags = session.query(IndustryTag).filter(IndustryTag.tag.ilike("%{}%".format(search))).all()
    else:
        industry_tags = session.query(IndustryTag).filter(IndustryTag.tag.ilike("{}%".format(search))).all()
    session.close()

    return {
        "statusCode": 200,
        "body": json.dumps({
            "industry_tags": [row2dict(r) for r in industry_tags],
            "count": len(industry_tags)
        })
    }