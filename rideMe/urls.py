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
from django.urls import path
from rideMeApp import views

# app_name = 'rideMeApp'
urlpatterns = [
    path('admin/', admin.site.urls),
    # path('rideMeApp/', include('rideMeApp.urls')),
    # path('', include('django.contrib.auth.urls')),
    path('', views.login, name='landingPage'),
    path('signup/', views.createUser, name='signup'),
    path('verifyusername/', views.verifyUsername, name='verifyusername'),
    path('securityQuestion/', views.securityQuestion, name='securityQuestion'),
    path('resetPassword/', views.resetPassword, name='resetPassword'),
    path('logout/', views.logout, name='logout'),
    path('postings?submitted=True/', views.viewPostings, name='postings'),
    path('<int:pk>/postingdetails?submitted=True/', views.viewPostingDetails, name='postingdetails'),
    path('<int:pk>/userdetails?submitted=True/', views.viewUserDetails.as_view(), name='userdetails'),
    path('postings/addPostings?submitted=True/', views.addPosting, name='addPosting'),
    path('usersToReview?submitted=True/', views.usersToReview, name='usersToReview'),
    path('<int:pk>/addReview?submitted=True/', views.addReview, name='addReview'),
    path('<int:pk>/dismissReview?submitted=True/', views.dismissReview, name='dismissReview'),
    path('viewConversations?submitted=True/', views.viewConversations, name='viewConversations'),
    path('<int:pk>/viewMessages?submitted=True/', views.viewMessages, name='viewMessages'),
    path('<int:pk>/addApprovedPassenger?submitted=True/', views.addApprovedPassenger, name='addApprovedPassenger'),
    path('myProfile?submitted=True/', views.viewMyProfile, name='myProfile'),
    path('confirmDeleteProfile?submitted=True', views.confirmDeleteProfile, name='confirmDeleteProfile'),
    path('deleteProfile?submitted=True/', views.deleteProfile, name='deleteProfile'),
    path('myDriverPostings?submitted=True/', views.myDriverPostings, name='myDriverPostings'),
    path('<int:pk>/managePosting?submitted=True', views.managePosting, name='managePosting'),
    path('<int:pk>/completePosting?submitted=True/', views.completePosting, name='completePosting'),
    path('<int:pk>/confirmCancelPosting?submitted=True/', views.confirmCancelPosting, name='confirmCancelPosting'),
    path('<int:pk>/cancelPosting?submitted=True/', views.cancelPosting, name='cancelPosting'),
    path('myPassengerPostings?submitted=True/', views.myPassengerPostings, name='myPassengerPostings'),
    path('<int:pk>/removeMyselfAsApprovedPassenger?submitted=True/', views.removeMyselfAsApprovedPassenger, name='removeMyselfAsApprovedPassenger'),
    path('<int:pk>/confirmRemoveMyselfAsApprovedPassenger?submitted=True/', views.confirmRemoveMyselfAsApprovedPassenger, name='confirmRemoveMyselfAsApprovedPassenger'),
    path('<int:pk>/getUnreadMessages?submitted=True/', views.getUnreadMessages, name='getUnreadMessages'),
]
