from django.urls import path, include
from .views import (
    PostIdeaView,
    SocialLoginView,
    SocialLogoutView,
    PublishedIdeasView,
    ViewIdea,
)
from rest_framework import routers

router = routers.DefaultRouter()


urlpatterns = [
    path("post_ideas/", PostIdeaView.as_view()),
    path("published_ideas/", PublishedIdeasView.as_view()), 
    path("view_idea/<int:pk>/", ViewIdea.as_view()),
    path("login/", SocialLoginView.as_view()),
    path("logout/", SocialLogoutView.as_view()),
]
