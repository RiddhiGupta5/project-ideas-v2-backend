from django.db import models
from app.models import User

class Question(models.Model):
    question_body = models.CharField(max_length=150)
    date_time = models.DateTimeField(auto_now_add=True)

class Answer(models.Model):
    # 0 - Daily Challenges
    # 1 - Weekly challenges
    answer_type = models.IntegerField()
    daily_challenge = models.ForeignKey(Question, on_delete=models.CASCADE, default=None, null=True)
    weekly_challenge = models.IntegerField(default=None, null=True)
    answer_body = models.TextField()
    marks = models.IntegerField(default=0)
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    date_time = models.DateTimeField(auto_now_add=True)
    evaluated = models.BooleanField(default=False)