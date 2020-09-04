from django.urls import path, include
from adminApp.views import (
    AdminLoginView,
    AdminSignupView,
    AdminLogoutView,
    UnpublishedIdeas,
    RejectedIdeasView,
    AllIdeasView,
    SearchAllIdeaByContent,
    QuestionView,
    AllQuestionsView,
    FilterQuestionDateView,
    AnswerView,
    AllAnswersView,
    FilterAnswerDateView,
    MarksView,
    ExcelSheetView,
    LeaderBoardView,
    UnevaluatedAnswersView,
    LatestQuestionView,
    SocialMediaDetailsView,
    DeletedIdeasView,
    CompletedIdeasView
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
    path("question/", QuestionView.as_view()),
    path("question/<int:pk>/", QuestionView.as_view()),
    path("all_questions/", AllQuestionsView.as_view()),
    path("filter_question_date/", FilterQuestionDateView.as_view()),
    path("answer/", AnswerView.as_view()),
    path("answer/<int:pk>/", AnswerView.as_view()),
    path("all_answers/", AllAnswersView.as_view()),
    path("filter_answer_date/", FilterAnswerDateView.as_view()),
    path("give_marks/", MarksView.as_view()),
    path("excel_sheet_upload/", ExcelSheetView.as_view()),
    path("leaderboard_view/", LeaderBoardView.as_view()),
    path("unevaluated_answers/", UnevaluatedAnswersView.as_view()),
    path("latest_question/", LatestQuestionView.as_view()),
    path("social_details/", SocialMediaDetailsView.as_view()),
    path("deleted_ideas/", DeletedIdeasView.as_view()),
    path("completed_ideas/", CompletedIdeasView.as_view()),
]
