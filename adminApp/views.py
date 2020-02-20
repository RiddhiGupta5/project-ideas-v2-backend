from django.shortcuts import render

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.permissions import AllowAny

from django.contrib.auth import authenticate

from django.db.models import Q

import os
from dotenv import load_dotenv

from app.serializers import ( 
    UserSerializer,
    IdeaSerializer
)

from app.models import (
    Idea,
    User,
)

load_dotenv()

# View for Admin Signup
class AdminSignupView(APIView):
    permission_classes = (AllowAny,)

    def post(self, request):
        req_data = request.data         

        # Hardcoded the password and email address
        if req_data['password']==os.getenv('ADMIN_PASSWORD') and req_data['email']==os.getenv('ADMIN_EMAIL_ID'):

            try:
                # Checking if Admin already signed up
                user = User.objects.get(email=req_data['email'])
                return Response({"message":"Admin already signed Up"}, status=status.HTTP_400_BAD_REQUEST)
            except User.DoesNotExist:
                # Creating superuser (Admin)
                serializer = UserSerializer(data=req_data)
                if serializer.is_valid():
                    User.objects.create_superuser(req_data['email'], req_data['password'])
                    return Response({"message":"Admin signed up"}, status=status.HTTP_200_OK)
                else:
                    return Response({"message":"Invalid Data"}, status=status.HTTP_400_BAD_REQUEST)

        else:            
            return Response({"message":"Invalid Email and Password"}, status=status.HTTP_400_BAD_REQUEST)

# VIew to Login Admin
class AdminLoginView(APIView):
    permission_classes = (AllowAny,)

    def post(self, request):
        req_data = request.data
        user = authenticate(email=req_data['email'], password=req_data['password'])
        if not user:
            return Response({"message":"Invalid Details"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            token, _ = Token.objects.get_or_create(user=user)
            return Response({
                "message":"Admin Logged In", 
                "Admin":{
                    "id":user.id,
                    "email":user.email,
                    "token":token.key
            }})

# View to Logout Admin
class AdminLogoutView(APIView):

    def get(self, request, format=None):
        user = request.user
        response = {
            "message":"Admin logged out", 
            "Details":{
                "id": user.id,
                "email":user.email
            }}
        request.user.auth_token.delete()
        return Response(response, status=status.HTTP_200_OK)

# View to Get unpublished ideas and Reviewing them
class UnpublishedIdeas(APIView):

    # Get unpublished ideas
    def get(self, request):
        user = request.user
        keys = {"PENDING":0, "PUBLISHED":1, "REJECTED":2}
        if user.is_staff==True and user.is_superuser==True:
            ideas = list(Idea.objects.filter(is_reviewed=keys['PENDING']))
            serializer = IdeaSerializer(ideas, many=True)
            return Response({"message":serializer.data}, status=status.HTTP_200_OK)
        else:
            return Response({"message":"Not an Admin"}, status=status.HTTP_403_FORBIDDEN)            

    # Review Unpublished Ideas
    def post(self, request):
        user = request.user
        req_data = request.data
        keys = {"PENDING":0, "PUBLISHED":1, "REJECTED":2}

        if user.is_staff==True and user.is_superuser==True:
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
        user = request.user
        req_data = request.data
        keys = {"PENDING":0, "PUBLISHED":1, "REJECTED":2}

        if user.is_staff==True and user.is_superuser==True:
            ideas = list(Idea.objects.filter(is_reviewed=keys['REJECTED']))
            serializer = IdeaSerializer(ideas, many=True)
            return Response({"message":serializer.data}, status=status.HTTP_200_OK)
        else:
            return Response({"message":"Not an Admin"}, status=status.HTTP_403_FORBIDDEN)            

# Get all Ideas (published, unpublished and rejected)
class AllIdeasView(APIView):

    def get(self, request):
        user = request.user
        req_data = request.data

        if user.is_staff==True and user.is_superuser==True:
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
            

