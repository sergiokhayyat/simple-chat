import boto3
import json
import os
from boto3.dynamodb.conditions import Key
from datetime import datetime, timezone

# Instantiate messages table
messages_table = boto3.resource('dynamodb').Table(os.environ.get('DYNAMODB_MESSAGES_TABLE'))

def get_messages(event, context):
    """Return the messages published in the chat room

    :param chat_id: (path parameter) ID of the chat
    :type chat_id: str

    :rtype: dict
        return example:
        {
            "messages": [
                {   "ts": "timestamp",   "user_id"": "author1",   "text": "text message"   },
                ...
            ]
        }
    """
    chat_id = event.get('pathParameters', {}).get('chat_id')
    messages = messages_table.query(KeyConditionExpression=Key('chat_id').eq(chat_id))
    if "Items" in messages:
        body = {
            "status": 200,
            'messages': [ {'ts': x['ts'], 'user_id': x['user_id'], 'text': x['text']} for x in messages["Items"] ],
        }
        response = {
            "statusCode": 200,
            "body": json.dumps(body)
        }
    else:
        # No Item == 404
        body = {
            "status": 404,
            "title": "Chat not found",
            "detail": f"Chat {chat_id} not found in database",
        }
        response = {
            "statusCode": 404,
            "body": json.dumps(body)
        }
    # return
    return response


def send_message(event, context):
    """Send a message into a chat room

    :param chat_id: (path parameter) ID of the chat
    :type chat_id: str
    :param message: (body) new info
    :type message: dict
        message example:
        {
            "user_id": "user ID of the author",
            "text": "content written by the user",
        }

    :rtype: SimpleResponse
    """
    chat_id = event.get('pathParameters', {}).get('chat_id')
    message = json.loads(event.get('body', '{}'))
    messages_table.put_item(
        Item={
            'chat_id': chat_id,
            'ts': datetime.utcnow().replace(tzinfo=timezone.utc).isoformat(),
            'user_id': message['user_id'],
            'text': message['text'],
        }
    )
    body = {
        "status": 201,
        "title": "OK",
        "detail": f"New message posted into chat {chat_id}",
    }
    return {
        "statusCode": 201,
        "body": json.dumps(body)
    }
