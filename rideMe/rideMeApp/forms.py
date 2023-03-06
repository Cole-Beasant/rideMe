from django import forms
from django.utils import timezone

class SignUpForm(forms.Form):
    username = forms.CharField(label='Enter your username:')
    firstName = forms.CharField(label='Enter your First Name:')
    lastName = forms.CharField(label='Enter your Last Name:')
    email = forms.EmailField(label="Enter your email address:")
    password = forms.CharField(label='Enter your password:', widget=forms.PasswordInput)
    confirmPassword = forms.CharField(label='Confirm you password:', widget=forms.PasswordInput)

class LoginForm(forms.Form):
    username = forms.CharField(label='Enter your username')
    password = forms.CharField(label='Enter your password', widget=forms.PasswordInput)

class ResetPasswordForm(forms.Form):
    username = forms.CharField(label='Enter your username:')
    newPassword = forms.CharField(label='Enter your new password:', widget=forms.PasswordInput)
    confirmNewPassword = forms.CharField(label='Confirm your new password:', widget=forms.PasswordInput)

class AddPostingForm(forms.Form):
    numAvailableSeats = forms.IntegerField(label='Enter the number of available seats for your trip:', widget=forms.NumberInput(attrs={'placeholder':'Number of Seats'}))
    tripDate = forms.DateTimeField(label='Enter the date the trip will be occuring:', widget=forms.DateInput(
        attrs={'type': 'date', 'placeholder': 'yyyy-mm-dd', 'class': 'form-control'}
    ))   
    tripTime = forms.TimeField(label='Enter the time the trip will be occuring:', widget=forms.DateInput(
        attrs={'class': 'timepicker', 'type':'time'}
    ))
    pickupLocation = forms.CharField(label='Enter the general location where you can pick up passengers:', max_length=50, widget=forms.TextInput(attrs={'placeholder':'Pickup Location'}))
    dropoffLocation = forms.CharField(label='Enter the general location where you can drop off passengers:', max_length=50, widget=forms.TextInput(attrs={'placeholder':'Dropoff Location'}))
    vehicle = forms.CharField(label='Enter the make and model of the vehicle you will be making the trip with:', max_length=50, widget=forms.TextInput(attrs={'placeholder':'Vehicle Information'}))

    def clean(self):
        cleaned_data = super().clean()
        date = cleaned_data.get('tripDate')
        seats = cleaned_data.get('numAvailableSeats')
        try:
            if int(seats)<1:
                self.add_error('numAvailableSeats', forms.ValidationError('The number of available seats must be a positive integer'))
        except:
            self.add_error('numAvailableSeats', forms.ValidationError('The number of available seats must be a positive integer'))
        if not (date > timezone.now()):
            self.add_error('tripDate', forms.ValidationError('Please put a date in the future'))
        return cleaned_data

class UpdatePickupLocation(forms.Form):
    pickupLocation = forms.CharField(max_length=50, label='New pick up location:')

class UpdateDropoffLocation(forms.Form):
    dropoffLocation = forms.CharField(max_length=50, label='New drop off location:')

class UpdateTripDate(forms.Form):
    tripDate = forms.DateTimeField(label='New date:', widget=forms.DateInput(
        attrs={'type': 'date', 'placeholder': 'yyyy-mm-dd', 'class': 'form-control', 'required': 'false'}
    ))
    def clean(self):
        cleaned_data = super().clean()
        date = cleaned_data.get('tripDate')
        if type(date) == type(None):
            return cleaned_data
        if not (date > timezone.now()):
            self.add_error('tripDate', forms.ValidationError('Please put a date in the future'))
        return cleaned_data

class UpdateTripTime(forms.Form):
    tripTime = forms.TimeField(label='New time in the format HH:MM in military time:', widget=forms.DateInput(
        attrs={'class': 'timepicker', 'type':'time'}
    ))

class UpdateNumAvailableSeats(forms.Form):
    numAvailableSeats = forms.IntegerField(label='New number of available seats:')
    def clean(self):
        cleaned_data = super().clean()
        seats = cleaned_data.get('numAvailableSeats')
        try:
            if int(seats)<0:
                self.add_error('numAvailableSeats', forms.ValidationError('Please put a postive integer'))
        except:
            self.add_error('numAvailableSeats', forms.ValidationError('Please put a positive integer'))
        return cleaned_data

class UpdateVehicle(forms.Form):
    vehicle = forms.CharField(label='New vehicle', max_length=50)

class StartConversation(forms.Form):
    message = forms.CharField(max_length=500, label='Enter the message you would like to send to the post owner')

class AddReviewForm(forms.Form):
    rating = forms.FloatField(min_value=0, max_value=5, label='Enter a rating of your experience with this user from 0 to 5 with 5 being the best:', widget=forms.NumberInput(attrs={'placeholder': '0-5'}))
    description = forms.CharField(max_length=500, label='Enter a description of your experience with this user (max 500 characters):', widget=forms.Textarea(attrs={'placeholder':'Message'}))

class SendMessageForm(forms.Form):
    message = forms.CharField(max_length=500, label='Enter Message:', widget=forms.TextInput(attrs={'placeholder': 'Message'}))