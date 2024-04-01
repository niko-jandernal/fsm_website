from django.urls import path
from . import views

urlpatterns = [
    path('', views.home), # This is the default page (home page of the website)
    path('home', views.home, name='home'),
    path('explore', views.explore, name='explore'),
    path('notifications', views.notifications, name='notifications'),
    path('boards', views.boards, name='boards'),
    path('polls', views.polls, name='polls'),
    path('discussions', views.discussions, name='discussions'),
    path('news', views.news, name='news'),
    path('create', views.create, name='create'),
    path('signin', views.signin, name='signin'),


]