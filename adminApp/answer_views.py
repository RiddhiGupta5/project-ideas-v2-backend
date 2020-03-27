from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import ParseError
from rest_framework.parsers import FileUploadParser

from django.db.models import Q
from app.helper_functions import get_user, get_token

import datetime
import pyexcel

from .models import Question, Answer
from .serializers import QuestionSerializer, AnswerSerializer


class AnswerView(APIView):

    def post(self, request):
        token = request.headers.get('Authorization', None)
        if token is None or token=="":
            return Response({"message":"Authorization credentials missing"}, status=status.HTTP_403_FORBIDDEN)
        
        user = get_user(token)
        if user is None:
            return Response({"message":"User Already Logged Out"}, status=status.HTTP_403_FORBIDDEN)

        req_data = {}
        req_data['answer_body'] = request.data.get("answer_body", None)
        req_data['answer_type'] = request.data.get("answer_type", None)
        req_data['daily_challenge'] = request.data.get("daily_challenge", None)
        req_data['weekly_challenge'] = request.data.get("weekly_challenge", None)
        req_data['user_id'] = user.id

        if req_data['daily_challenge'] and req_data['weekly_challenge']:
            return Response({"message":"Invlaid Answer"}, status=status.HTTP_400_BAD_REQUEST)

        serializer = AnswerSerializer(data=req_data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message":"Answer Saved", "Answer":serializer.data}, status=status.HTTP_200_OK)
        else:
            return Response({"message":"Invalid Answer"}, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request, pk):
        token = request.headers.get('Authorization', None)
        if token is None or token=="":
            return Response({"message":"Authorization credentials missing"}, status=status.HTTP_403_FORBIDDEN)
        
        user = get_user(token)
        if user is None:
            return Response({"message":"User Already Logged Out"}, status=status.HTTP_403_FORBIDDEN)

        try:
            answer = Answer.objects.get(id=pk)
            serializer = AnswerSerializer(answer)
            return Response({"message":serializer.data}, status=status.HTTP_200_OK)
        except Answer.DoesNotExist:
            return Response({"message":"Answers Does Not Exist"}, status=status.HTTP_400_BAD_REQUEST)


class AllAnswersView(APIView):

    def get(self, request, pk):
        token = request.headers.get('Authorization', None)
        if token is None or token=="":
            return Response({"message":"Authorization credentials missing"}, status=status.HTTP_403_FORBIDDEN)
        
        user = get_user(token)
        if user is None:
            return Response({"message":"User Already Logged Out"}, status=status.HTTP_403_FORBIDDEN)

        if user.is_superuser==True:
            answers = Answer.objects.all()
            if len(answers) == 0:
                return Response({"message":"No Answers Found"}, status=status.HTTP_204_NO_CONTENT)
            
            serializer = AnswerSerializer(answers, many=True)
            return Response({"message":serializer.data}, status=status.HTTP_200_OK)
        else:
            return Response({"message":"Not an Admin"}, status=status.HTTP_403_FORBIDDEN)  

class FilterAnswerDateView(APIView):

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
        answers = Answer.objects.filter(date_time__date=datetime.date(year, month, day))
        serializer = AnswerSerializer(answers, many=True)

        if len(serializer.data)==0:
            return Response({"message":"No Answer Found"}, status=status.HTTP_204_NO_CONTENT)

        return Response({"message":serializer.data}, status=status.HTTP_200_OK)


class MarksView(APIView):

    def post(self, request):
        token = request.headers.get('Authorization', None)
        if token is None or token=="":
            return Response({"message":"Authorization credentials missing"}, status=status.HTTP_403_FORBIDDEN)
        
        user = get_user(token)
        if user is None:
            return Response({"message":"User Already Logged Out"}, status=status.HTTP_403_FORBIDDEN)

        if user.is_superuser==True:
            req_data = request.data
            try:
                answer = Answer.objects.get(id=req_data['answer_id'])
                answer_type = req_data.get('answer_type', None)
                marks = eq_data.data.get("marks", None)
                if answer_type==0:
                   answer.marks = 1
                elif answer_type==1:
                    if marks==None or marks=="":
                        return Response({"message":"Invalid Data"}, status=status.HTTP_400_BAD_REQUEST)
                    answer.marks = marks
                else:
                    return Response({"message":"Invalid Data"}, status=status.HTTP_400_BAD_REQUEST)
                
                answer.save()
                serializer = AnswerSerializer(answer)
                return Response({"message":"Marks Saved", "Answer":serializer.data}, status=status.HTTP_200_OK)

            except Answer.DoesNotExist:
                return Response({"message":"ANswer Does Not Exist"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"message":"Not an Admin"}, status=status.HTTP_403_FORBIDDEN)

class ExcelSheetView(APIView):
    parser_class = (FileUploadParser,)

    def post(self, request):
        if 'file' not in request.data:
            raise ParseError("Empty content")

        file = request.data['file']
        extension = file.name.split('.')[-1]
        if extension not in ['csv', 'xls', 'xlsx']:
            return Response({"message":"Invalid File Format"}, status=status.HTTP_400_BAD_REQUEST)

        content = file.read()
        print(content)
        return Response({"message":"file content"}, status=status.HTTP_200_OK)
        



