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


def LandingPage(request):
    return HttpResponse('Welcome to RideMe')


'''
class SignUpView(generic.CreateView):
    form_class = UserCreationForm
    success_url = reverse_lazy('login')
    template_name = 'registration/signup.html'
'''

def login(request):
    # render(request, 'rideMeApp/landingPage.html')
    username = request.POST.get('username')
    password = request.POST.get('password')
    # user = get_object_or_404(User, username=username)

    try:
        user = User.objects.get(username = username)
        try:
            password == user.password
            return HttpResponseRedirect(reverse('postings'))
        except User.DoesNotExist:
            return HttpResponse('The username and password do not match')
    except User.DoesNotExist:
        return HttpResponse('There is no user with this username')
        


def createUser(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        firstName = request.POST['firstName']
        lastName = request.POST['lastName']
        email = request.POST['email']
        # phoneNumber = request.POST['phoneNumber']

        encryptPassword = pbkdf2_sha256.encrypt(password, rounds=12000, salt_size=32)

        User.objects.create(
            username = username,
            password = encryptPassword,
            firstName = firstName,
            lastName = lastName,
            email = email,
            # phoneNumber = phoneNumber,
            numTripsAsDriver = 0,
            numTripsAsPassenger = 0,
            averageRating = 0.0,
            registrationTime = timezone.now()
        )

class viewPostings(generic.ListView):
    template_name = 'rideMeApp/postingsList.html'
    context_object_name = 'postingsList'

    def get_queryset(self):
        return Posting.objects.filter(isOpen=True)

class viewPostingDetails(generic.DetailView):
    model = Posting
    context_object_name = 'posting'
    template_name = 'rideMeApp/postingDetails.html'