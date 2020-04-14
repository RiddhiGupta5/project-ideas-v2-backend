from django.shortcuts import render

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .helper_functions import get_user

from django.db.models import Q

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

        if token is None or token=="":
            return Response({"message":"Authorization credentials missing"}, status=status.HTTP_403_FORBIDDEN)
        
        user = get_user(token)
        if user is None:
            return Response({"message":"User Not Allowed"}, status=status.HTTP_403_FORBIDDEN)

        data = {}
        data['project_title'] = request.data.get("project_title", None)
        data['project_description'] = request.data.get("project_description", None)
        data['tags'] =request.data.get("tags", None)
        data['user_id'] = user.id

        serializer = IdeaSerializer(data = data)

        if serializer.is_valid():
            serializer.save()
            return Response({"message":serializer.data}, status=status.HTTP_200_OK)
        else:
            return Response({"message": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

# View for getting all published ideas
class PublishedIdeasView(APIView):

    def get(self, request):
        keys = {"PENDING":0, "PUBLISHED":1, "REJECTED":2}
        ideas = list(Idea.objects.filter(is_reviewed=keys["PUBLISHED"]))
        serializers = (IdeaSerializer(ideas, many=True))

        if len(ideas) == 0:
            return Response({"message":"No Published Ideas found"}, status=status.HTTP_204_NO_CONTENT)

        serializer_data = serializers.data

        for idea in serializer_data:
            user = User.objects.get(id=idea['user_id'])
            idea['username'] = user.username

        return Response({"message":serializer_data}, status=status.HTTP_200_OK)

# View for getting details for a particular idea
class ViewIdea(APIView):

    def get(self, request, pk):
        try:
            idea = Idea.objects.get(id=pk)
            serializer = IdeaSerializer(idea)
            serializer = serializer.data
            user = User.objects.get(id=idea.user_id.id)
            serializer['username'] = user.username
            return Response({"message":serializer}, status=status.HTTP_200_OK)
        except Idea.DoesNotExist:
            return Response({"message":"Idea not found or Invalid id number"}, status=status.HTTP_204_NO_CONTENT)

class SearchIdeaByContent(APIView):

    def get(self, request):
        keys = {"PENDING":0, "PUBLISHED":1, "REJECTED":2}
        text = request.query_params.get("text", None)
        print(text)
        all_ideas = list(Idea.objects.filter(
            Q(is_reviewed=keys['PUBLISHED']) & 
            (Q(project_title__icontains=text) | Q(project_description__icontains=text) | Q(tags__icontains=text))).all())
        search_result = all_ideas
        
        if len(search_result)==0:
            return Response({"message":"No Idea found"}, status=204)

        serializer = IdeaSerializer(search_result, many=True)
        serializer_data = serializer.data

        for idea in serializer_data:
            user = User.objects.get(id=idea['user_id'])
            idea['username'] = user.username

        return Response({"message":serializer_data}, status=status.HTTP_200_OK)
            
        
        