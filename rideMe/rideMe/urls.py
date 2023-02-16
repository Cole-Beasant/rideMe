"""rideMe URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from rideMeApp import views

# app_name = 'rideMeApp'
urlpatterns = [
    path('admin/', admin.site.urls),
    # path('rideMeApp/', include('rideMeApp.urls')),
    # path('', include('django.contrib.auth.urls')),
    path('', views.login, name='landingPage'),
    path('signup/', views.createUser, name='signup'),
    path('resetPassword/', views.resetPassword, name='resetPassword'),
    path('logout/', views.logout, name='logout'),
    # path('getLoggedInUser/', views.getLoggedInUser, name='getLoggedInUser'),
    path('postings?submitted=True/', views.viewPostings, name='postings'),
    path('<int:pk>/postingdetails?submitted=True/', views.viewPostingDetails, name='postingdetails'),
    path('<int:pk>/postingdetails/messagePostOwner?submitted=True/', views.messagePostOwner, name='messagePostOwner'),
    path('<int:pk>/userdetails?submitted=True/', views.viewUserDetails.as_view(), name='userdetails'),
    path('postings/addPostings?submitted=True/', views.addPosting, name='addPosting'),
    path('usersToReview', views.usersToReview, name='usersToReview'),
    path('<int:pk>/addReview', views.addReview, name='addReview'),
    path('<int:pk>/dismissReview', views.dismissReview, name='dismissReview')
]
