from django.db import models
from django.utils import timezone
from passlib.hash import pbkdf2_sha256
import datetime
from django.utils.text import slugify

def user_directory_path(instance, filename):
    # File will be uploaded to MEDIA_ROOT/user_<id>/<filename>
    return f'user_{instance.pk}/{filename}'

class User(models.Model):
    username = models.CharField(max_length=50)
    password = models.CharField(max_length=256)
    firstName = models.CharField(max_length=50)
    lastName = models.CharField(max_length=50)
    email = models.EmailField()
    numTripsAsDriver = models.IntegerField(default=0)
    numTripsAsPassenger = models.IntegerField(default=0)
    registrationTime = models.DateTimeField(auto_now_add=True)
    securityQuestion = models.CharField(max_length=50, default="What is the name of the site")
    securityQuestionAnswer = models.CharField(max_length=256, default='rideMe')
    profilePicture = models.ImageField(upload_to=user_directory_path, blank=True, null=True)

    # phoneNumber

    def __str__(self):
        return self.username

    def verifyPassword(self, raw_password):
        return pbkdf2_sha256.verify(raw_password, self.password)
    
    def verifySecurityQuestionAnswer(self, rawSecurityQuestionAnswer):
        return pbkdf2_sha256.verify(rawSecurityQuestionAnswer, self.securityQuestionAnswer)

    def getAverageRatingAsDriver(self):
        reviews = Review.objects.filter(reviewedUserID=self, reviewedUserType='driver')
        sumOfRatings = sum(r.rating for r in reviews)
        numRatings = reviews.count()
        """
        for review in Review.objects.all():
            if self == review.reviewedUserID:
                if review.reviewedUserType == 'driver':
                    sumOfRatings += review.rating
                    numRatings += 1
        """
        if numRatings == 0:
            return 0
        else:
            return sumOfRatings / numRatings

    def getAverageRatingAsPassenger(self):
        reviews = Review.objects.filter(reviewedUserID=self, reviewedUserType='passenger')
        sumOfRatings = sum(r.rating for r in reviews)
        numRatings = reviews.count()
        """
        sumOfRatings = 0
        numRatings = 0
        for review in Review.objects.all():
            if self == review.reviewedUserID:
                if review.reviewedUserType == 'passenger':
                    sumOfRatings += review.rating
                    numRatings += 1
        """
        if numRatings == 0:
            return 0
        else:
            return sumOfRatings / numRatings

    def completedRideAsDriver(self):
        self.numTripsAsDriver += 1

    def completedRideAsPassenger(self):
        self.numTripsAsPassenger += 1

    def getReviewsAsDriver(self):
        reviews = []
        for review in Review.objects.all().order_by('-submissionTime'):
            if self == review.reviewedUserID:
                if review.reviewedUserType == 'driver':
                    reviews.append((review.reviewerID, review.rating, review.description, review.submissionTime))
        return reviews

    def getReviewsAsPassenger(self):
        reviews = []
        for review in Review.objects.all().order_by('-submissionTime'):
            if self == review.reviewedUserID:
                if review.reviewedUserType == 'passenger':
                    reviews.append((review.reviewerID, review.rating, review.description, review.submissionTime))
        return reviews

    def getOwnedPostings(self):
        return Posting.objects.filter(ownerID=self).order_by('-tripDate')

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
                    if user.postingID.tripDate < datetime.date.today():
                        usersToReview.append(user.theInteracter)
        return usersToReview        


    def getNumUsersToReview(self):
        return len(self.getUsersToReview())

    def getConversations(self):
        conversations = []
        for conversation in Conversation.objects.filter(isClosed=False).order_by('-latestMessageSentTime'):
            if self == conversation.passengerID:
                conversations.append(conversation)
            elif self == conversation.postingID.ownerID:
                conversations.append(conversation)
        return conversations

    def getNumUnreadConversations(self):
        numUnreadConversations = 0
        for conversation in Conversation.objects.filter(isClosed=False).order_by('-latestMessageSentTime'):
            if self == conversation.passengerID:
                if conversation.hasUnreadMessages() == True:
                    for message in conversation.getMessages():
                        if message.hasRead == False:
                            if self != message.senderID:
                                numUnreadConversations += 1
            elif self == conversation.postingID.ownerID:
                if conversation.hasUnreadMessages() == True:
                    for message in conversation.getMessages():
                        if message.hasRead == False:
                            if self != message.senderID:
                                numUnreadConversations += 1
        return numUnreadConversations

    def getUpcomingDriverTrips(self):
        return Posting.objects.filter(ownerID=self, tripDate__gt=timezone.now(), isCancelled=False).order_by('-tripDate')

    def getNumUpcomingDriverTrips(self):
        return len(self.getUpcomingDriverTrips())

    def getPastDriverTripsNeedingAction(self):
        query = Posting.objects.filter(ownerID=self, tripDate__lt=timezone.now(), isComplete=False, isCancelled=False).order_by('-tripDate')
        pastDriverTrips = []
        for posting in query:
            if len(posting.getApprovedPassengers()) == 0:
                posting.isCancelled == True
                posting.save()
            elif posting.isComplete == False and posting.isCancelled == False:
                pastDriverTrips.append(posting)
        return pastDriverTrips

    def getNumPastDriverTripsNeedingAction(self):
        return len(self.getPastDriverTripsNeedingAction())

    def getPastDriverTrips(self):
        return Posting.objects.filter(ownerID=self, tripDate__lt=timezone.now(), isComplete=True).order_by('-tripDate')

    def getUpcomingApprovedPassengerTrips(self):
        upcomingApprovedPassengerTrips = []
        for object in ApprovedPassengers.objects.all():
            if object.userID == self and object.postingID.tripDate > datetime.date.today():
                upcomingApprovedPassengerTrips.append(object.postingID)
        return upcomingApprovedPassengerTrips

    def getNumUpcomingApprovedPassengerTrips(self):
        return len(self.getUpcomingApprovedPassengerTrips())

    def getAwaitingApprovalPassengerTrips(self):
        awaitingApprovalPassengerTrips = []
        for object in UsersInteractedForPostings.objects.all():
            if object.userID == self and object.postingID.tripDate > datetime.date.today():
                awaitingApprovalPassengerTrips.append(object.postingID)
        return awaitingApprovalPassengerTrips

    def getPastApprovedPassengerTrips(self):
        pastApprovedPassengerTrips = []
        for object in ApprovedPassengers.objects.all():
            if object.userID == self and object.postingID.tripDate < datetime.date.today():
                if object.postingID.isComplete == True:
                    pastApprovedPassengerTrips.append(object.postingID)
        return pastApprovedPassengerTrips
    
    def getUpcomingOpenDriverPosting(self):
        return Posting.objects.filter(ownerID=self, isOpen=True, tripDate__gt = timezone.now(), isCancelled = False).order_by('-tripDate')

class Review(models.Model):
    reviewedUserID = models.ForeignKey(User, on_delete=models.CASCADE)
    reviewedUserType = models.CharField(max_length=20, default='passenger')
    reviewerID = models.ForeignKey(User, on_delete=models.CASCADE, related_name='leaves')
    rating = models.FloatField(max_length=2)
    description = models.CharField(max_length=500)
    submissionTime = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.reviewerID.username + " " + self.rating.__str__() + " " + self.description

class Posting(models.Model):
    ownerID = models.ForeignKey(User, on_delete=models.CASCADE)
    numAvailableSeats = models.IntegerField()
    isOpen = models.BooleanField(default=True)
    isCancelled = models.BooleanField(default=False)
    isComplete = models.BooleanField(default=False)
    tripDate = models.DateField(default=datetime.date(2023,2,15))
    tripTime = models.TimeField(default=datetime.time(10,30,0))
    tripPrice = models.DecimalField(max_digits=6, decimal_places=2)
    pickupLocation = models.CharField(max_length=50)
    dropoffLocation = models.CharField(max_length=50)
    vehicle = models.CharField(max_length=50)
    submissionTime = models.DateTimeField(auto_now_add=True)

    def getApprovedPassengers(self):
        approvedPassengers = []
        for object in ApprovedPassengers.objects.filter(postingID=self):
            approvedPassengers.append(object.userID)
        return approvedPassengers

    def getUsersInteractedWith(self):
        usersInteractedWith = []
        for user in UsersInteractedForPostings.objects.all():
            if self == user.postingID:
                usersInteractedWith.append(user.userID)
        return usersInteractedWith

    def getAssociatedConversations(self):
        associatedConversations = []
        for conversation in Conversation.objects.filter(isClosed=False).order_by('-latestMessageSentTime'):
            if self == conversation.postingID:
                associatedConversations.append(conversation)
        return associatedConversations

    def sendTripClosedNotification(self):
        for conversation in self.getAssociatedConversations():
            Message.objects.create(
                conversationID=conversation,
                senderID = self.ownerID,
                message = 'This is an automated message stating that the posting is now closed. If you are not an approved passenger, you cannot be added to the approved passenger list unless an existing approved passenger cancels.',
                hasRead = False,
                timeSent = timezone.now()
            )
            conversation.setLatestMessageSentTime(timezone.now())
            conversation.save()

    def sendTripReopenNotification(self):
        for conversation in self.getAssociatedConversations():
            Message.objects.create(
                conversationID=conversation,
                senderID = self.ownerID,
                message = 'This is an automated message stating that the posting has reopened. If you are not an approved passenger, the post owner is now able to add you to the approved passenger list.',
                hasRead = False,
                timeSent = timezone.now()
            )
            conversation.setLatestMessageSentTime(timezone.now())
            conversation.save()

    def sendTripCancelledNotification(self):
        for conversation in self.getAssociatedConversations():
            Message.objects.create(
                conversationID=conversation,
                senderID = self.ownerID,
                message = 'This is an automated message stating that the trip has been cancelled. RideMe apologizes for any inconvenience.',
                hasRead = False,
                timeSent = timezone.now()
            )
            conversation.setLatestMessageSentTime(timezone.now())
            conversation.save()

    def sendTripInfoUpdatedNotification(self):
        for conversation in self.getAssociatedConversations():
            Message.objects.create(
                conversationID=conversation,
                senderID = self.ownerID,
                message = 'This is an automated message stating that the trip information has been updated. If you are an approved passenger for this trip, you should verify that the trip still fits your schedule and if not, you should remove yourself from the list.',
                hasRead = False,
                timeSent = timezone.now()
            )
            conversation.setLatestMessageSentTime(timezone.now())
            conversation.save()

    def tripCompleted(self):
        for conversation in self.getAssociatedConversations():
            conversation.isClosed = True
            conversation.save()

class UsersInteractedForUsers(models.Model):
    '''
    For reviewing purposes
    '''
    theUser = models.ForeignKey(User, on_delete=models.CASCADE, related_name='has')
    theInteracter = models.ForeignKey(User, on_delete=models.CASCADE, related_name='interacts_with')
    InteractionType = models.CharField(max_length=20, default='passenger')
    hasReviewed = models.BooleanField(default=False)
    postingID = models.ForeignKey(Posting, on_delete=models.CASCADE, null=True)

class ApprovedPassengers(models.Model):
    id = models.AutoField(primary_key=True)
    postingID = models.ForeignKey(Posting, on_delete=models.CASCADE)
    userID = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.postingID.ownerID.username + ', ' + self.userID.username

class UsersInteractedForPostings(models.Model):
    '''
    For notification purposes
    '''
    postingID = models.ForeignKey(Posting, on_delete=models.CASCADE)
    userID = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.postingID.ownerID.username + ', ' + self.userID.username

class Conversation(models.Model):
    postingID = models.ForeignKey(Posting, on_delete=models.CASCADE)
    passengerID = models.ForeignKey(User, on_delete=models.CASCADE)
    isClosed = models.BooleanField(default=False)
    latestMessageSentTime = models.DateTimeField(auto_now_add=True)
    hasUnreadMessagesCurUser = models.BooleanField(default=False)

    def getMessages(self):
        messages = []
        for message in Message.objects.all():
            if self == message.conversationID:
                messages.append(message)
        return messages

    def hasUnreadMessages(self):
        for message in Message.objects.all():
            if self == message.conversationID:
                if message.hasRead == False:
                    return True
        return False

    def setHasUnreadMessagesCurUser(self, user):
        for message in Message.objects.all():
            if self == message.conversationID:
                if message.hasRead == False:
                    if message.senderID != user:
                        self.hasUnreadMessagesCurUser = True
                        return
        self.hasUnreadMessagesCurUser = False

    def setLatestMessageSentTime(self, time):
        self.latestMessageSentTime = time

class Message(models.Model):
    conversationID = models.ForeignKey(Conversation, on_delete=models.CASCADE)
    senderID = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.CharField(max_length=500)
    hasRead = models.BooleanField(default=True)
    timeSent = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.senderID.username + ', ' + self.message
