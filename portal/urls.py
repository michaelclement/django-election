from django.urls import path

from . import views

app_name = "portal"
urlpatterns = [
    # ex: /portal/
    path("", views.index, name="index"),
    # ex: /portal/2
    path("<int:submission_id>/", views.detail, name="detail"),
    # ex: /portal/2/results
    path("<int:submitter_id>/results/", views.results, name="results"),
    # ex: /portal/vote
    path("vote/", views.vote, name="vote"),
    path("react/", views.vote, name="react"),
    #
    path("history/", views.all_weekly_submissions, name="history"),
]

