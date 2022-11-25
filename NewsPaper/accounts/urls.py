from django.urls import path
from django.contrib.auth.views import LoginView, LogoutView
from .views import *

urlpatterns = [
    path('login/',
         LoginView.as_view(template_name = 'account/login.html'),
         name='login'),
    path('logout/',
         LogoutView.as_view(template_name = 'account/logout.html'),
         name='logout'),
    path('signup/',
         BaseRegisterView.as_view(template_name = 'account/signup.html'),
         name='signup'),
    path('author/', make_me_author, name = 'make_me_author'),
    path('profile/',
         BaseRegisterView.as_view(template_name='account/index.html'),
         name='profile'),
]
