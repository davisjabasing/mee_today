from django.contrib import admin
from .models import UserProfile

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'email', 'phone_number', 'profession', 'city', 'state')  # Add fields to display
    search_fields = ('email', 'phone_number', 'user__username')  # Make email searchable
