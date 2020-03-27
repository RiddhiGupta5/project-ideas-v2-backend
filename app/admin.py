from django.contrib import admin
from .models import Idea, Comment, User, Vote, UserToken

admin.site.register(User)
admin.site.register(Idea)
admin.site.register(Comment)
admin.site.register(Vote)
admin.site.register(UserToken)