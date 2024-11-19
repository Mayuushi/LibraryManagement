from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import StudentProfile, FacultyProfile

class StudentRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(required=True)
    last_name = forms.CharField(required=True)
    birthdate = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
    )
    contact_number = forms.CharField(
        max_length=15,
        widget=forms.TextInput(attrs={'class': 'form-control', 'pattern': '[0-9]{11}', 'placeholder': '09XXXXXXXXX'})
    )
    address = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 2})
    )
    course = forms.ChoiceField(
        choices=[
            ('', 'Select Course'),
            ('BS in Computer Science', 'BS in Computer Science'),
            ('BS in Information Technology', 'BS in Information Technology'),
            ('BS in Computer Engineering', 'BS in Computer Engineering'),
            ('BS in Civil Engineering', 'BS in Civil Engineering'),
            ('BS in Mechanical Engineering', 'BS in Mechanical Engineering'),
            ('BS in Architecture', 'BS in Architecture'),
        ],
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    year_level = forms.ChoiceField(
        choices=StudentProfile.YEAR_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    student_id = forms.CharField(
        max_length=20,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter Student ID'
        }),
        help_text='Format: YYYY-XXXXX'
    )

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2', 'first_name', 'last_name')
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in ['username', 'password1', 'password2']:
            self.fields[field].help_text = None

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        
        if commit:
            user.save()
            StudentProfile.objects.create(
                user=user,
                student_id=self.cleaned_data['student_id'],
                birthdate=self.cleaned_data['birthdate'],
                contact_number=self.cleaned_data['contact_number'],
                address=self.cleaned_data['address'],
                course=self.cleaned_data['course'],
                year_level=self.cleaned_data['year_level']
            )
        return user

    def clean_student_id(self):
        student_id = self.cleaned_data.get('student_id')
        if not student_id:
            raise forms.ValidationError("Student ID is required.")
        if StudentProfile.objects.filter(student_id=student_id).exists():
            raise forms.ValidationError("This Student ID is already in use.")
        return student_id

class StudentProfileForm(forms.ModelForm):
    class Meta:
        model = StudentProfile
        fields = ['student_id', 'course', 'year_level', 'contact_number', 'address']
        widgets = {
            'student_id': forms.TextInput(attrs={'class': 'form-control'}),
            'course': forms.TextInput(attrs={'class': 'form-control'}),
            'year_level': forms.Select(attrs={'class': 'form-control'}),
            'contact_number': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

class FacultyRegistrationForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )
    department = forms.ChoiceField(
        choices=[
            ('', 'Select Department'),
            ('College of Engineering', 'College of Engineering'),
            ('College of Computer Studies', 'College of Computer Studies'),
            ('College of Architecture', 'College of Architecture'),
            ('College of Management', 'College of Management'),
            ('College of Education', 'College of Education'),
        ],
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    contact_number = forms.CharField(
        max_length=11,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'pattern': '[0-9]{11}',
            'placeholder': '09XXXXXXXXX'
        })
    )

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'username', 
                 'password1', 'password2', 'department', 'contact_number')
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'username': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in ['username', 'password1', 'password2']:
            self.fields[field].help_text = None

    def save(self, commit=True):
        user = super().save(commit=False)
        user.is_staff = True
        user.is_superuser = False
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
            FacultyProfile.objects.create(
                user=user,
                department=self.cleaned_data['department'],
                contact_number=self.cleaned_data['contact_number']
            )
        return user

    def clean_contact_number(self):
        contact = self.cleaned_data.get('contact_number')
        if not contact.isdigit() or len(contact) != 11 or not contact.startswith('09'):
            raise forms.ValidationError('Please enter a valid Philippine mobile number (09XXXXXXXXX)')
        return contact
