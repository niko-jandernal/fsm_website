from django.conf import settings
from django.conf.urls.static import static
from django.urls import path

from . import views
from .views import discussions, view_polls
from .views import like_post, post_comment, search_users, discussion_like_post, discussion_post_comment, explore, news
from .views import topic_list, topic_detail, topic_follow, following_posts

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

        path('discussions/topic/<int:topic_id>/follow/', views.topic_follow, name='topic_follow'),
        path('discussions/', discussions, name='discussions'),
        path('discussions/like/<int:post_id>/', discussion_like_post, name='discussion_like_post'),
        path('discussions/comment/<int:post_id>/', discussion_post_comment, name='discussion_post_comment'),
        path('discussions/<int:post_id>/', views.discussion_detail, name='discussion_detail'),

        path('topics/', topic_list, name='topic_list'),
        path('topics/<int:topic_id>/', topic_detail, name='topic_detail'),
        path('topics/<int:topic_id>/follow/', topic_follow, name='topic_follow'),

        path('discussions/following/', following_posts, name='following_posts'),
        path('topics/<int:topic_id>/delete/', views.topic_delete, name='topic_delete'),
        path('create_poll/', views.create_poll, name='create_poll'),
        path('view_polls/', view_polls, name='view_polls'),

        path('vote/<int:poll_id>/', views.vote, name='vote'),
        path('add_comment/<int:poll_id>/', views.add_comment, name='add_comment'),
        path('polls/<int:poll_id>/', views.poll_detail,   name='poll_detail'),
        path('polls/<int:poll_id>/vote_ajax/',   views.vote_ajax,    name='vote_ajax'),
        path('polls/<int:poll_id>/comment_ajax/',views.comment_ajax, name='comment_ajax'),

        path('albums/', views.album_list, name='album_list'),
        path('albums/create/', views.album_create, name='album_create'),
        path('albums/<int:album_id>/', views.album_detail, name='album_detail'),
        path('albums/<int:album_id>/add/<int:post_id>/', views.album_add_photo, name='add_photo'),
        path('albums/<int:album_id>/remove/<int:post_id>/', views.album_remove_post, name='remove_photo'),
        path('albums/<int:album_id>/delete/', views.album_delete, name='album_delete'),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
