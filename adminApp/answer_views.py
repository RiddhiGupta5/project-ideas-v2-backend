import datetime
import os

import pyexcel
import xlrd
from django.db.models import Q
from rest_framework import status
from rest_framework.exceptions import ParseError
from rest_framework.parsers import FileUploadParser
from rest_framework.response import Response
from rest_framework.views import APIView

from app.helper_functions import get_token, get_user
from app.models import User
from app.serializers import UserSerializer

from .models import Answer, Question
from .serializers import AnswerSerializer, QuestionSerializer


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

        answer = Answer.objects.filter(
            Q(user_id=user.id) & 
            Q(Q(daily_challenge=req_data['daily_challenge']) | Q(weekly_challenge=req_data['weekly_challenge'])))
        if len(answer)!=0:
            answer = answer[0]
            if answer.answer_type==1 and req_data['answer_body']!=None and answer.evaluated==False:
                answer.answer_body = req_data['answer_body']
                answer.save()
                serializer = AnswerSerializer(answer)
                return Response({"message":"Answer saved", "Answer":serializer.data}, status=status.HTTP_200_OK)
            else:
                return Response({"message":"Already Answered"}, status=status.HTTP_400_BAD_REQUEST)

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

    def get(self, request):
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

class UnevaluatedAnswersView(APIView):

    def get(self, request):
        token = request.headers.get('Authorization', None)
        if token is None or token=="":
            return Response({"message":"Authorization credentials missing"}, status=status.HTTP_403_FORBIDDEN)
        
        user = get_user(token)
        if user is None:
            return Response({"message":"User Already Logged Out"}, status=status.HTTP_403_FORBIDDEN)

        if user.is_superuser==True:
            answers = Answer.objects.filter(evaluated=False)
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

        if user.is_superuser==False:
            return Response({"message":"Not an Admin"}, status=status.HTTP_403_FORBIDDEN)  
        
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
                if answer.evaluated==True:
                    return Response({"message":"Answer Already Evaluated"}, status=status.HTTP_400_BAD_REQUEST)
                marks = req_data.get("marks", None)
                if marks==None or marks=="":
                    return Response({"message":"Please provide marks"}, status=status.HTTP_400_BAD_REQUEST)
                answer.marks = marks 
                answer.evaluated = True               
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
        token = request.headers.get('Authorization', None)
        if token is None or token=="":
            return Response({"message":"Authorization credentials missing"}, status=status.HTTP_403_FORBIDDEN)
        
        user = get_user(token)
        if user is None:
            return Response({"message":"User Already Logged Out"}, status=status.HTTP_403_FORBIDDEN)

        if user.is_superuser==False:
            return Response({"message":"Not an Admin"}, status=status.HTTP_403_FORBIDDEN) 

        if 'file' not in request.data:
            return Response({"message":"File Missing"}, status=status.HTTP_400_BAD_REQUEST)

        

        file = request.data['file']
        extension = file.name.split('.')[-1]
        if extension not in ['csv', 'xls', 'xlsx']:
            return Response({"message":"Invalid File Format"}, status=status.HTTP_400_BAD_REQUEST)

        content = file.read()
        records = pyexcel.iget_records(file_type=extension, file_content=content)
        print("____________________________________________________________________")
        for record in records:

            #####   USERNAME   ########
            username = record.get('username', None)
            if username=="":
                print("LOGS: USER -> Username Missing")
                continue

            #####   QUESTION   ########
            daily_challenge = record.get('daily_challenge', None)
            if daily_challenge=="":
                print("LOGS: QUESTION -> Question Missing")
                continue
            try:
                question = Question.objects.get(id=daily_challenge)
            except Question.DoesNotExist:
                print("LOGS: QUESTION -> Question Not Found")
                continue

            #####   EMAIL   ########
            email = record.get('email', None)
            if email=="":
                email=None

            #####   ANSWER   ########
            answer_body = record.get('answer_body', None)
            if answer_body=="":
                answer_body=None
            platform = 1

            user = User.objects.filter(Q(username__iexact=username) & Q(platform=platform))
            if len(user)!=0:
                user = user[0]
                answer = {
                    "answer_type":0,
                    "answer_body":answer_body,
                    "daily_challenge":question.id,
                    "user_id":user.id
                }
                
            else:
                user_data = {
                    "username":username,
                    "email":email,
                    "platform":platform
                }
                user_serializer = UserSerializer(data=user_data)
                if user_serializer.is_valid():
                    user_serializer.save()
                    user = User.objects.filter(Q(username__iexact=username) & Q(platform=platform))
                    user = user[0]
                    answer = {
                        "answer_type":0,
                        "answer_body":answer_body,
                        "daily_challenge":question.id,
                        "user_id":user.id
                    }
                    print("LOGS: USER -> New User created username = " + username)
                else:
                    print("LOGS: USER -> Invalid user username = " + username)
                    print(user_serializer.errors)

            try:
                stored_answer = Answer.objects.get(user_id=answer['user_id'], daily_challenge=question.id)
                print("LOGS: ANSWER -> Answer Already Stored for user " + username)

            except:
                serializer = AnswerSerializer(data=answer)
                if serializer.is_valid():
                    serializer.save()
                    print("LOGS: ANSWER -> Answer stored for " + username)
                else:
                    print("LOGS: ANSWER -> Invalid Answer of " + username)

        print("____________________________________________________________________")
        return Response({"message":"Records saved succesfully"}, status=status.HTTP_200_OK)


class LeaderBoardView(APIView):

    def get(self, request):
        result = []
        users = User.objects.all()
        for user in users:
            answers = Answer.objects.filter(user_id=user.id)
            marks = 0
            for answer in answers:
                marks = marks + answer.marks
            user_data = {
                "username":user.username,
                "platform":user.platform,
                "marks":marks * 100
            }
            result.append(user_data)
        result = sorted(result, key=lambda k: k['marks'], reverse=True)
        last_marks = result[0]['marks']
        key = 1
        last_position = 1
        admin = None
        toppers = [1, 2, 3]
        for item in result:
            if item['username']==os.getenv('ADMIN_USERNAME'):
                admin = item
            item['key'] = key
            key = key + 1
            if last_marks==item['marks']:
                item['position'] = last_position
                if item['position'] in toppers:
                    item['topper'] = item['position']
                else:
                    item['topper'] = 0
            else:
                last_position = last_position + 1
                item['position'] = last_position
                if item['position'] in toppers:
                    item['topper'] = item['position']
                else:
                    item['topper'] = 0

            last_marks = item['marks']
        result.remove(admin)
        return Response({"message":result}, status=status.HTTP_200_OK)
        