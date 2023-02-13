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
    path('', views.LandingPageView.as_view()),
    path('login/', views.LoginView.as_view()),
    path('loginsuccess/', views.login),
    path('signup/', views.SignupView.as_view()),
    path('postings/', views.viewPostings.as_view(), name='postings'),
    path('postings/<int:pk>/postingdetails/', views.viewPostingDetails.as_view())
]
