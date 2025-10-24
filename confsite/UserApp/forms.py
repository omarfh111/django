from django import forms 
from .models import User
from django.contrib.auth.forms import UserCreationForm
class UserResgisterForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username','first_name','last_name','email','affiliation','nationality','password','password2']
        widgets = {
            'email' : forms.EmailInput(attrs={
                'palceholder' : "Email universitaire"
            }),
            'password1' : forms.PasswordInput(),
            'password2' : forms.PasswordInput(),
        }