from django.shortcuts import render
from rideMeApp.models import User, Posting, Review, Conversation, Message
from rideMeApp.models import ApprovedPassengers, UsersInteractedForUsers, UsersInteractedForPostings
from passlib.hash import pbkdf2_sha256
from django.utils import timezone

def create_user(request):
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
