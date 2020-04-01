import jwt
import os
from dotenv import load_dotenv
load_dotenv()

from .models import User, UserToken

def get_user(token):
    try:
        token = token.split(" ")
        payload = jwt.decode(token[1], os.getenv('JWT_SECRET'), algorithms=['HS256'])
        user = User.objects.get(username=payload['username'], platform=payload['platform'])
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