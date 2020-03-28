import datetime
import hashlib
import os

from django.db.models import Q
from django.shortcuts import render
from dotenv import load_dotenv
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from app.helper_functions import get_token, get_user
from app.models import Idea, User, UserToken
from app.serializers import IdeaSerializer, UserSerializer

from .answer_views import (AllAnswersView, AnswerView, ExcelSheetView,
                           FilterAnswerDateView, MarksView, LeaderBoardView,
                           UnevaluatedAnswersView)
from .question_views import (AllQuestionsView, FilterQuestionDateView,
                             QuestionView)

load_dotenv()

# View for Admin Signup
class AdminSignupView(APIView):

    def post(self, request):
        req_data = {}
        req_data['email'] = request.data.get("email", None)
        req_data['username'] = request.data.get("username", None)
        req_data['platform'] = request.data.get("platform", 0)
        req_data['password'] = request.data.get("password", None)
        req_data['is_superuser'] = True       

        # Hardcoded the password and email address
        if (req_data.get('password', None)==os.getenv('ADMIN_PASSWORD') and 
            req_data.get('username', None)==os.getenv('ADMIN_USERNAME') and 
            req_data.get('email', None)==os.getenv('ADMIN_EMAIL_ID')):

            try:
                # Checking if Admin already signed up
                user = User.objects.get(username=req_data['username'], email=req_data['email'])
                return Response({"message":"Admin already signed Up"}, status=status.HTTP_400_BAD_REQUEST)
            except User.DoesNotExist:
                # Creating superuser (Admin)
                print(req_data)
                serializer = UserSerializer(data=req_data)
                if serializer.is_valid():
                    serializer.save()
                    user = User.objects.get(username=req_data['username'], email=req_data['email'])
                    user.is_superuser = True
                    user.password = req_data['password']
                    user.save()
                    return Response({"message":"Admin signed up"}, status=status.HTTP_200_OK)
                else:
                    return Response({"message":"Invalid Data"}, status=status.HTTP_400_BAD_REQUEST)

        else:            
            return Response({"message":"Invalid Email and Password"}, status=status.HTTP_400_BAD_REQUEST)

# VIew to Login Admin
class AdminLoginView(APIView):
    

    def post(self, request):
        req_data = {}
        req_data['email'] = request.data.get("email", None)
        req_data['username'] = request.data.get("username", None)
        req_data['platform'] = request.data.get("platform", 0)
        req_data['password'] = request.data.get("password", None)
        req_data['is_superuser'] = True

        if req_data.get("platform", None)==None:
            req_data['platform'] = 0
        try:
            user = User.objects.get(username=req_data['username'], email=req_data['email'], platform=req_data['platform'])
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
                    return Response({"message":"Admin Logged in", "Admin":{
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
                    return Response({"message":"Admin Logged in", "Admin":{
                        "id":user.id,
                        "username":user.username,
                        "platform":user.platform,
                        "email":user.email,
                        "token":token
                    }})
            else:
                return Response({"message":"Invalid Password"}, status=status.HTTP_403_FORBIDDEN)
        except User.DoesNotExist:
            return Response({"message":"Admin does not exist"}, status=status.HTTP_403_FORBIDDEN) 


# View to Logout Admin
class AdminLogoutView(APIView):

    def get(self, request, format=None):
        # Get User and delete the token
        token = request.headers.get('Authorization', None)
        if token is None or token=="":
            return Response({"message":"Authorization credentials missing"}, status=status.HTTP_403_FORBIDDEN)
        
        user = get_user(token)
        if user is None:
            return Response({"message":"User Already Logged Out"}, status=status.HTTP_403_FORBIDDEN)

        response = {
            "message":"Admin logged out", 
            "Details":{
                "id": user.id,
                "email":user.email
            }}
        
        usertoken = UserToken.objects.get(user=user.id)
        usertoken.delete()
        return Response(response, status=status.HTTP_200_OK)

# View to Get unpublished ideas and Reviewing them
class UnpublishedIdeas(APIView):

    # Get unpublished ideas
    def get(self, request):
        token = request.headers.get('Authorization', None)
        if token is None or token=="":
            return Response({"message":"Authorization credentials missing"}, status=status.HTTP_403_FORBIDDEN)
        
        user = get_user(token)
        if user is None:
            return Response({"message":"User Already Logged Out"}, status=status.HTTP_403_FORBIDDEN)

        keys = {"PENDING":0, "PUBLISHED":1, "REJECTED":2}
        if user.is_superuser==True:
            ideas = list(Idea.objects.filter(is_reviewed=keys['PENDING']))
            serializer = IdeaSerializer(ideas, many=True)
            return Response({"message":serializer.data}, status=status.HTTP_200_OK)
        else:
            return Response({"message":"Not an Admin"}, status=status.HTTP_403_FORBIDDEN)            

    # Review Unpublished Ideas
    def post(self, request):
        token = request.headers.get('Authorization', None)
        if token is None or token=="":
            return Response({"message":"Authorization credentials missing"}, status=status.HTTP_403_FORBIDDEN)
        
        user = get_user(token)
        if user is None:
            return Response({"message":"User Already Logged Out"}, status=status.HTTP_403_FORBIDDEN)

        req_data = request.data
        keys = {"PENDING":0, "PUBLISHED":1, "REJECTED":2}

        if user.is_superuser==True:
            try:
                idea = Idea.objects.get(id=req_data['idea_id'])
                idea.is_reviewed = req_data['is_reviewed']
                idea.reviewer_id = user
                idea.save()
                serializer = IdeaSerializer(idea)
                return Response({"message":"Idea reviewed successfully", "idea":serializer.data}, status=status.HTTP_200_OK)
            except:
                return Response({"message":"Invalid Idea Id"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"message":"Only Admin can Access"}, status=status.HTTP_403_FORBIDDEN)            

# View to get rejected ideas
class RejectedIdeasView(APIView):

    def get(self, request):
        token = request.headers.get('Authorization', None)
        if token is None or token=="":
            return Response({"message":"Authorization credentials missing"}, status=status.HTTP_403_FORBIDDEN)
        
        user = get_user(token)
        if user is None:
            return Response({"message":"User Already Logged Out"}, status=status.HTTP_403_FORBIDDEN)

        req_data = request.data
        keys = {"PENDING":0, "PUBLISHED":1, "REJECTED":2}

        if user.is_superuser==True:
            ideas = list(Idea.objects.filter(is_reviewed=keys['REJECTED']))
            serializer = IdeaSerializer(ideas, many=True)
            return Response({"message":serializer.data}, status=status.HTTP_200_OK)
        else:
            return Response({"message":"Not an Admin"}, status=status.HTTP_403_FORBIDDEN)            

# Get all Ideas (published, unpublished and rejected)
class AllIdeasView(APIView):

    def get(self, request):
        token = request.headers.get('Authorization', None)
        if token is None or token=="":
            return Response({"message":"Authorization credentials missing"}, status=status.HTTP_403_FORBIDDEN)
        
        user = get_user(token)
        if user is None:
            return Response({"message":"User Already Logged Out"}, status=status.HTTP_403_FORBIDDEN)

        req_data = request.data

        if user.is_superuser==True:
            ideas = list(Idea.objects.all())
            serializer = IdeaSerializer(ideas, many=True)
            return Response({"message":serializer.data}, status=status.HTTP_200_OK)
        else:
            return Response({"message":"Not an Admin"}, status=status.HTTP_403_FORBIDDEN)


class SearchAllIdeaByContent(APIView):

    def get(self, request):

        text = request.query_params.get("text", None)
        print(text)
        all_ideas = list(Idea.objects.filter(Q(project_title__icontains=text) | Q(project_description__icontains=text)).all())
        search_result = all_ideas
        
        if len(search_result)==0:
            return Response({"message":"No Idea found"}, status=204)

        serializer = IdeaSerializer(search_result, many=True)
        serializer_data = serializer.data

        return Response({"message":serializer_data}, status=status.HTTP_200_OK)
