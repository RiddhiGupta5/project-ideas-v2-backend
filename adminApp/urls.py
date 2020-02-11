from django.urls import path, include
from adminApp.views import (
    AdminLoginView,
    AdminSignupView,
    AdminLogoutView,
    UnpublishedIdeas,
    RejectedIdeasView,
    AllIdeasView,
    SearchAllIdeaByContent,
)
from rest_framework import routers

router = routers.DefaultRouter()


urlpatterns = [
    path("login/", AdminLoginView.as_view()),
    path("signup/", AdminSignupView.as_view()),
    path("logout/", AdminLogoutView.as_view()),
    path("unpublished_ideas/", UnpublishedIdeas.as_view()),
    path("rejected_ideas/", RejectedIdeasView.as_view()),
    path("all_ideas/", AllIdeasView.as_view()),
    path("search_all_ideas/", SearchAllIdeaByContent.as_view()),
]