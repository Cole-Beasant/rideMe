from django.db import models

class User(models.Model):
    username = models.CharField(max_length=50)
    firstName = models.CharField(max_length=50)
    lastName = models.CharField(max_length=50)
    numTripsAsDriver = models.IntegerField()
    numTripsAsPassenger = models.IntegerField()

    # password
    # email
    # phoneNumber
    # averageRating
    # registrationTime = models.DateTimeField('registration date')

class Review(models.Model):
    reviewedUserID = models.ForeignKey(User, on_delete=models.CASCADE)
    reviewerID = models.ForeignKey(User, on_delete=models.CASCADE, related_name='leaves')
    rating = models.FloatField(max_length=2)
    description = models.CharField(max_length=500)

class UsersInteractedForUsers(models.Model):
    '''
    For reviewing purposes
    '''
    theUser = models.ForeignKey(User, on_delete=models.CASCADE, related_name='has')
    theInteracter = models.ForeignKey(User, on_delete=models.CASCADE, related_name='interacts_with')
    hasReviewed = models.BooleanField()

class Posting(models.Model):
    ownerID = models.ForeignKey(User, on_delete=models.CASCADE)
    numAvailableSeats = models.IntegerField()
    isOpen = models.BooleanField()
    isCancelled = models.BooleanField()
    isComplete = models.BooleanField()
    # tripDateAndTime = models.DateTimeField()
    pickupLocation = models.CharField(max_length=50)
    dropoffLocation = models.CharField(max_length=50)
    vehicle = models.CharField(max_length=50)

class ApprovedPassengers(models.Model):
    postingID = models.ForeignKey(Posting, on_delete=models.CASCADE)
    userID = models.ForeignKey(User, on_delete=models.CASCADE)

class UsersInteractedForPostings(models.Model):
    '''
    For notification purposes
    '''
    postingID = models.ForeignKey(Posting, on_delete=models.CASCADE)
    userID = models.ForeignKey(User, on_delete=models.CASCADE)

class Conversation(models.Model):
    postingID = models.ForeignKey(Posting, on_delete=models.CASCADE)
    # postOwnerID = models.ForeignKey(User, on_delete=models.CASCADE)
    passengerID = models.ForeignKey(User, on_delete=models.CASCADE)
    isClosed = models.BooleanField()

class Message(models.Model):
    conversationID = models.ForeignKey(Conversation, on_delete=models.CASCADE)
    senderID = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.CharField(max_length=500)
