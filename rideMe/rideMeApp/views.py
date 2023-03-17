from django.shortcuts import render
from django.http import HttpResponseRedirect
from rideMeApp.models import User, Posting, Review, Conversation, Message
from rideMeApp.models import ApprovedPassengers, UsersInteractedForUsers, UsersInteractedForPostings
from passlib.hash import pbkdf2_sha256
from django.utils import timezone
from django.views import generic
from django.views.decorators.cache import cache_control
from .forms import LoginForm, SignUpForm, ResetPasswordForm
from django.urls import reverse
from .forms import SignUpForm, LoginForm, AddPostingForm, StartConversation, AddReviewForm, SendMessageForm
from .forms import UpdatePickupLocation, UpdateDropoffLocation, UpdateTripDate, UpdateTripTime, UpdateVehicle
from .forms import UpdateNumAvailableSeats, UpdatePriceForm
from django.contrib import messages
import random, datetime


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
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
                    registrationTime = timezone.now()
                )
                messages.success(request, 'Successfully signed up!')
                return HttpResponseRedirect(reverse('landingPage'))
            except:
                messages.error(request, 'No user added')
                return render(request, 'rideMeApp/signup.html', {'form': form})
        else:
            messages.error(request, 'Ensure that the email address is valid')
            return render(request, 'rideMeApp/signup.html', {'form': form})

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
    postingsList = Posting.objects.filter(isOpen=True, tripDate__gt=timezone.now()).order_by('-tripDate') 
    user = User.objects.get(username=request.session['loggedInUser'])

    numPastDriverTripsNeedingAction = user.getNumPastDriverTripsNeedingAction()
    if numPastDriverTripsNeedingAction > 0:
        messages.info(request, 'You have ' + str(numPastDriverTripsNeedingAction) + ' past trips where you were a driver that need action')

    numUpcomingDriverTrips = user.getNumUpcomingDriverTrips()
    if numUpcomingDriverTrips > 0:
        messages.info(request, 'You have ' + str(numUpcomingDriverTrips) + ' upcoming trips where you are a driver')

    numUpcomingPassengerTrips = user.getNumUpcomingApprovedPassengerTrips()
    if numUpcomingPassengerTrips > 0:
        messages.info(request, 'You have ' + str(numUpcomingPassengerTrips) + ' upcoming trips where you are an approved passenger')

    numUnreadConversations = user.getNumUnreadConversations()
    if numUnreadConversations > 0:
        messages.info(request, 'You have ' + str(numUnreadConversations) + ' unread messages')

    numUsersToReview = user.getNumUsersToReview()
    if numUsersToReview > 0:
        messages.info(request, 'You have ' + str(numUsersToReview) + ' users to review')

    context = {'postingsList': postingsList, 'user': user}

    return render(request, 'rideMeApp/postingsList.html', context)


def viewPostingDetails(request, pk):
    user = User.objects.get(username=request.session['loggedInUser'])
    posting = Posting.objects.get(pk=pk)
    form = SendMessageForm()
    if (posting in user.getPostingsInteractedWith() and user!=posting.ownerID):
        conversation = Conversation.objects.get(postingID=posting, passengerID=user)
    else:
        conversation = Conversation.objects.filter(passengerID=user) # this solution isn't ideal but none of these should be accessible
        if len(conversation) == 0:
            conversation = Conversation.objects.get(pk=1)
    if request.method == 'POST':             
        try:
            newConversation = Conversation(
                postingID = posting, 
                passengerID = user,
                isClosed = False,
                latestMessageSentTime = timezone.now()
            )
        except:
            messages.error(request, 'Conversation was not created. Please try again.')
            return render(request, 'rideMeApp/postingDetails.html', context)

        try:
            message = request.POST['message']
            newMessage = Message(
                conversationID = newConversation,
                senderID = user,
                message = message,
                hasRead = False,
                timeSent = timezone.now()
            )
        except:
            messages.error(request, 'Message was not created. Please try again.')
            return render(request, 'rideMeApp/postingDetails.html', context)
        try:
            newObject = UsersInteractedForPostings(
                postingID = posting,
                userID = user
            )
        except:
            messages.error(request, 'Something went wrong. Please try again.')
            render(request, 'rideMeApp/postingDetails.html', context)
        try:
            newUserToReview = UsersInteractedForUsers(
                theUser = user,
                theInteracter = posting.ownerID,
                InteractionType = 'driver',
                hasReviewed = False,
                postingID = posting
            )
        except:
            messages.error(request, 'Something went wrong. Please try again.')
            render(request, 'rideMeApp/postingDetails.html', context)
        try:
            newUserToReview1 = UsersInteractedForUsers(
                theUser = posting.ownerID,
                theInteracter = user,
                InteractionType = 'passenger',
                hasReviewed = False,
                postingID = posting
            )
        except:
            messages.error(request, 'Something went wrong. Please try again.')
            return render(request, 'rideMeApp/postingDetails.html', context)
        try:
            newConversation.save()
            newMessage.save()
            newObject.save()
            newUserToReview.save()
            newUserToReview1.save()
        except:
            messages.error(request, 'New data items not successfully saved to the database. Please try again.')
            return render(request, 'rideMeApp/postingDetails.html', context)
        messages.success(request, 'Successfully messaged post owner!')
        return HttpResponseRedirect(reverse("viewMessages", args=[newConversation.pk]))
    context = {'posting': posting, 'user': user, 'form': form, 'conversation': conversation}
    return render(request, 'rideMeApp/postingDetails.html', context)


class viewUserDetails(generic.DetailView):
    model = User
    context_object_name = 'user'
    template_name = 'rideMeApp/userDetails.html'


def addPosting(request):
    if request.method == 'POST':
        form = AddPostingForm(request.POST)
        
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
                    tripPrice = request.POST['tripPrice'],
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
        
        else:
            messages.error(request, 'Please correct your sumbission')
            return render(request, 'rideMeApp/addPosting.html', {'form': form})
         

    return render(request, 'rideMeApp/addPosting.html', {'form': AddPostingForm})


def usersToReview(request):
    username = request.session['loggedInUser']
    user = User.objects.get(username=username)

    usersToReview =[]
    for object in UsersInteractedForUsers.objects.filter(theUser = user, hasReviewed=False):
        if object.postingID.tripDate < datetime.date.today():
            usersToReview.append(object)
    context = {'usersToReview': usersToReview}
    return render(request, 'rideMeApp/usersToReview.html', context)


def addReview(request, pk):
    object = UsersInteractedForUsers.objects.get(pk=pk)
    userToReview = object.theInteracter
    reviewedUserType = object.InteractionType
    reviewer = User.objects.get(username=request.session['loggedInUser'])
    if request.method == 'POST':
        form = AddReviewForm(request.POST)
        if form.is_valid():
            Review.objects.create(
                reviewedUserID = userToReview,
                reviewerID = reviewer,
                reviewedUserType = reviewedUserType,
                rating = request.POST['rating'],
                description = request.POST['description']
            )

            object.delete()

            messages.success(request, 'Review posted successfully!')
            return HttpResponseRedirect(reverse('usersToReview'))

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
    return HttpResponseRedirect(reverse('usersToReview'))


def viewConversations(request):
    user = User.objects.get(username = request.session['loggedInUser'])
    conversations = user.getConversations()
    
    for conversation in conversations:
        conversation.setHasUnreadMessagesCurUser(user)

    context = {'conversations': conversations, 'user': user}
    return render(request, 'rideMeApp/viewConversations.html', context)


def viewMessages(request, pk):
    conversation = Conversation.objects.get(pk=pk)
    posting = conversation.postingID
    messages = Message.objects.filter(conversationID = conversation).order_by('-timeSent')
    user = User.objects.get(username=request.session['loggedInUser'])
    if request.method == 'POST':
        form = SendMessageForm(request.POST)
        if form.is_valid():
            Message.objects.create(
                conversationID = conversation,
                senderID = user,
                message = request.POST['message'],
                hasRead = False,
                timeSent = timezone.now()
            )
            conversation.setLatestMessageSentTime(timezone.now())
            conversation.save()
            return HttpResponseRedirect(reverse("viewMessages", args=[pk]))
    else:
        form = SendMessageForm()
    for message in messages:
        if message.senderID != User.objects.get(username=request.session['loggedInUser']):
            if message.hasRead == False:
                message.hasRead = True
                message.save()
    context = {'messages': messages, 'conversation': conversation, 'user': user, 'posting': posting, 'form': SendMessageForm}
    return render(request, 'rideMeApp/viewMessages.html', context)


def viewMyProfile(request):
    user = User.objects.get(username = request.session['loggedInUser'])
    context = {'user': user}
    return render(request, 'rideMeApp/myProfile.html', context)


def addApprovedPassenger(request, pk):
    conversation = Conversation.objects.get(pk=pk)
    posting = conversation.postingID

    if posting.isOpen == False:
        messages.error(request, 'All the seats for this trip have already been filled')
        return HttpResponseRedirect(reverse('viewConversations'))

    approvedPassenger = conversation.passengerID
    for user in posting.getApprovedPassengers():
        if user == approvedPassenger:
            messages.error(request, approvedPassenger.username + ' is already an approved passenger for this trip.')
            return HttpResponseRedirect(reverse('viewConversations'))
    try:
        toDelete = UsersInteractedForPostings.objects.get(postingID=posting,userID=approvedPassenger)
        toDelete.delete()
    except:
        pass

    isIDUnique = False
    while isIDUnique == False:
        isIDUnique = True
        objectID = random.randint(1, 1000000)
        for object in ApprovedPassengers.objects.all():
            if object.id == objectID:
                isIDUnique = False
                break
    ApprovedPassengers.objects.create(id=objectID, postingID=posting, userID=approvedPassenger)

    Message.objects.create(
        conversationID = conversation,
        senderID = posting.ownerID,
        message = 'This is an automated message stating that you have been added as an approved passenger for my trip',
        hasRead = False,
        timeSent = timezone.now()
    )
    conversation.setLatestMessageSentTime(timezone.now())
    conversation.save()
    posting.numAvailableSeats -= 1
    posting.save()

    if posting.numAvailableSeats == 0:
        posting.isOpen = False
        posting.save()
        posting.sendTripClosedNotification()

    messages.success(request, approvedPassenger.username + ' is now an approved passenger for this trip')
    return HttpResponseRedirect(reverse('viewConversations'))


def confirmDeleteProfile(request):
    return render(request, 'rideMeApp/confirmDeleteProfile.html')


def deleteProfile(request):
    user = User.objects.get(username=request.session['loggedInUser'])
    try:
        user.delete()
        messages.success(request, 'Successfully deleted profile')
        return HttpResponseRedirect(reverse('landingPage'))
    except:
        messages.error(request, 'Profile was not deleted')
        return HttpResponseRedirect(reverse('myProfile'))


def myDriverPostings(request):
    user = User.objects.get(username=request.session['loggedInUser'])
    context = {'user': user}
    return render(request, 'rideMeApp/myDriverPostings.html', context)


def managePosting(request, pk):
    posting = Posting.objects.get(pk=pk)
    pickupLocationForm = UpdatePickupLocation()
    dropoffLocationForm = UpdateDropoffLocation()
    tripDateForm = UpdateTripDate()
    tripTimeForm = UpdateTripTime()
    numSeatsForm = UpdateNumAvailableSeats()
    tripPrice = UpdatePriceForm()
    vehicleForm = UpdateVehicle()
    
    user = User.objects.get(username=request.session['loggedInUser'])

    for conversation in user.getConversations():
        conversation.setHasUnreadMessagesCurUser(user)

    if request.method == 'POST':
        if 'pickupButton' in request.POST:
            pickupLocationForm = UpdatePickupLocation(request.POST)
            if pickupLocationForm.is_valid():
                posting.pickupLocation = request.POST['pickupLocation']
                posting.sendTripInfoUpdatedNotification()
                posting.save()
                messages.success(request, 'Successfully updated pickup location!')
                pickupLocationForm = UpdateDropoffLocation()
        if 'dropoffButton' in request.POST:
            dropoffLocationForm = UpdateDropoffLocation(request.POST)
            if dropoffLocationForm.is_valid():
                posting.dropoffLocation = request.POST['dropoffLocation']
                posting.sendTripInfoUpdatedNotification()
                posting.save()
                messages.success(request, 'Successfully updated dropoff location!')
                dropoffLocationForm = UpdateDropoffLocation()
        if 'tripDateButton' in request.POST:
            tripDateForm = UpdateTripDate(request.POST)
            if tripDateForm.is_valid():
                posting.tripDate = request.POST['tripDate']
                posting.sendTripInfoUpdatedNotification()
                posting.save()
                messages.success(request, 'Successfully updated trip date!')
                tripDateForm = UpdateTripDate()
        if 'tripTimeButton' in request.POST:
            tripTimeForm = UpdateTripTime(request.POST)
            if tripTimeForm.is_valid():
                posting.tripTime = request.POST['tripTime']
                posting.sendTripInfoUpdatedNotification()
                posting.save()
                messages.success(request, 'Successfully updated trip time!')
                tripTimeForm = UpdateTripTime()
        if 'numSeatsButton' in request.POST:
            numSeatsForm = UpdateNumAvailableSeats(request.POST)
            if numSeatsForm.is_valid():
                numAvailableSeats = int(request.POST['numAvailableSeats'])
                if posting.numAvailableSeats == 0 and numAvailableSeats > 0:
                    posting.sendTripReopenNotification()
                    posting.isOpen = True
                    posting.save()

                elif posting.numAvailableSeats > 0 and numAvailableSeats == 0:
                    posting.sendTripClosedNotification()
                    posting.isOpen = False
                    posting.save()

                posting.numAvailableSeats = numAvailableSeats
                posting.save()
                messages.success(request, 'Successfully update number of available seats!')
                numSeatsForm = UpdateNumAvailableSeats()
        if 'tripPrice' in request.POST:
            tripPrice = UpdatePriceForm(request.POST)
            if tripPrice.is_valid():
                posting.tripPrice = request.POST['tripPrice']
                posting.sendTripInfoUpdatedNotification()
                posting.save()
                messages.success(request, 'Successfully updated trip price!')
                tripPrice = UpdatePriceForm()
        if 'vehicleButton' in request.POST:
            vehicleForm = UpdateVehicle(request.POST)
            if vehicleForm.is_valid():
                posting.vehicle = request.POST['vehicle']
                posting.sendTripInfoUpdatedNotification()
                posting.save()
                messages.success(request, 'Successfully updated vehicle!')
                vehicleForm = UpdateVehicle()
    context = {'posting': posting, 
               'pickupLocationForm': pickupLocationForm,
               'dropoffLocationForm': dropoffLocationForm,
               'tripDateForm': tripDateForm,
               'tripTimeForm': tripTimeForm,
               'numSeatsForm': numSeatsForm,
               'tripPriceForm': tripPrice,
               'vehicleForm': vehicleForm
    }
    return render(request, 'rideMeApp/managePosting.html', context)


def completePosting(request, pk):
    posting = Posting.objects.get(pk=pk)
    postOwner = posting.ownerID
    postOwner.completedRideAsDriver()
    postOwner.save()
    posting.tripCompleted()
    posting.isComplete = True
    for passenger in posting.getApprovedPassengers():
        passenger.completedRideAsPassenger()
        passenger.save()
    posting.save()
    messages.success(request, 'Successfully marked posting as complete!')
    return HttpResponseRedirect(reverse('myDriverPostings'))


def confirmCancelPosting(request, pk):
    posting = Posting.objects.get(pk=pk)
    context = {'posting': posting}
    return render(request, 'rideMeApp/confirmCancelPosting.html', context)


def cancelPosting(request, pk):
    posting = Posting.objects.get(pk=pk)
    posting.sendTripCancelledNotification()
    posting.isCancelled = True
    posting.save()
    messages.success(request, 'Successfully cancelled posting')
    return HttpResponseRedirect(reverse('myDriverPostings'))


def myPassengerPostings(request):
    user = User.objects.get(username=request.session['loggedInUser'])
    context = {'user': user}
    return render(request, 'rideMeApp/myPassengerPostings.html', context)    


def removeMyselfAsApprovedPassenger(request, pk):
    user = User.objects.get(username=request.session['loggedInUser'])
    posting = Posting.objects.get(pk=pk)
    for passenger in posting.getApprovedPassengers():
        if user == passenger:
            object = ApprovedPassengers.objects.get(postingID=posting, userID=user)
            object.delete()
            if posting.numAvailableSeats == 0:
                posting.sendTripReopenNotification()
                posting.isOpen = True
            posting.numAvailableSeats += 1
            posting.save()
            conversation = Conversation.objects.get(postingID=posting, passengerID=user)
            conversation.latestMessageSentTime = timezone.now()
            conversation.save()
            Message.objects.create(
                conversationID = conversation,
                senderID = user,
                message = 'This is an automated message stating that I have removed myself from the approved passenger list. My apologies for any inconvenice.',
                hasRead = False,
                timeSent = timezone.now()
            )
            messages.success(request, 'Successfully removed from the approved passenger list for the posting')
            return HttpResponseRedirect(reverse('myPassengerPostings'))
    messages.error(request, 'Something went wrong')
    return HttpResponseRedirect(reverse('myPassengerPostings'))


def confirmRemoveMyselfAsApprovedPassenger(request, pk):
    posting = Posting.objects.get(pk=pk)
    context = {'posting': posting}
    return render(request, 'rideMeApp/removeMyselfAsApprovedPassenger.html', context)


def handler404(request, exception, template_name='404.html'):
    response = render(template_name)
    response.status_code = 404
    return response


def handler500(request, exception, template_name='500.html'):
    response = render(template_name)
    response.status_code = 500
    return response
