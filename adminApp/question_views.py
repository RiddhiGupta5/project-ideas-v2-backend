from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from django.db.models import Q
from app.helper_functions import get_user, get_token

import datetime
import pytz

from .models import Question, Answer
from .serializers import QuestionSerializer, AnswerSerializer

class QuestionView(APIView):

    def post(self, request):
        token = request.headers.get('Authorization', None)
        if token is None or token=="":
            return Response({"message":"Authorization credentials missing"}, status=status.HTTP_403_FORBIDDEN)
        
        user = get_user(token)
        if user is None:
            return Response({"message":"User Already Logged Out"}, status=status.HTTP_403_FORBIDDEN)

        if user.is_superuser==True:
            serializer = QuestionSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response({"message":serializer.data}, status=status.HTTP_200_OK)
            else:
                return Response({"message":"Invalid Question"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"message":"Not an Admin"}, status=status.HTTP_403_FORBIDDEN)   

    def get(self, request, pk):
        token = request.headers.get('Authorization', None)
        if token is None or token=="":
            return Response({"message":"Authorization credentials missing"}, status=status.HTTP_403_FORBIDDEN)
        
        user = get_user(token)
        if user is None:
            return Response({"message":"User Already Logged Out"}, status=status.HTTP_403_FORBIDDEN)

        try:
            question = Question.objects.get(id=pk)
            serializer = QuestionSerializer(question)
            return Response({"message":serializer.data}, status=status.HTTP_200_OK)
        except Question.DoesNotExist:
            return Response({"message":"Questions Does Not Exist"}, status=status.HTTP_400_BAD_REQUEST)
        
class AllQuestionsView(APIView):

    def get(self, request):
        token = request.headers.get('Authorization', None)
        if token is None or token=="":
            return Response({"message":"Authorization credentials missing"}, status=status.HTTP_403_FORBIDDEN)
        
        user = get_user(token)
        if user is None:
            return Response({"message":"User Already Logged Out"}, status=status.HTTP_403_FORBIDDEN)

        questions = Question.objects.all()
        if len(questions) == 0:
            return Response({"message":"No Questions Found"}, status=status.HTTP_204_NO_CONTENT)
        
        serializer = QuestionSerializer(questions, many=True)
        return Response({"message":serializer.data}, status=status.HTTP_200_OK)

class FilterQuestionDateView(APIView):

    def get(self, request):
        token = request.headers.get('Authorization', None)
        if token is None or token=="":
            return Response({"message":"Authorization credentials missing"}, status=status.HTTP_403_FORBIDDEN)
        
        user = get_user(token)
        if user is None:
            return Response({"message":"User Already Logged Out"}, status=status.HTTP_403_FORBIDDEN)

        date = request.query_params.get("date", None)
        if date==None or date=="":
            return Response({"message":"Date missing"}, status=status.HTTP_400_BAD_REQUEST)
        
        date = date.split('-')
        day = int(date[0])
        month = int(date[1])
        year = int(date[2])
        questions = Question.objects.filter(date_time__date=datetime.date(year, month, day))
        serializer = QuestionSerializer(questions, many=True)

        if len(serializer.data)==0:
            return Response({"message":"No Question Found"}, status=status.HTTP_204_NO_CONTENT)

        return Response({"message":serializer.data}, status=status.HTTP_200_OK)

class LatestQuestionView(APIView):

    def get(self, request):
        date = datetime.datetime.now(pytz.utc)
        questions = Question.objects.all()
        serializer = QuestionSerializer(questions, many=True)
        result = serializer.data
        if len(result)!=0:
            return Response({"message":"Latest Question", "Question":result[0]}, status=status.HTTP_200_OK)
        else:
            return Response({"message":"No questions found"}, status=status.HTTP_204_NO_CONTENT)
        # min = 1000
        # if len(questions)==0:
        #     return Response({"message":"No questions found"}, status=status.HTTP_204_NO_CONTENT)
        # result = questions[0]
        # for question in questions:
        #     quest_date = question.date_time
        #     diff = (date - quest_date).seconds
        #     print(diff)
        #     if diff<min:
        #         min = diff
        #         result = question
        
        # if result:
        #     serializer = QuestionSerializer(result)
        #     return Response({"message":"Latest Question", "Question":serializer.data}, status=status.HTTP_200_OK)
        # else:
        #     return Response({"message":"No questions found"}, status=status.HTTP_204_NO_CONTENT)