from django.urls import path

from . import views

app_name = 'polls'
urlpatterns = [
    path('', views.landing_page, name='index'),
    path('<str:token>/submit_vote/', views.submit_vote, name='submit_vote'),
    path('home/', views.landing_page, name='home'),
    path('<str:token>/vote', views.vote, name='vote'),
    path('enter_token/', views.enter_token, name='enter_token'),
    path('results/', views.results_view, name='results')
]