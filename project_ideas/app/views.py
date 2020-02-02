from django.shortcuts import render

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.permissions import AllowAny

from social_django.utils import load_strategy, load_backend
from social_core.exceptions import MissingBackend, AuthTokenError, AuthForbidden
from social_core.backends.oauth import BaseOAuth2

from requests.exceptions import HTTPError
from django.forms.models import model_to_dict

from .serializers import (
    SocialSerializer,
    AdminSignupSerializer, 
    UserSerializer, 
    IdeaSerializer,
    CommentSerializer
)

from .models import (
    Idea,
    Comment,
    User
)


class SocialLoginView(APIView):
    permission_classes = (AllowAny,)

    def post(self, request):
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
            user = backend.do_auth(access_token)
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
            token, _ = Token.objects.get_or_create(user=user)
            response = {
                "id": user.id,
                "email": authenticated_user.email,
                "username": authenticated_user.username,                
                "token":token.key
            }
            return Response(status=status.HTTP_200_OK, data=response)


class SocialLogoutView(APIView):

    def get(self, request, format=None):
        user = request.user
        response = {
            "message":"User logged out", 
            "Details":{
                "id": user.id,
                "username": user.username,
                "email": user.email
            }}
        request.user.auth_token.delete()
        return Response(response, status=status.HTTP_200_OK)
            

class PostIdeaView(APIView):
    permission_classes = (AllowAny,)

    def post(self, request):
        serializer = IdeaSerializer(data = request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message":serializer.data}, status=status.HTTP_200_OK)
        else:
            return Response({"message": "Invalid Idea Posted"}, status=status.HTTP_400_BAD_REQUEST)


class PublishedIdeasView(APIView):
    permission_classes = (AllowAny,)

    def get(self, request):
        ideas = list(Idea.objects.filter(is_reviewed=1))
        serializers = (IdeaSerializer(ideas, many=True))
        if len(ideas) == 0:
            return Response({"message":"No Published Ideas found"}, status=status.HTTP_204_NO_CONTENT)
        return Response({"message":serializers.data}, status=status.HTTP_200_OK)


class ViewIdea(APIView):
    permission_classes = (AllowAny,)

    def get(self, request, pk):
        try:
            idea = Idea.objects.get(id=pk)
            serializer = IdeaSerializer(idea)
            return Response({"message":serializer.data}, status=status.HTTP_200_OK)
        except Idea.DoesNotExist:
            return Response({"message":"Idea not found or Invalid id number"}, status=status.HTTP_204_NO_CONTENT)