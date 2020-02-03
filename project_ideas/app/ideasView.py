from django.shortcuts import render

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny

from fuzzywuzzy import fuzz

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
        ideas = list(Idea.objects.filter(is_reviewed=keys['PUBLISHED']))

        print(text)

        if not text:            
            return Response({"message":"Please provide text"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            for idea in ideas:
                response = []
                token_set_ratio_title = fuzz.token_set_ratio(idea.project_title, text)
                token_set_ratio_description = fuzz.token_set_ratio(idea.project_description, text)
                if token_set_ratio_title > 60 or token_set_ratio_description > 60:
                    serializer = IdeaSerializer(idea)
                    response.append(serializer.data)
            return Response({"message":response}, status=status.HTTP_200_OK)
            
        
        