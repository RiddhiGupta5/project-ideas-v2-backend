import datetime
import hashlib
import os

from django.db.models import Q
from django.shortcuts import render
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from app.helper_functions import get_token, get_user
from app.models import Idea, User, UserToken
from app.serializers import IdeaSerializer


# View to Get unpublished ideas and Reviewing them


class UnpublishedIdeas(APIView):

    # Get unpublished ideas
    def get(self, request):
        token = request.headers.get('Authorization', None)
        if token is None or token == "":
            return Response({"message": "Authorization credentials missing"}, status=status.HTTP_403_FORBIDDEN)

        user = get_user(token)
        if user is None:
            return Response({"message": "User Already Logged Out"}, status=status.HTTP_403_FORBIDDEN)

        offset = request.query_params.get('offset', None)
        if offset != None and offset != "":
            offset = int(offset)
            start = offset * 5
            end = (offset + 1) * 5

        keys = {"PENDING": 0, "PUBLISHED": 1, "REJECTED": 2}
        if user.is_superuser == True:
            ideas = list(Idea.objects.filter(
                is_reviewed=keys['PENDING'], is_deleted=False))
            serializer = IdeaSerializer(ideas, many=True)

            if offset == None or offset == "":
                serializer_data = serializer.data
            else:
                serializer_data = serializer.data[start:end]

            if len(serializer_data) == 0:
                return Response({"message": "No Idea Found"}, status=status.HTTP_204_NO_CONTENT)

            for idea in serializer_data:
                user = User.objects.get(id=idea['user_id'])
                idea['username'] = user.username

            return Response({"message": serializer_data}, status=status.HTTP_200_OK)
        else:
            return Response({"message": "Not an Admin"}, status=status.HTTP_403_FORBIDDEN)

    # Review Unpublished Ideas
    def post(self, request):
        token = request.headers.get('Authorization', None)
        if token is None or token == "":
            return Response({"message": "Authorization credentials missing"}, status=status.HTTP_403_FORBIDDEN)

        user = get_user(token)
        if user is None:
            return Response({"message": "User Already Logged Out"}, status=status.HTTP_403_FORBIDDEN)

        req_data = request.data
        keys = {"PENDING": 0, "PUBLISHED": 1, "REJECTED": 2}

        if user.is_superuser == True:
            try:
                idea = Idea.objects.get(id=req_data['idea_id'])
                idea.is_reviewed = req_data['is_reviewed']
                idea.reviewer_id = user
                idea.save()
                serializer = IdeaSerializer(idea)
                return Response({"message": "Idea reviewed successfully", "idea": serializer.data}, status=status.HTTP_200_OK)
            except:
                return Response({"message": "Invalid Idea Id"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"message": "Only Admin can Access"}, status=status.HTTP_403_FORBIDDEN)

# View to get rejected ideas


class RejectedIdeasView(APIView):

    def get(self, request):
        token = request.headers.get('Authorization', None)
        if token is None or token == "":
            return Response({"message": "Authorization credentials missing"}, status=status.HTTP_403_FORBIDDEN)

        user = get_user(token)
        if user is None:
            return Response({"message": "User Already Logged Out"}, status=status.HTTP_403_FORBIDDEN)

        offset = request.query_params.get('offset', None)
        if offset != None and offset != "":
            offset = int(offset)
            start = offset * 5
            end = (offset + 1) * 5

        req_data = request.data
        keys = {"PENDING": 0, "PUBLISHED": 1, "REJECTED": 2}

        if user.is_superuser == True:
            ideas = list(Idea.objects.filter(
                is_reviewed=keys['REJECTED'], is_deleted=False))
            serializer = IdeaSerializer(ideas, many=True)

            if offset == None or offset == "":
                serializer_data = serializer.data
            else:
                serializer_data = serializer.data[start:end]

            if len(serializer_data) == 0:
                return Response({"message": "No Idea Found"}, status=status.HTTP_204_NO_CONTENT)

            for idea in serializer_data:
                user = User.objects.get(id=idea['user_id'])
                idea['username'] = user.username

            return Response({"message": serializer_data}, status=status.HTTP_200_OK)
        else:
            return Response({"message": "Not an Admin"}, status=status.HTTP_403_FORBIDDEN)


class DeletedIdeasView(APIView):

    def get(self, request):
        token = request.headers.get('Authorization', None)
        if token is None or token == "":
            return Response({"message": "Authorization credentials missing"}, status=status.HTTP_403_FORBIDDEN)

        user = get_user(token)
        if user is None:
            return Response({"message": "User Already Logged Out"}, status=status.HTTP_403_FORBIDDEN)

        offset = request.query_params.get('offset', None)
        if offset != None and offset != "":
            offset = int(offset)
            start = offset * 5
            end = (offset + 1) * 5

        req_data = request.data
        keys = {"PENDING": 0, "PUBLISHED": 1, "REJECTED": 2}

        if user.is_superuser == True:
            ideas = list(Idea.objects.filter(is_deleted=True))
            serializer = IdeaSerializer(ideas, many=True)

            if offset == None or offset == "":
                serializer_data = serializer.data
            else:
                serializer_data = serializer.data[start:end]

            if len(serializer_data) == 0:
                return Response({"message": "No Idea Found"}, status=status.HTTP_204_NO_CONTENT)

            for idea in serializer_data:
                user = User.objects.get(id=idea['user_id'])
                idea['username'] = user.username

            return Response({"message": serializer_data}, status=status.HTTP_200_OK)
        else:
            return Response({"message": "Not an Admin"}, status=status.HTTP_403_FORBIDDEN)


# Get all Ideas (published, unpublished and rejected)
class AllIdeasView(APIView):

    def get(self, request):
        token = request.headers.get('Authorization', None)
        if token is None or token == "":
            return Response({"message": "Authorization credentials missing"}, status=status.HTTP_403_FORBIDDEN)

        user = get_user(token)
        if user is None:
            return Response({"message": "User Already Logged Out"}, status=status.HTTP_403_FORBIDDEN)

        offset = request.query_params.get('offset', None)
        if offset != None and offset != "":
            offset = int(offset)
            start = offset * 5
            end = (offset + 1) * 5

        req_data = request.data

        if user.is_superuser == True:
            ideas = list(Idea.objects.all())
            serializer = IdeaSerializer(ideas, many=True)

            if offset == None or offset == "":
                serializer_data = serializer.data
            else:
                serializer_data = serializer.data[start:end]

            if len(serializer_data) == 0:
                return Response({"message": "No Idea Found"}, status=status.HTTP_204_NO_CONTENT)

            for idea in serializer_data:
                user = User.objects.get(id=idea['user_id'])
                idea['username'] = user.username

            return Response({"message": serializer_data}, status=status.HTTP_200_OK)
        else:
            return Response({"message": "Not an Admin"}, status=status.HTTP_403_FORBIDDEN)


class SearchAllIdeaByContent(APIView):

    def get(self, request):

        offset = request.query_params.get('offset', None)
        if offset != None and offset != "":
            offset = int(offset)
            start = offset * 5
            end = (offset + 1) * 5

        text = request.query_params.get("text", None)
        print(text)
        all_ideas = list(Idea.objects.filter(Q(project_title__icontains=text) | Q(
            project_description__icontains=text) | Q(tags__icontains=text)).all())
        search_result = all_ideas

        if len(search_result) == 0:
            return Response({"message": "No Idea found"}, status=204)

        serializer = IdeaSerializer(search_result, many=True)

        if offset == None or offset == "":
            serializer_data = serializer.data
        else:
            serializer_data = serializer.data[start:end]

        if len(serializer_data) == 0:
            return Response({"message": "No Idea Found"}, status=status.HTTP_204_NO_CONTENT)

        return Response({"message": serializer_data}, status=status.HTTP_200_OK)


class CompletedIdeasView(APIView):

    def patch(self, request):
        token = request.headers.get('Authorization', None)
        if token is None or token == "":
            return Response({"message": "Authorization credentials missing"}, status=status.HTTP_403_FORBIDDEN)

        user = get_user(token)
        if user is None:
            return Response({"message": "User Already Logged Out"}, status=status.HTTP_403_FORBIDDEN)

        if user.is_superuser == True:
            idea = Idea.objects.get(id=request.data.get('id', None))
            repo_link = request.data.get('repo_link', None)
            if repo_link == None or repo_link == "":
                return Response({"message": "Github Repository Link required"}, status=status.HTTP_400_BAD_REQUEST)
            idea.repo_link = repo_link
            idea.is_completed = True
            idea.save()
            idea_serializer = IdeaSerializer(idea)
            return Response({"message": "Idea successfully marked as completed", "Idea": idea_serializer.data}, status=status.HTTP_200_OK)

        else:
            return Response({"message": "Not an Admin"}, status=status.HTTP_403_FORBIDDEN)

    def get(self, request):
        # View First 5 ideas on home page
        NO_OF_IDEAS = 6
        ideas = Idea.objects.filter(is_completed=True)
        idea_serializer = IdeaSerializer(ideas, many=True)
        return Response({"message": "Completed Ideas", "Ideas": idea_serializer.data[0:NO_OF_IDEAS]}, status=status.HTTP_200_OK)
