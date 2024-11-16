from django import forms
from .models import UserProfile

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['name', 'profession', 'address', 'city', 'state', 'district', 'pincode', 'designation', 'company', 'university', 'field_of_study', 'description', 'phone_number', 'email', 'date_of_birth', 'sex', 'photo']
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date'}),
        }