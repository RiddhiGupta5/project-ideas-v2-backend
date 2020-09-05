import datetime
from django.shortcuts import render

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .helper_functions import get_user

from django.db.models import Q
from math import ceil

from app.serializers import (
    IdeaSerializer,

)

from .models import (
    Idea,
    User
)

# View for Posting Ideas


class PostIdeaView(APIView):

    def post(self, request):

        token = request.headers.get('Authorization', None)

        if token is None or token == "":
            return Response({"message": "Authorization credentials missing"}, status=status.HTTP_403_FORBIDDEN)

        user = get_user(token)
        if user is None:
            return Response({"message": "You need to login to perform this action !"}, status=status.HTTP_403_FORBIDDEN)

        data = {}
        data['project_title'] = request.data.get("project_title", None)
        data['project_description'] = request.data.get(
            "project_description", None)
        data['tags'] = request.data.get("tags", None)
        data['user_id'] = user.id

        serializer = IdeaSerializer(data=data)

        if serializer.is_valid():
            serializer.save()
            return Response({"message": serializer.data}, status=status.HTTP_200_OK)
        else:
            return Response({"message": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

# View for getting all published ideas


class PublishedIdeasView(APIView):

    def get(self, request):

        offset = request.query_params.get('offset', None)
        if offset != None and offset != "":
            offset = int(offset)
            start = offset * 5
            end = (offset + 1) * 5

        total_pages = 0

        keys = {"PENDING": 0, "PUBLISHED": 1, "REJECTED": 2}
        ideas = list(Idea.objects.filter(
            is_deleted=False, is_reviewed=keys["PUBLISHED"]))
        serializers = (IdeaSerializer(ideas, many=True))

        if len(ideas) == 0:
            return Response({"message": "No Published Ideas Found", 'total_pages': total_pages}, status=status.HTTP_204_NO_CONTENT)

        total_pages = ceil(len(serializers.data)/5)

        if offset == None or offset == "":
            serializer_data = serializers.data
        else:
            serializer_data = serializers.data[start:end]

        if len(serializer_data) == 0:
            return Response({"message": "No Published Ideas Found", 'total_pages': total_pages}, status=status.HTTP_204_NO_CONTENT)

        for idea in serializer_data:
            user = User.objects.get(id=idea['user_id'])
            idea['username'] = user.username

        return Response({"message": serializer_data, 'total_pages': total_pages}, status=status.HTTP_200_OK)

# View for getting details for a particular idea


class ViewIdea(APIView):

    def get(self, request, pk):
        try:
            idea = Idea.objects.get(id=pk)
            serializer = IdeaSerializer(idea)
            serializer = serializer.data
            user = User.objects.get(id=idea.user_id.id)
            serializer['username'] = user.username
            return Response({"message": serializer}, status=status.HTTP_200_OK)
        except Idea.DoesNotExist:
            return Response({"message": "Idea not found or Invalid id number"}, status=status.HTTP_204_NO_CONTENT)


class SearchIdeaByContent(APIView):

    def get(self, request):
        """
        Request Format
        tag:
        date:
        is made real: true, false
        text:
        votes: desc, asc
        """

        offset = request.query_params.get('offset', None)
        if offset != None and offset != "":
            offset = int(offset)
            start = offset * 5
            end = (offset + 1) * 5

        total_pages = 0

        keys = {"PENDING": 0, "PUBLISHED": 1, "REJECTED": 2}
        text = request.query_params.get("text", None)
        tag = request.query_params.get("tag", None)
        date = request.query_params.get("date", None)
        is_made_real = request.query_params.get("is_made_real", None)
        votes = request.query_params.get("votes", None)
        sort = request.query_params.get("sort", None)
        print(text)
        all_ideas = Idea.objects.filter(
            Q(is_reviewed=keys['PUBLISHED']) & Q(is_deleted=False)).all()
        if text != None and text != "":
            all_ideas = all_ideas.filter((Q(project_title__icontains=text) | Q(
                project_description__icontains=text) | Q(tags__icontains=text)))
        if tag != None and tag != "":
            all_ideas = all_ideas.filter(Q(tags__icontains=tag))
        if date != None and date != "":
            # YYYY-mm-dd
            date = date.split('-')
            day = int(date[2])
            month = int(date[1])
            year = int(date[0])
            all_ideas = all_ideas.filter(
                date_time__date=datetime.date(year, month, day))
        if is_made_real != None and is_made_real != "":
            all_ideas = all_ideas.filter(is_completed=is_made_real)
        if (votes != None and votes != ""):
            if votes.lower() == "desc":
                all_ideas = all_ideas.order_by('-votes')
            elif votes.lower() == "asc":
                all_ideas = all_ideas.order_by('votes')
        if sort != None and sort != "":
            if sort.lower() == "new":
                # Latest on top
                all_ideas = all_ideas.order_by('-date_time')
            elif sort.lower() == "old":
                # Oldest on top
                all_ideas = all_ideas.order_by('date_time')

        search_result = all_ideas

        if len(search_result) == 0:
            return Response({"message": "No Idea found", 'total_pages': total_pages}, status=204)

        serializer = IdeaSerializer(search_result, many=True)

        total_pages = ceil(len(serializer.data)/5)

        if offset == None or offset == "":
            serializer_data = serializer.data
        else:
            serializer_data = serializer.data[start:end]

        if len(serializer_data) == 0:
            return Response({"message": "No Idea Found", 'total_pages': total_pages}, status=status.HTTP_204_NO_CONTENT)

        for idea in serializer_data:
            user = User.objects.get(id=idea['user_id'])
            idea['username'] = user.username

        return Response({"message": serializer_data, 'total_pages': total_pages}, status=status.HTTP_200_OK)


class UserIdeaView(APIView):

    def get(self, request):
        token = request.headers.get('Authorization', None)

        if token is None or token == "":
            return Response({"message": "Authorization credentials missing"}, status=status.HTTP_403_FORBIDDEN)

        user = get_user(token)
        if user is None:
            return Response({"message": "You need to login to perform this action !"}, status=status.HTTP_403_FORBIDDEN)

        offset = request.query_params.get('offset', None)
        if offset != None and offset != "":
            offset = int(offset)
            start = offset * 5
            end = (offset + 1) * 5

        total_pages = 0

        user_ideas = Idea.objects.filter(user_id=user.id, is_deleted=False)
        serializer = IdeaSerializer(user_ideas, many=True)
        total_pages = ceil(len(serializer.data)/5)

        if offset == None or offset == "":
            serializer_data = serializer.data
        else:
            serializer_data = serializer.data[start:end]

        if len(serializer_data) == 0:
            return Response({"message": "No Idea Found", 'total_pages': total_pages}, status=status.HTTP_204_NO_CONTENT)

        return Response({"message": serializer_data, 'total_pages': total_pages}, status=status.HTTP_200_OK)

    def delete(self, request, pk):
        token = request.headers.get('Authorization', None)

        if token is None or token == "":
            return Response({"message": "Authorization credentials missing"}, status=status.HTTP_403_FORBIDDEN)

        user = get_user(token)
        if user is None:
            return Response({"message": "You need to login to perform this action !"}, status=status.HTTP_403_FORBIDDEN)

        try:
            idea = Idea.objects.get(id=pk, is_deleted=False)
            if idea.user_id.id == user.id:
                idea.is_deleted = True
                idea.save()
                serializer = IdeaSerializer(idea)
                return Response({'message': serializer.data}, status=status.HTTP_200_OK)
            else:
                return Response({"message": "You are not allowed to delete this idea!"}, status=status.HTTP_403_FORBIDDEN)
        except Idea.DoesNotExist:
            return Response({"message": "Idea not Found"}, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request):
        token = request.headers.get('Authorization', None)

        if token is None or token == "":
            return Response({"message": "Authorization credentials missing"}, status=status.HTTP_403_FORBIDDEN)

        user = get_user(token)
        if user is None:
            return Response({"message": "You need to login to perform this action !"}, status=status.HTTP_403_FORBIDDEN)

        pk = request.data.get('id', None)
        project_title = request.data.get('project_title', None)
        project_description = request.data.get('project_description', None)
        tags = request.data.get('tags', None)

        if not(pk) or not(project_title) or not(project_description) or not(tags):
            return Response({"message": "Please Provide all fields"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            idea = Idea.objects.get(id=pk, is_deleted=False)
            idea_dict = {}
            if idea.user_id.id == user.id:
                idea.project_title = project_title
                idea.project_description = project_description
                idea.tags = tags
                idea.is_reviewed = 0
                idea_dict['project_title'] = project_title
                idea_dict['project_description'] = project_description
                idea_dict['tags'] = tags
                idea_dict['id'] = idea.id
                idea_dict['is_reviewed'] = 0
                idea_dict['user_id'] = user.id
                serializer = IdeaSerializer(data=idea_dict)
                if serializer.is_valid():
                    idea.save()
                    return Response({'message': idea_dict}, status=status.HTTP_200_OK)
                else:
                    return Response({'message': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({"message": "You are not allowed to delete this idea!"}, status=status.HTTP_403_FORBIDDEN)
        except Idea.DoesNotExist:
            return Response({"message": "Idea not Found"}, status=status.HTTP_400_BAD_REQUEST)
