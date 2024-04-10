from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static
from .views import like_post, post_comment, search_users

urlpatterns = [
    path('', views.home),  # This is the default page (home page of the website)
    path('home', views.home, name='home'),
    path('explore', views.explore, name='explore'),
    path('notifications', views.notifications, name='notifications'),
    path('boards', views.boards, name='boards'),
    path('polls', views.polls, name='polls'),
    path('discussions', views.discussions, name='discussions'),
    path('news', views.news, name='news'),
    path('create', views.create, name='create'),
    path('register', views.register, name='register'),
    path('login', views.loginPage, name='login'),
    path('logout', views.logoutUser, name='logout'),

    path('post/<int:post_id>/', views.post_detail, name='post_detail'),
    path('post/<int:post_id>/like/', like_post, name='like_post'),
    path('post/<int:post_id>/comment/', post_comment, name='post_comment'),
    path('search/', search_users, name='search_users'),

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
