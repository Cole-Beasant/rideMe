from django.db import models
from passlib.hash import pbkdf2_sha256

class User(models.Model):
    username = models.CharField(max_length=50)
    password = models.CharField(max_length=256)
    firstName = models.CharField(max_length=50)
    lastName = models.CharField(max_length=50)
    email = models.EmailField()
    numTripsAsDriver = models.IntegerField()
    numTripsAsPassenger = models.IntegerField()
    averageRating = models.FloatField()
    registrationTime = models.DateTimeField()

    # phoneNumber

    def __str__(self):
        return self.username

    def verifyPassword(self, raw_password):
        return pbkdf2_sha256.verify(raw_password, self.password)

    def setAverageRating(self):
        sumOfRatings = 0
        numRatings = 0
        for review in Review.objects.all():
            if self == review.reviewedUserID:
                sumOfRatings += review.rating
                numRatings += 1
        if numRatings == 0:
            print('This user has not yet been rated.')
        else:
            self.averageRating = sumOfRatings / numRatings

    def completedRideAsDriver(self):
        self.numTripsAsDriver += 1

    def completedRideAsPassenger(self):
        self.numTripsAsPassenger += 1

    def getReviews(self):
        reviews = []
        for review in Review.objects.all():
            if self == review.reviewedUserID:
                reviews.append((review.rating, review.description))
        return reviews

    def getOwnedPostings(self):
        ownedPostings = []
        for posting in Posting.objects.all():
            if self == posting.ownerID:
                ownedPostings.append(posting)
        return ownedPostings

    def getApprovedPassengerRides(self):
        approvedPassengerRides = []
        for approvedPassenger in ApprovedPassengers.objects.all():
            if self == approvedPassenger.userID:
                approvedPassengerRides.append(approvedPassenger.postingID)
        return approvedPassengerRides 

    def getPostingsInteractedWith(self):
        postings = [] 
        for user in UsersInteractedForPostings.objects.all():
            if self == user.userID:
                postings.append(user.postingID)
        return postings

    def getUsersToReview(self):
        usersToReview = []
        for user in UsersInteractedForUsers.objects.all():
            if self == user.theUser:
                if user.hasReviewed == False:
                    usersToReview.append(user.theInteracter)
        return usersToReview

    '''
    def getConversations(self):
        conversations = []
        for conversation in Conversation.objects.all():
            if self =    
    '''


class Review(models.Model):
    reviewedUserID = models.ForeignKey(User, on_delete=models.CASCADE)
    reviewerID = models.ForeignKey(User, on_delete=models.CASCADE, related_name='leaves')
    rating = models.FloatField(max_length=2)
    description = models.CharField(max_length=500)

    def __str__(self):
        return (self.rating, self.description)

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
    tripDateAndTime = models.DateTimeField()
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
