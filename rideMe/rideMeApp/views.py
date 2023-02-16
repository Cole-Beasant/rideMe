from django.shortcuts import render, get_object_or_404, HttpResponse
from django.http import HttpResponseRedirect
from rideMeApp.models import User, Posting, Review, Conversation, Message
from rideMeApp.models import ApprovedPassengers, UsersInteractedForUsers, UsersInteractedForPostings
from passlib.hash import pbkdf2_sha256
from django.utils import timezone
from django.views import generic
from .forms import LoginForm, SignUpForm, ResetPasswordForm
from django.contrib.auth.forms import UserCreationForm
from django.urls import reverse_lazy, reverse
from .forms import SignUpForm, LoginForm, AddPostingForm, StartConversation, AddReviewForm
from django.contrib import messages


def logout(request):
    try:
        del request.session['loggedInUser']
    except KeyError:
        pass
    messages.success(request, 'Successfully logged out!')
    return HttpResponseRedirect(reverse('landingPage'))

def login(request):
    submitted = False
    if request.method == 'POST':
        form = LoginForm(request.POST)
        
        username = request.POST['username']
        password = request.POST['password']

        if form.is_valid():
            try:
                User.objects.get(username=username)
            except:
                messages.error(request, 'Enter a valid username')
                return render(request, 'rideMeApp/landingPage.html', {'form': LoginForm})
            user = User.objects.get(username=username)
            if user.verifyPassword(password) == True:
                submitted = True
                request.session['loggedInUser'] = user.username
                messages.success(request, 'Successfully signed in!')
                # return render(request, 'rideMeApp/postingsList.html')
                return HttpResponseRedirect(reverse('postings'))
            else:
                messages.error(request, 'Login credentials do not match')
                return render(request, 'rideMeApp/landingPage.html', {'form': LoginForm})

    return render(request, 'rideMeApp/landingPage.html', {'form': LoginForm})
        

def createUser(request):
    if request.method == "POST":
        form = SignUpForm(request.POST)
        if request.POST['password'] != request.POST['confirmPassword']:
            messages.error(request, 'Passwords do not match')
            return render(request, 'rideMeApp/signup.html', {'form': SignUpForm})

        for user in User.objects.all():
            if request.POST['username'] == user.username:
                messages.error(request, 'There is already a RideMe user with this username. Please enter a different username')
                return render(request, 'rideMeApp/signup.html', {'form': SignUpForm})

        username = request.POST['username']
        password = request.POST['password']
        firstName = request.POST['firstName']
        lastName = request.POST['lastName']
        email = request.POST['email']
        encryptPassword = pbkdf2_sha256.encrypt(password, rounds=12000, salt_size=32)

        if form.is_valid():
            try:
                User.objects.create(
                    username = username,
                    password = encryptPassword,
                    firstName = firstName,
                    lastName = lastName,
                    email = email,
                    numTripsAsDriver = 0,
                    numTripsAsPassenger = 0,
                    averageRating = 0.0,
                    registrationTime = timezone.now()
                )
                messages.success(request, 'Successfully signed up!')
                return HttpResponseRedirect(reverse('landingPage'))
            except:
                messages.error(request, 'No user added')
                return render(request, 'rideMeApp/signup.html', {'form': SignUpForm})
        else:
            messages.error(request, 'Ensure that the email address is valid')
            return render(request, 'rideMeApp/signup.html', {'form': SignUpForm})

    return render(request, 'rideMeApp/signup.html', {'form': SignUpForm})

def resetPassword(request):
    if request.method == 'POST':
        username = request.POST['username']
        newPassword = request.POST['newPassword']
        confirmNewPassword = request.POST['confirmNewPassword']

        if newPassword != confirmNewPassword:
            messages.error(request, 'Passwords do not match')
            return render(request, 'rideMeApp/resetPassword.html', {'form': ResetPasswordForm})

        try:
            User.objects.get(username=username)
        except:
                messages.error(request, 'Enter a valid username')
                return render(request, 'rideMeApp/resetPassword.html', {'form': ResetPasswordForm})
        user = User.objects.get(username=username)
        user.password = pbkdf2_sha256.encrypt(newPassword, rounds=12000, salt_size=32)
        user.save()
        messages.success(request, 'Password has been successfully reset')
        return HttpResponseRedirect(reverse('landingPage'))

        
    return render(request, 'rideMeApp/resetPassword.html', {'form': ResetPasswordForm})


def viewPostings(request):
    postingsList = Posting.objects.filter(isOpen=True).order_by('-tripDate') # add to the filter tripDate__gt=timezone.now()
    user = User.objects.get(username=request.session['loggedInUser'])

    numUnreadConversations = user.getNumUnreadConversations()
    if numUnreadConversations > 0:
        messages.info(request, 'You have ' + str(numUnreadConversations) + ' unread messages')

    numUsersToReview = user.getNumUsersToReview()
    if numUsersToReview > 0:
        messages.info(request, 'You have ' + str(numUsersToReview) + ' users to review')

    context = {'postingsList': postingsList, 'user': user}

    return render(request, 'rideMeApp/postingsList.html', context)

def viewPostingDetails(request, pk):
    posting = Posting.objects.get(pk=pk)
    context = {'posting': posting}
    return render(request, 'rideMeApp/postingDetails.html', context)

def messagePostOwner(request, pk):
    posting = Posting.objects.get(pk=pk)
    user = User.objects.get(username = request.session['loggedInUser'])

    if user == posting.ownerID:
        messages.error(request, 'You cannot message yourself')
        return HttpResponseRedirect(reverse('postings'))

    for conversation in posting.getAssociatedConversations():
        if user == conversation.passengerID:
            messages.error(request, 'You have already messaged this post owner regarding this posting. Go to your conversations page to view the conversation.')
            return HttpResponseRedirect(reverse('postings'))

    if request.method == 'POST':             

        newConversation = Conversation(postingID = posting, passengerID = user, isClosed = False)
        newConversation.save()
        message = request.POST['message']
        Message.objects.create(
            conversationID = newConversation,
            senderID = user,
            message = message
        )
        UsersInteractedForPostings.objects.create(
            postingID = posting,
            userID = user
        )
        UsersInteractedForUsers.objects.create(
            theUser = user,
            theInteracter = posting.ownerID,
            hasReviewed = False
        )
        UsersInteractedForUsers.objects.create(
            theUser = posting.ownerID,
            theInteracter = user,
            hasReviewed = False
        )
        messages.success(request, 'Successfully messaged post owner!')
        return HttpResponseRedirect(reverse('postings'))

    return render(request, 'rideMeApp/messagePostOwner.html', {'form': StartConversation})

'''
class viewPostingDetailsView(generic.DetailView):
    model = Posting
    context_object_name = 'posting'
    template_name = 'rideMeApp/postingDetails.html'
'''

class viewUserDetails(generic.DetailView):
    model = User
    context_object_name = 'user'
    template_name = 'rideMeApp/userDetails.html'

def addPosting(request):
    if request.method == 'POST':
        form = AddPostingForm(request.POST)
        if int != type(request.POST['numAvailableSeats']):
            messages.error(request, 'The number of available seats must be an integer.')
            return render(request, 'rideMeApp/addPosting.html', {'form': AddPostingForm})

        if request.POST['numAvailableSeats'] < 1:
            messages.error(request, 'You must have available seats in order to list the posting')
            return render(request, 'rideMeApp/addPosting.html', {'form': AddPostingForm})

        if timezone.now() > request.POST['tripDate']:
            messages.error(request, 'The trip must occur in the future.')
            return render(request, 'rideMeApp/addPosting.html', {'form': AddPostingForm}) 

        if form.is_valid():
            try:
                ownerUsername = request.session['loggedInUser']
                owner = User.objects.get(username=ownerUsername)
                Posting.objects.create(
                    ownerID=owner,
                    numAvailableSeats = request.POST['numAvailableSeats'],
                    tripDate = request.POST['tripDate'],
                    tripTime = request.POST['tripTime'],
                    submissionTime = timezone.now(),
                    pickupLocation = request.POST['pickupLocation'],
                    dropoffLocation = request.POST['dropoffLocation'],
                    vehicle = request.POST['vehicle'],
                    isOpen = True,
                    isCancelled = False,
                    isComplete = False
                )
                messages.success(request, 'Successfully added posting!')
                return HttpResponseRedirect(reverse('postings'))
            except:
                messages.error(request, 'No posting added')
                return render(request, 'rideMeApp/addPosting.html', {'form': AddPostingForm})
        

    return render(request, 'rideMeApp/addPosting.html', {'form': AddPostingForm})


def usersToReview(request):
    username = request.session['loggedInUser']
    user = User.objects.get(username=username)
    usersToReview = UsersInteractedForUsers.objects.filter(
        theUser = user,
        hasReviewed=False
    )
    context = {'usersToReview': usersToReview}
    return render(request, 'rideMeApp/usersToReview.html', context)

def addReview(request, pk):
    userToReview = User.objects.get(pk=pk)
    reviewer = User.objects.get(username=request.session['loggedInUser'])
    if request.method == 'POST':
        form = AddReviewForm(request.POST)
        if form.is_valid():
            Review.objects.create(
                reviewedUserID = userToReview,
                reviewerID = reviewer,
                rating = request.POST['rating'],
                description = request.POST['description']
            )

            for usersInteractedObject in UsersInteractedForUsers.objects.all():
                if usersInteractedObject.theUser == reviewer:
                    if usersInteractedObject.theInteracter == userToReview:
                        usersInteractedObject.hasReviewed = True
                        usersInteractedObject.delete()
                        break

            messages.success(request, 'Review posted successfully!')
            return HttpResponseRedirect(reverse('postings'))

        else:
            messages.error('Your rating may not be between 0 and 5 or your description may be too long.')
            return render(request, 'rideMeApp/addReview.html', {'form': AddReviewForm})
    
    messages.info(request, 'Leave a review for ' + userToReview.lastName + ', ' + userToReview.firstName)
    return render(request, 'rideMeApp/addReview.html', {'form': AddReviewForm})

def dismissReview(request, pk):
    userToReview = User.objects.get(pk=pk)
    reviewer = User.objects.get(username=request.session['loggedInUser'])
    for usersInteractedObject in UsersInteractedForUsers.objects.all():
        if usersInteractedObject.theUser == reviewer:
            if usersInteractedObject.theInteracter == userToReview:
                usersInteractedObject.hasReviewed = True
                usersInteractedObject.delete()
                break

    messages.success(request, 'Successfully dismissed')
    return HttpResponseRedirect(reverse('postings'))