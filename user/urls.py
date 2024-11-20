from django.urls import path
from . views import *

urlpatterns = [
    path('register/',UserRegisterView.as_view(),name='user-register'),
    path('login/',UserLoginView.as_view(),name='user-login'),
    path('',UserHomePageView.as_view(),name='user-homepage'),
    
]
