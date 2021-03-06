import logging
import json

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def success(res_body=""):
    return {
        "statusCode": 200,
        "body": res_body,
        "headers": {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'OPTIONS,GET,POST,PUT',
            'Access-Control-Allow-Headers': "'Content-Type,Authorization,Access-Control-Allow-Origin,Aspire-Client-Timezone-Offset'"
        }
    }

def unauthorized(message=""):
    return {
        "statusCode": 401,
        "body": json.dumps({
            "errors": "Unauthorized",
            "message": message
        }),
        "headers": {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'OPTIONS,GET,POST,PUT',
            'Access-Control-Allow-Headers': "'Content-Type,Authorization,Access-Control-Allow-Origin,Aspire-Client-Timezone-Offset'"
        }
    }

def forbidden(message=""):
    return {
        "statusCode": 403,
        "body": json.dumps({
            "errors": "Forbidden",
            "message": message
        }),
        "headers": {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'OPTIONS,GET,POST,PUT',
            'Access-Control-Allow-Headers': "'Content-Type,Authorization,Access-Control-Allow-Origin,Aspire-Client-Timezone-Offset'"
        }
    }

def not_found(message=""):
    return {
        "statusCode": 404,
        "body": json.dumps({
            "errors": "Not Found",
            "message": message
        }),
        "headers": {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'OPTIONS,GET,POST,PUT',
            'Access-Control-Allow-Headers': "'Content-Type,Authorization,Access-Control-Allow-Origin,Aspire-Client-Timezone-Offset'"
        }
    }


def bad_request(message=""):
    return {
        "statusCode": 400,
        "body": json.dumps({
            "errors": "Bad Request",
            "message": message
        }),
        "headers": {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'OPTIONS,GET,POST,PUT',
            'Access-Control-Allow-Headers': "'Content-Type,Authorization,Access-Control-Allow-Origin,Aspire-Client-Timezone-Offset'"
        }
    }

def server_error(message=""):
    return {
        "statusCode": 500,
        "body": json.dumps({
            "error": "Internal Server Error",
            "message": message
        }),
        "headers": {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'OPTIONS,GET,POST,PUT',
            'Access-Control-Allow-Headers': "'Content-Type,Authorization,Access-Control-Allow-Origin,Aspire-Client-Timezone-Offset'"
        }
    }