from django.urls import path
from . views import *

urlpatterns = [
    path('register/',UserRegisterView.as_view(),name='user-register'),
    path('login/',UserLoginView.as_view(),name='user-login'),
    path('',UserHomePageView.as_view(),name='user-homepage'),
    path('add-blog/',BlogCreateView.as_view(),name='blog-create'),
    path('edit-blog/<slug:slug>/',BlogUpdateView.as_view(),name='blog-update'),
    path('delete/<int:id>/',BlogDeleteView.as_view(),name='blog-delete'),
    path('blogs/',BlogListView.as_view(),name='blog-list'),
    path('user-blogs/',AuthenticatedUserBlogListView.as_view(),name='userblog-list'),
    path('blogs/<slug:slug>/',BlogDetailView.as_view(),name='blog-detail'),
    path('profile/',UserProfileView.as_view(),name='user-profile'),
    path('edit-profile/',UserProfileUpdateView.as_view(),name='edit-profile'),
    path('logout/',UserLogoutView.as_view(),name='user-logout')
]
