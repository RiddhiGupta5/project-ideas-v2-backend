from django.shortcuts import render
from django.contrib.auth import login, logout
from django.db.models import Q

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authtoken.models import Token

from social_django.utils import load_strategy, load_backend
from social_core.exceptions import MissingBackend, AuthTokenError, AuthForbidden
from social_core.backends.oauth import BaseOAuth2

import hashlib
import jwt
import datetime
import requests
import os
from dotenv import load_dotenv

from .helper_functions import get_token, get_user

from app.serializers import (
    SocialSerializer,
    UserSerializer,
    SocialMediaDetailsSerializer,
)

from .models import User, UserToken, SocialMediaDetails

from .ideasView import (
    PostIdeaView,
    PublishedIdeasView,
    ViewIdea,
    SearchIdeaByContent,
)

from .voteAndCommentViews import (
    VoteView,
    CommentView,
)

load_dotenv()

def social_media_details(user, platform_name, social_user_id):
    record = SocialMediaDetails.objects.filter(Q(platform_name=platform_name) & Q(user_email=user.email))
    temp = SocialMediaDetailsSerializer(record, many=True)
    print(temp.data)
    if len(record)==0:
        print("New record")
        data = {
            "platform_name":platform_name,
            "user_email": user.email,
            "user_id": user.id,
            "social_user_id": social_user_id
        }
        serializer = SocialMediaDetailsSerializer(data=data)
        if serializer.is_valid():
            print("IT is valid")
            serializer.save()


# View for Social Login 
class SocialLoginView(APIView):

    def post(self, request):
        #Validating and getting data from request
        secret_key = os.getenv("GOOGLE_RECAPTCHA_SECRET")
        data={
            'secret': secret_key,
            'response': request.data.get('g-recaptcha-response', None)
        }

        resp = requests.post(
            'https://www.google.com/recaptcha/api/siteverify',
            data=data
        )

        print(resp.json())

        if not resp.json().get('success'):
            return Response(data={'error': 'ReCAPTCHA not verified.'}, status=status.HTTP_406_NOT_ACCEPTABLE)

        req_data = request.data
        serializer = SocialSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        provider = req_data['provider']
        strategy = load_strategy(request)

        try:
            backend = load_backend(
                strategy=strategy, 
                name=provider,
                redirect_uri=None)
        except MissingBackend:
            return Response({"error": "Please provide a valid provider"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            if isinstance(backend, BaseOAuth2):
                access_token = req_data['access_token']

            #Creating a new user by using google or facebook
            user = backend.do_auth(access_token)
            print(user.id)
            authenticated_user = backend.do_auth(access_token, user=user)

        except Exception as error:
            return Response({
                "error": {
                    "access_token":"Invalid token",
                    "details":str(error)
                }
            }, status=status.HTTP_400_BAD_REQUEST)


        if authenticated_user and authenticated_user.is_active:     
            #generate Token for authtication
            my_user = User.objects.filter(Q(username__iexact=user.username) & Q(email=user.email))
            if len(my_user)==0:
                user = User.objects.create(
                    username=user.username,
                    email=user.email,
                    platform=0
                )
            else:
                user = my_user[0]

            token = get_token({
                "username":user.username,
                "platform":user.platform,
                "date_time":str(datetime.datetime.today())
            })
            try:
                usertoken = UserToken.objects.get(user=user.id)
                return Response({
                    "message":"User Already Logged in",
                    "User":{
                        "id": user.id,
                        "username":user.username,
                        "platform":user.platform,
                        "email": user.email,                
                        "token":token
                    }
                }, status=status.HTTP_400_BAD_REQUEST)
            except UserToken.DoesNotExist:
                UserToken.objects.create(
                    token=token,
                    user=user
                )
                return Response({
                    "message":"User Signed up successfully", 
                    "User":{
                        "id": user.id,
                        "username":user.username,
                        "platform":user.platform,
                        "email": user.email,                
                        "token":token
                    }}, status=status.HTTP_201_CREATED)

# View for Social Logout
class LogoutView(APIView):

    def get(self, request, format=None):
        # Get User and delete the token
        token = request.headers.get('Authorization', None)
        if token is None or token=="":
            return Response({"message":"Authorization credentials missing"}, status=status.HTTP_403_FORBIDDEN)
        
        user = get_user(token)
        if user is None:
            return Response({"message":"User Already Logged Out"}, status=status.HTTP_403_FORBIDDEN)

        response = {
            "message":"User logged out", 
            "Details":{
                "id": user.id,
                "username":user.username,
                "platform":user.platform,
                "email": user.email
            }}
        
        usertoken = UserToken.objects.get(user=user.id)
        usertoken.delete()
        return Response(response, status=status.HTTP_200_OK)

class UserSignupView(APIView):

    # Sigup user (create new object)
    def post(self, request):

        secret_key = os.getenv("GOOGLE_RECAPTCHA_SECRET")
        data={
            'secret': secret_key,
            'response': request.data.get('g-recaptcha-response', None)
        }

        resp = requests.post(
            'https://www.google.com/recaptcha/api/siteverify',
            data=data
        )

        print(resp.json())

        if not resp.json().get('success'):
            return Response(data={'error': 'ReCAPTCHA not verified.'}, status=status.HTTP_406_NOT_ACCEPTABLE)

        user_data = {}
        user_data['email'] = request.data.get("email", None)
        user_data['username'] = request.data.get("username", None)
        user_data['platform'] = request.data.get("platform", 0)
        user_data['password'] = request.data.get("password", None)
        if len(user_data['password'])<6:
            return Response({"Invalid Password"}, status=status.HTTP_400_BAD_REQUEST)
        serializer = UserSerializer(data=user_data)       

        if serializer.is_valid():
            serializer.save()            
            
            user = User.objects.filter(Q(username__iexact=user_data['username']) & Q(email=user_data['email']))
            user = user[0]
            token = get_token({
                "username":user.username,
                "platform":user.platform,
                "date_time":str(datetime.datetime.today())
            })
            user_data['token'] = token
            del user_data['password']
            try:
                usertoken = UserToken.objects.get(user=user.id)
                return Response({"message":"User Already Logged in"}, status=status.HTTP_400_BAD_REQUEST)
            except UserToken.DoesNotExist:
                UserToken.objects.create(
                    token=token,
                    user=user
                )
                return Response({"message":"User Signed up successfully", "User":user_data}, status=status.HTTP_201_CREATED)
        else:
            return Response({"message":serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

class NormalLoginView(APIView):

    def post(self, request):

        secret_key = os.getenv("GOOGLE_RECAPTCHA_SECRET")
        data={
            'secret': secret_key,
            'response': request.data.get('g-recaptcha-response', None)
        }

        resp = requests.post(
            'https://www.google.com/recaptcha/api/siteverify',
            data=data
        )

        print(resp.json())

        if not resp.json().get('success'):
            return Response(data={'error': 'ReCAPTCHA not verified.'}, status=status.HTTP_406_NOT_ACCEPTABLE)

        req_data = request.data
        if req_data.get("platform", None)==None:
            req_data['platform'] = 0
        
        user = User.objects.filter(Q(username__iexact=req_data['username']) & Q(email=req_data.get('email', None)))
        if len(user)==0:
            return Response({"message":"User does not exist"}, status=status.HTTP_403_FORBIDDEN)  
        else:
            user = user[0]
            m = hashlib.md5()     
            m.update(req_data['password'].encode("utf-8"))
            if user.password == str(m.digest()):
                token = get_token({
                    "username":user.username,
                    "platform":user.platform,
                    "date_time":str(datetime.datetime.today())
                })
                try:
                    usertoken = UserToken.objects.get(user=user.id)
                    return Response({"message":"User Logged in", "User":{
                        "id":user.id,
                        "username":user.username,
                        "platform":user.platform,
                        "email":user.email,
                        "token":usertoken.token
                    }})
                except:
                    UserToken.objects.create(
                        token=token,
                        user=user
                    )
                    return Response({"message":"User Logged in", "User":{
                        "id":user.id,
                        "username":user.username,
                        "platform":user.platform,
                        "email":user.email,
                        "token":token
                    }})
            else:
                return Response({"message":"Invalid Password"}, status=status.HTTP_403_FORBIDDEN)
            

class LoginSignup(APIView):        

    def post(self, request):

        secret_key = os.getenv("GOOGLE_RECAPTCHA_SECRET")
        data={
            'secret': secret_key,
            'response': request.data.get('g-recaptcha-response', None)
        }

        resp = requests.post(
            'https://www.google.com/recaptcha/api/siteverify',
            data=data
        )

        if not resp.json().get('success'):
            return Response(data={'error': 'ReCAPTCHA not verified.'}, status=status.HTTP_406_NOT_ACCEPTABLE)

        req_data = request.data
        if req_data.get("platform", None)==None:
            req_data['platform'] = 0
        
        print("&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&")
        print(req_data)
        print("$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$")
        user = User.objects.filter(email=req_data.get('email', None))
        trial = UserSerializer(user, many=True)
        print(trial.data)

        if len(user)==0:
            print("creating new user")
            serializer = UserSerializer(data=req_data)  
            if serializer.is_valid():
                print("Everythong is valid")
                serializer.save()
                user = User.objects.filter(Q(username__iexact=req_data['username']) & Q(email=req_data.get('email', None)))
                user = user[0]
                token = get_token({
                    "username":user.username,
                    "platform":user.platform,
                    "date_time":str(datetime.datetime.today())
                })
                req_data['email'] = user.email
                req_data['token'] = token
                
                try:
                    usertoken = UserToken.objects.get(user=user.id)
                    social_media_details(user, req_data.get('platform_name', None), req_data.get('social_user_id', None))
                    return Response({"message":"User Already Logged in", "User":{
                        "id":user.id,
                        "username":user.username,
                        "platform":user.platform,
                        "email":user.email,
                        "token":usertoken.token
                    }}, status=status.HTTP_200_OK)
                except UserToken.DoesNotExist:
                    UserToken.objects.create(
                        token=token,
                        user=user
                    )
                    social_media_details(user, req_data.get('platform_name', None), req_data.get('social_user_id', None))
                    return Response({"message":"User Signed up successfully", "User":req_data}, status=status.HTTP_201_CREATED)
            else:
                print(serializer.errors)
                return Response({"message":serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        else:
            print("User already there")
            user = user[0]
            if req_data.get("password", None)==None:
                req_data['password'] = " "
            m = hashlib.md5()     
            m.update(req_data['password'].encode("utf-8"))
            if user.password == str(m.digest()):
                print("password is correct")
                token = get_token({
                    "username":user.username,
                    "platform":user.platform,
                    "date_time":str(datetime.datetime.today())
                })
                try:
                    usertoken = UserToken.objects.get(user=user.id)
                    social_media_details(user, req_data.get('platform_name', None), req_data.get('social_user_id', None))
                    return Response({"message":"User Logged in", "User":{
                        "id":user.id,
                        "username":user.username,
                        "platform":user.platform,
                        "email":user.email,
                        "token":usertoken.token
                    }})
                except:
                    UserToken.objects.create(
                        token=token,
                        user=user
                    )
                    social_media_details(user, req_data.get('platform_name', None), req_data.get('social_user_id', None))
                    return Response({"message":"User Logged in", "User":{
                        "id":user.id,
                        "username":user.username,
                        "platform":user.platform,
                        "email":user.email,
                        "token":token
                    }})
            else:
                print("Invalid password")
                return Response({"message":"Invalid Password"}, status=status.HTTP_403_FORBIDDEN)              