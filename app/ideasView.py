from django.shortcuts import render

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny

from django.db.models import Q

from app.serializers import ( 
    IdeaSerializer,
    
)

from .models import (
    Idea
)

# View for Posting Ideas
class PostIdeaView(APIView):
    permission_classes = (AllowAny,)

    def post(self, request):
        serializer = IdeaSerializer(data = request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message":serializer.data}, status=status.HTTP_200_OK)
        else:
            return Response({"message": "Invalid Idea Posted"}, status=status.HTTP_400_BAD_REQUEST)

# View for getting all published ideas
class PublishedIdeasView(APIView):
    permission_classes = (AllowAny,)

    def get(self, request):
        keys = {"PENDING":0, "PUBLISHED":1, "REJECTED":2}
        ideas = list(Idea.objects.filter(is_reviewed=keys["PUBLISHED"]))
        serializers = (IdeaSerializer(ideas, many=True))
        if len(ideas) == 0:
            return Response({"message":"No Published Ideas found"}, status=status.HTTP_204_NO_CONTENT)
        return Response({"message":serializers.data}, status=status.HTTP_200_OK)

# View for getting details for a particular idea
class ViewIdea(APIView):
    permission_classes = (AllowAny,)

    def get(self, request, pk):
        try:
            idea = Idea.objects.get(id=pk)
            serializer = IdeaSerializer(idea)
            return Response({"message":serializer.data}, status=status.HTTP_200_OK)
        except Idea.DoesNotExist:
            return Response({"message":"Idea not found or Invalid id number"}, status=status.HTTP_204_NO_CONTENT)

class SearchIdeaByContent(APIView):
    permission_classes = (AllowAny,)

    def get(self, request):
        keys = {"PENDING":0, "PUBLISHED":1, "REJECTED":2}
        text = request.query_params.get("text", None)
        print(text)
        all_ideas = list(Idea.objects.filter(
            Q(is_reviewed=keys['PUBLISHED']) & 
            (Q(project_title__icontains=text) | Q(project_description__icontains=text))).all())
        search_result = all_ideas
        
        if len(search_result)==0:
            return Response({"message":"No Idea found"}, status=204)

        serializer = IdeaSerializer(search_result, many=True)
        serializer_data = serializer.data

        return Response({"message":serializer_data}, status=status.HTTP_200_OK)
            
        
        