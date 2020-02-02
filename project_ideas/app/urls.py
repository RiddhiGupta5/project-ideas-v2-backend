from django.urls import path, include
from .views import (
    PostIdeaView,
    SocialLoginView,
    SocialLogoutView,
    PublishedIdeasView,
    ViewIdea,
    VoteView,
    CommentView,
)
from rest_framework import routers

router = routers.DefaultRouter()


urlpatterns = [
    path("post_ideas/", PostIdeaView.as_view()),
    path("published_ideas/", PublishedIdeasView.as_view()), 
    path("view_idea/<int:pk>/", ViewIdea.as_view()),
    path("login/", SocialLoginView.as_view()),
    path("logout/", SocialLogoutView.as_view()),
    path("vote/", VoteView.as_view()),
    path("comment/", CommentView.as_view()),
    path("comment/<int:pk>/", CommentView.as_view()),
]
