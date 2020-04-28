import jwt
import os
from dotenv import load_dotenv
from pyfcm import FCMNotification
load_dotenv()

from .models import User, UserToken

def get_user(token):
    try:
        token = token.split(" ")
        payload = jwt.decode(token[1], os.getenv('JWT_SECRET'), algorithms=['HS256'])
        user = User.objects.get(username=payload['username'], email=payload['email'], platform=payload['platform'])
        usertoken = UserToken.objects.get(user=user.id)
        return user
    except Exception as error:
        print(error)
        return None

def get_token(payload):
    encoded_jwt = jwt.encode(payload, os.getenv('JWT_SECRET'), algorithm='HS256')
    print("HEYYYY")
    result = (encoded_jwt.decode("utf-8"))
    return result

def send_notifs(registration_ids, message_title, message_body, data=None):
    print("$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$")
    print(data)
    print(registration_ids)
    print(message_body)
    print(message_title)
    print("$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$")
    push_service = FCMNotification(api_key=os.getenv("FCM_SERVER_KEY"))
    try:
        result = push_service.notify_multiple_devices(
            registration_ids=registration_ids, 
            message_title=message_title, 
            message_body=message_body, 
            data_message=data)
        print(result)
        if result['success']==0:
            return 1
        return 0
    except Exception as e:
        print(e)
        return 1