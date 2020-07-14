from django.contrib import admin
from .models import Idea, Comment, User, Vote, UserToken, SocialMediaDetails, UserFCMDevice

admin.site.register(User)
admin.site.register(Idea)
admin.site.register(Comment)
admin.site.register(Vote)
admin.site.register(UserToken)
admin.site.register(SocialMediaDetails)
admin.site.register(UserFCMDevice)