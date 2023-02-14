from django.shortcuts import render, get_object_or_404, HttpResponse
from django.http import HttpResponseRedirect
from rideMeApp.models import User, Posting, Review, Conversation, Message
from rideMeApp.models import ApprovedPassengers, UsersInteractedForUsers, UsersInteractedForPostings
from passlib.hash import pbkdf2_sha256
from django.utils import timezone
from django.views import generic
from .forms import LoginForm
from django.contrib.auth.forms import UserCreationForm
from django.urls import reverse_lazy, reverse
from .forms import SignUpForm, LoginForm
from django.contrib import messages


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
                messages.error(request, 'This username does not exist')
                return render(request, 'rideMeApp/landingPage.html', {'form': LoginForm})
            user = User.objects.get(username=username)
            if user.verifyPassword(password) == True:
                submitted = True
                messages.success(request, 'Successfully signed in!')
                return HttpResponseRedirect(reverse('postings'))
            else:
                messages.error(request, 'Login credentials do not match')
                return render(request, 'rideMeApp/landingPage.html', {'form': LoginForm})

    return render(request, 'rideMeApp/landingPage.html', {'form': LoginForm})
        

def createUser(request):
    if request.method == "POST":
        form = SignUpForm(request.POST)
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
            except (ValueError):
                messages.error(request, 'No user added')
                return render(request, 'rideMeApp/signup.html', {'form': SignUpForm})

    return render(request, 'rideMeApp/signup.html', {'form': SignUpForm})

class viewPostings(generic.ListView):
    template_name = 'rideMeApp/postingsList.html'
    context_object_name = 'postingsList'

    def get_queryset(self):
        return Posting.objects.filter(isOpen=True)

class viewPostingDetails(generic.DetailView):
    model = Posting
    context_object_name = 'posting'
    template_name = 'rideMeApp/postingDetails.html'

class viewUserDetails(generic.DetailView):
    model = User
    context_object_name = 'user'
    template_name = 'rideMeApp/userDetails.html'
