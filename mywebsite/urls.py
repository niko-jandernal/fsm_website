from django.urls import path
from . import views

urlpatterns = [
    path('', views.home), # This is the default page (home page of the website)
    path('home', views.home, name='home'),
    path('explore', views.explore, name='explore'),

]