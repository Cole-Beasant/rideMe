from django import forms

from .models import User

class SignUpForm(forms.Form):
    # class Meta:
        # model = User
        # fields = ('username', 'firstName', 'lastName', 'email', 'password')
    username = forms.CharField(label='Enter your username:')
    firstName = forms.CharField(label='Enter your First Name:')
    lastName = forms.CharField(label='Enter your Last Name:')
    email = forms.EmailField(label="Enter your email address:")
    password = forms.CharField(label='Enter your password:')
    confirmPassword = forms.CharField(label='Confirm you password:')

class LoginForm(forms.Form):
    username = forms.CharField(label='Enter your username')
    password = forms.CharField(label='Enter your password')

class ResetPasswordForm(forms.Form):
    username = forms.CharField(label='Enter your username:')
    newPassword = forms.CharField(label='Enter your new password:')
    confirmNewPassword = forms.CharField(label='Confirm your new password:')

class AddPostingForm(forms.Form):
    numAvailableSeats = forms.IntegerField(label='Enter the number of available seats for your trip:')
    tripDate = forms.DateField(label='Enter the date the trip will be occuring:', widget=forms.DateInput()),
    tripTime = forms.TimeField(label='Enter the time the trip will be occuring:', widget=forms.TimeInput(format='%H:%M'))
    pickupLocation = forms.CharField(label='Enter the general location of where you can pick up passengers:', max_length=50)
    dropoffLocation = forms.CharField(label='Enter the general location where you can drop off passenger:', max_length=50)
    vehicle = forms.CharField(label='Enter the make and model of the vehicle you will be making the trip with:', max_length=50)

class StartConversation(forms.Form):
    message = forms.CharField(label='Enter the message you would like to send to the post owner')