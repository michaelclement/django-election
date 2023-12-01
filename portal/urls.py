from django.urls import path

from . import views

app_name = "portal"
urlpatterns = [
    path("", views.index, name="index"),
    path("<int:submission_id>/", views.detail, name="detail"),
    path("<int:submitter_id>/results/", views.results, name="results"),
    path("vote/", views.vote, name="vote"),
    path("react/", views.vote, name="react"),
    path("history/", views.all_weekly_submissions, name="history"),
    path("leaderboard/", views.leaderboard, name="leaderboard"),
]

