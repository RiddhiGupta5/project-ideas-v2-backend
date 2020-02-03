from django.db import models
from django.contrib.auth.models import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.utils.translation import gettext_lazy as _
from django.utils import timezone

from .managers import CustomUserManager


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(_('email address'), unique=True)
    is_staff = models.BooleanField(default=False)       # Field necessary for a django user
    is_active = models.BooleanField(default=True)       # Field necessary for a django user
    is_superuser = models.BooleanField(default=False)   # Field necessary for a django user
    date_joined = models.DateTimeField(default=timezone.now)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    def __str__(self):
        return self.email



class Idea(models.Model):

    keys = {"PENDING":0, "PUBLISHED":1, "REJECTED":2}
    project_title = models.CharField(max_length=60)
    project_description = models.TextField()
    tags = models.CharField(max_length=300)
    is_reviewed = models.IntegerField(default=keys["PENDING"])
    votes = models.IntegerField(default=0)
    reviewer_id = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True, related_name="admin_id_idea")
    date_time = models.DateTimeField(auto_now_add=True)

class Comment(models.Model):

    body = models.TextField()
    parent_comment_id = models.IntegerField(null=True)
    user_id = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_id_comment")
    idea_id = models.ForeignKey(Idea, on_delete=models.CASCADE, related_name="idea_id_comment")

class Vote(models.Model):

    vote_type_key = {"UPVOTE":1, "DOWNVOTE":-1}
    vote_type = models.IntegerField()
    user_id = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_id_vote")
    idea_id = models.ForeignKey(Idea, on_delete=models.CASCADE, related_name="idea_id_vote")
