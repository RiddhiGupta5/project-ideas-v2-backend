from django.urls import path, include
from app.views import (
    PostIdeaView,
    SocialLoginView,
    LogoutView,
    PublishedIdeasView,
    ViewIdea,
    VoteView,
    CommentView,
    SearchIdeaByContent,
    UserSignupView,
    NormalLoginView,
)
from rest_framework import routers

router = routers.DefaultRouter()


urlpatterns = [
    path("post_ideas/", PostIdeaView.as_view()),
    path("published_ideas/", PublishedIdeasView.as_view()), 
    path("view_idea/<int:pk>/", ViewIdea.as_view()),
    path("login/", SocialLoginView.as_view()),
    path("logout/", LogoutView.as_view()),
    path("vote/", VoteView.as_view()),
    path("comment/", CommentView.as_view()),
    path("comment/<int:pk>/", CommentView.as_view()),
    path("search_published_ideas/", SearchIdeaByContent.as_view()),
    path("normal_login/", NormalLoginView.as_view()),
    path("signup/", UserSignupView.as_view())
]
