
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django_countries.fields import CountryField


class CustomUser(AbstractUser):
    phone_number = models.CharField(
        max_length=11,
        validators=[RegexValidator(regex=r'^01[0125][0-9]{8}$', message='Enter a valid Egyptian phone number.')],
        unique=True,
        default='01000000000'
    )
    profile_picture = models.ImageField(
        upload_to='user_uploads/',
        null=True,
        blank=True,
        default='user_uploads/default_profile_picture.jpg'
    )
    facebook_profile = models.URLField(max_length=200, blank=True, null=True)
    birth_date = models.DateField(null=True, blank=True)
    country = CountryField(blank_label='Select a country', null=True, blank=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    @property
    def profile_picture_url(self):
        if self.profile_picture:
            return self.profile_picture.url
        return '/media/user_uploads/default_profile_picture.jpg'














# from django.db import models
# from django.contrib.auth.models import User
# from django.core.validators import RegexValidator
# from django_countries.fields import CountryField
#
#
# class CustomUser(User):
#     phone_number = models.CharField(max_length=11, validators=[RegexValidator(regex='^01[0125]{1}[0-9]{8}$', message='Enter a valid Egyptian phone number.')], unique=True)
#     profile_picture = models.ImageField(upload_to='user_uploads/', null=True, blank=True, default='user_uploads/default_profile_picture.jpg')
#     facebook_profile = models.URLField(max_length=200, blank=True, null=True)
#     birth_date = models.DateField(null=True, blank=True)
#     country = CountryField(blank_label='Select a country', null=True, blank=True)
#
#     def __str__(self):
#         return f"{self.first_name} {self.last_name}"
#
#     @property
#     def profile_picture_url(self):
#         return f'/media/{self.profile_picture}'
#

























# from django.db import models
# from django.contrib.auth.models import AbstractUser
# from django.core.validators import RegexValidator
#
#
# class CustomUser(AbstractUser):
#     mobile_phone = models.CharField(
#         validators=[RegexValidator(regex=r'^01[0-2,5]{1}[0-9]{8}$', message="Enter a valid Egyptian phone number")],
#         max_length=11,
#         unique=True
#     )
#     profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
#
    

