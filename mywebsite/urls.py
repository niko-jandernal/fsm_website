from django.conf import settings
from django.conf.urls.static import static
from django.urls import path

from . import views
from .views import discussions, view_polls
from .views import like_post, post_comment, search_users, discussion_like_post, discussion_post_comment, explore, news

urlpatterns = [
    path('', views.home),
    path('home', views.home, name='home'),
    path('explore/', explore, name='explore'),

    path('boards', views.boards, name='boards'),
    path('discussions', views.discussions, name='discussions'),
    path('fashion-news/', news, name='news'),
    path('create', views.create, name='create'),
    path('register', views.register, name='register'),
    path('login', views.loginPage, name='login'),
    path('logout', views.logoutUser, name='logout'),

    path('post/<int:post_id>/', views.post_detail, name='post_detail'),
    path('post/<int:post_id>/like/', like_post, name='like_post'),
    path('post/<int:post_id>/comment/', post_comment, name='post_comment'),
    path('search/', search_users, name='search_users'),

    path('discussions/', discussions, name='discussions'),
    path('discussions/like/<int:post_id>/', discussion_like_post , name='discussion_like_post'),
    path('discussions/comment/<int:post_id>/', discussion_post_comment, name='discussion_post_comment'),

    path('create_poll/', views.create_poll, name='create_poll'),
    path('view_polls/', view_polls, name='view_polls'),
    path('vote/<int:poll_id>/', views.vote, name='vote'),
    path('add_comment/<int:poll_id>/', views.add_comment, name='add_comment')

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
