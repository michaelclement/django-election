from django.urls import path

from . import views

app_name = 'polls'
urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('<int:pk>/', views.DetailView.as_view(), name='detail'),
    path('<str:token>/submit_vote/', views.submit_vote, name='submit_vote'),
    path('<int:pk>/details/', views.DetailView.as_view(), name='details'),
    path('home/', views.landing_page, name='home'),
    path('<str:token>/vote', views.vote, name='vote'),
    path('enter_token/', views.enter_token, name='enter_token'),
]