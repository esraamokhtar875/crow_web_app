
import re
from datetime import date
from django.contrib.auth.forms import UserCreationForm, PasswordResetForm, SetPasswordForm
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from django import forms
from django_countries.fields import CountryField

from .models import CustomUser

User = get_user_model()


class RegistrationForm(UserCreationForm):
    username = forms.EmailField(widget=forms.EmailInput(attrs={
        "class": "form-control",
        "placeholder": "Enter your email"
    }))

    first_name = forms.CharField(widget=forms.TextInput(attrs={
        "class": "form-control",
        "type": "text",
        "placeholder": "Enter First Name"
    }))

    last_name = forms.CharField(widget=forms.TextInput(attrs={
        "class": "form-control",
        "type": "text",
        "placeholder": "Enter Last Name"
    }))

    password1 = forms.CharField(widget=forms.PasswordInput(attrs={
        "class": "form-control",
        "type": "password",
        "placeholder": "Enter Password"
    }))

    password2 = forms.CharField(widget=forms.PasswordInput(attrs={
        "class": "form-control",
        "type": "password",
        "placeholder": "Re-enter Password"
    }))

    phone_number = forms.CharField(widget=forms.TextInput(attrs={
        "class": "form-control",
        "type": "text",
        "placeholder": "Enter Phone Number",
    }))

    profile_picture = forms.ImageField(widget=forms.FileInput(attrs={
        "class": "form-control",
        "type": "file"
    }), required=False)

    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = ['username', 'first_name', 'last_name', 'password1', 'password2', 'phone_number', 'profile_picture']

    def clean_first_name(self):
        first_name = self.cleaned_data.get('first_name')
        if len(first_name) < 2:
            raise ValidationError('First name is too short')
        return first_name

    def clean_last_name(self):
        last_name = self.cleaned_data.get('last_name')
        if len(last_name) < 2:
            raise ValidationError('Last name is too short')
        return last_name

    def clean_username(self):
        username = self.cleaned_data.get('username')
        errors = []

        if User.objects.filter(username=username).exists():
            errors.append("This email is already taken. Please choose a different one.")

        elif not re.match(r'^[\w.+-]+@[\w.-]+\.[a-zA-Z]{2,}$', username):
            errors.append("Please enter a valid email address.")

        if errors:
            self.add_error('username', errors)

        return username


class LoginForm(forms.Form):
    username = forms.EmailField(widget=forms.EmailInput(attrs={
        "class": "form-control",
        "placeholder": "Enter your email"
    }))

    password = forms.CharField(widget=forms.PasswordInput(attrs={
        "class": "form-control",
        "placeholder": "Enter your password"
    }))

    def clean_username(self):
        username = self.cleaned_data.get('username')
        errors = []

        if not re.match(r'^[\w.+-]+@[\w.-]+\.[a-zA-Z]{2,}$', username):
            errors.append("Please enter a valid email address.")

        if errors:
            self.add_error('username', errors)

        return username


def validate_facebook_url(value):
    # regex to match Facebook URLs
    regex = r'^https?://(www\.)?facebook\.com/.+'

    if value and not re.match(regex, value):
        return False
    return True


class EditProfileForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'phone_number', 'profile_picture', 'facebook_profile', 'birth_date']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter First Name'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Last Name'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Phone Number'}),
            'profile_picture': forms.FileInput(attrs={'class': 'form-control'}),
            'facebook_profile': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'Enter Facebook Profile URL'}),
            'birth_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }

    def clean_mobile_phone(self):
        phone_number = self.cleaned_data.get('phone_number')
        if phone_number and not re.match(r'^01[0125]{1}[0-9]{8}$', phone_number):
            raise forms.ValidationError("Mobile phone number must be a valid Egyptian phone number.")
        return phone_number

    def clean_first_name(self):
        first_name = self.cleaned_data.get('first_name')
        if len(first_name) < 2:
            raise forms.ValidationError("First name must be at least 2 characters long.")
        return first_name

    def clean_last_name(self):
        last_name = self.cleaned_data.get('last_name')
        if len(last_name) < 2:
            raise forms.ValidationError("Last name must be at least 2 characters long.")
        return last_name

    def clean_profile_picture(self):
        profile_picture = self.cleaned_data.get('profile_picture')
        if not profile_picture:
            return 'user_uploads/default_profile_picture.jpg'
        return profile_picture

    def clean_birth_date(self):
        birth_date = self.cleaned_data.get('birth_date')
        if birth_date:
            today = date.today()
            # check if birthdate is after today's date
            if birth_date > today:
                raise forms.ValidationError("Birthdate cannot be in the future.")
        return birth_date

    def clean_facebook_profile(self):
        facebook_profile = self.cleaned_data.get('facebook_profile')
        if facebook_profile:
            if not validate_facebook_url(facebook_profile):
                raise ValidationError('Invalid Facebook URL')
        return facebook_profile


class ChangePasswordForm(SetPasswordForm):
    class Meta:
        model = get_user_model()
        fields = ['new_password1', 'new_password2']

    new_password1 = forms.CharField(widget=forms.PasswordInput(attrs={
        "class": "form-control",
        "type": "password",
        "placeholder": "Enter Password"
    }))

    new_password2 = forms.CharField(widget=forms.PasswordInput(attrs={
        "class": "form-control",
        "type": "password",
        "placeholder": "Re-enter Password"
    }))


class ResetPasswordForm(PasswordResetForm):
    username = forms.EmailField(widget=forms.EmailInput(attrs={
        "class": "form-control",
        "type": "email",
    }))

    def __init__(self, *args, **kwargs):
        super(ResetPasswordForm, self).__init__(*args, **kwargs)
        self.cleaned_data = None
        self.fields['username'] = self.fields['email']
        del self.fields['email']

    def clean_username(self):
        email = self.cleaned_data['username']

        if not email:
            raise ValidationError("Email field is required.")

        return email

















































# from django import forms
# from django.contrib.auth.forms import UserCreationForm
# from .models import CustomUser
#
# class RegistrationForm(UserCreationForm):
#     first_name = forms.CharField(max_length=30)
#     last_name = forms.CharField(max_length=30)
#     email = forms.EmailField()
#     mobile_phone = forms.CharField(max_length=11)
#     profile_picture = forms.ImageField(required=False)
#
#     class Meta:
#         model = CustomUser
#         fields = ['first_name', 'last_name', 'email', 'mobile_phone', 'profile_picture', 'password1', 'password2']
