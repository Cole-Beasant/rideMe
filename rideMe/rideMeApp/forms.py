from django import forms

class SignUpForm(forms.Form):
    # class Meta:
        # model = User
        # fields = ('username', 'firstName', 'lastName', 'email', 'password')
    username = forms.CharField(label='Enter your username:')
    firstName = forms.CharField(label='Enter your First Name:')
    lastName = forms.CharField(label='Enter your Last Name:')
    email = forms.EmailField(label="Enter your email address:")
    password = forms.CharField(label='Enter your password:', widget=forms.PasswordInput())
    confirmPassword = forms.CharField(label='Confirm you password:', widget=forms.PasswordInput())

class LoginForm(forms.Form):
    username = forms.CharField(label='Enter your username')
    password = forms.CharField(label='Enter your password', widget=forms.PasswordInput)

class ResetPasswordForm(forms.Form):
    username = forms.CharField(label='Enter your username:')
    newPassword = forms.CharField(label='Enter your new password:', widget=forms.PasswordInput)
    confirmNewPassword = forms.CharField(label='Confirm your new password:', widget=forms.PasswordInput)

class AddPostingForm(forms.Form):
    numAvailableSeats = forms.IntegerField(label='Enter the number of available seats for your trip:')
    tripDate = forms.DateTimeField(label='Enter the date the trip will be occuring:', widget=forms.DateInput(
        attrs={'type': 'date', 'placeholder': 'yyyy-mm-dd', 'class': 'form-control'}
    ))   
    tripTime = forms.TimeField(label='Enter the time the trip will be occuring in the format HH:MM in military time:', widget=forms.DateInput(
        attrs={'class': 'timepicker'}
    ))
    pickupLocation = forms.CharField(label='Enter the general location of where you can pick up passengers:', max_length=50)
    dropoffLocation = forms.CharField(label='Enter the general location where you can drop off passenger:', max_length=50)
    vehicle = forms.CharField(label='Enter the make and model of the vehicle you will be making the trip with:', max_length=50)

class StartConversation(forms.Form):
    message = forms.CharField(max_length=500, label='Enter the message you would like to send to the post owner')

class AddReviewForm(forms.Form):
    rating = forms.FloatField(min_value=0, max_value=5, label='Enter a rating of your experience with this user from 0 to 5 with 5 being the best:')
    description = forms.CharField(max_length=500, label='Enter a description of your experience with this user (max 500 characters):')

class SendMessageForm(forms.Form):
    message = forms.CharField(max_length=500, label='Enter Message:')