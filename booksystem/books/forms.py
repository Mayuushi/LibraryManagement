# books/forms.py
from django import forms
from .models import Book
from django.contrib.auth import get_user_model

CustomUser = get_user_model()


class BookForm(forms.ModelForm):
    class Meta:
        model = Book
        fields = ['title', 'author', 'description','image']


class CustomUserEditForm(forms.ModelForm):
    password = forms.CharField(required=False, widget=forms.PasswordInput)
    confirm_password = forms.CharField(required=False, widget=forms.PasswordInput)

    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'first_name', 'last_name']  # Add additional fields as necessary

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.instance.is_superuser:
            # Hide admin-specific fields for regular users
            self.fields.pop('some_admin_specific_field', None)


