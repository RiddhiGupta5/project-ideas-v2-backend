from django.shortcuts import render

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.permissions import AllowAny

from social_django.utils import load_strategy, load_backend
from social_core.exceptions import MissingBackend, AuthTokenError, AuthForbidden
from social_core.backends.oauth import BaseOAuth2

from app.serializers import (
    SocialSerializer
)

from .models import User

from .ideasView import (
    PostIdeaView,
    PublishedIdeasView,
    ViewIdea,
)

from .voteAndCommentViews import (
    VoteView,
    CommentView,
)

# View for Social Login 
class SocialLoginView(APIView):
    permission_classes = (AllowAny,)

    def post(self, request):
        #Validating and getting data from request
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
            token, _ = Token.objects.get_or_create(user=user)
            response = {
                "id": user.id,
                "email": user.email,                
                "token":token.key
            }
            return Response(status=status.HTTP_200_OK, data=response)

# View for Social Logout
class SocialLogoutView(APIView):

    def get(self, request, format=None):
        # Get User and delete the token
        user = request.user
        response = {
            "message":"User logged out", 
            "Details":{
                "id": user.id,
                "email": user.email
            }}
        request.user.auth_token.delete()
        return Response(response, status=status.HTTP_200_OK)