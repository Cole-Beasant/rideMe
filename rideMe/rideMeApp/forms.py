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

class LoginForm(forms.Form):
    username = forms.CharField(label='Enter your username')
    password = forms.CharField(label='Enter your password')