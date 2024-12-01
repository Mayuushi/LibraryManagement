from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser

class UserRegisterForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'password1', 'password2']

class AdminRegisterForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'password1', 'password2']

    def save(self, commit=True):
        
        user = super().save(commit=False)
        user.is_superuser = True  # Set superuser rights
        user.is_staff = True  # Set the admin rights
        if commit:
            user.save()
        return user
