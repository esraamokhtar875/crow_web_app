
from django.contrib import admin
from django.utils.safestring import mark_safe

from .models import CustomUser


class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'email_display', 'phone_number', 'facebook_profile', 'birth_date', 'country', 'is_active')
    list_filter = ('country', 'birth_date')
    search_fields = ('country', 'email')
    list_per_page = 10
    list_max_show_all = 10
    fieldsets = (
        (None, {
            'fields': ('username', 'is_active')
        }),
        ('Personal Info', {
            'fields': ('first_name', 'last_name', 'country', 'birth_date', 'phone_number', 'facebook_profile', 'profile_picture')
        }),
        ('Important dates', {
            'fields': ('last_login', 'date_joined')
        })
    )

    def profile_picture_display(self, obj):
        return mark_safe(f'<img src="{obj.profile_picture.url}" width="40" height="40" />')

    profile_picture_display.short_description = 'Profile Picture'

    def email_display(self, obj):
        return mark_safe(f'{obj.username}')

    email_display.short_description = 'Email address'

    def formfield_for_dbfield(self, db_field, **kwargs):
        if db_field.name == 'username':
            kwargs['label'] = 'email'
        return super().formfield_for_dbfield(db_field, **kwargs)


admin.site.register(CustomUser, CustomUserAdmin)
