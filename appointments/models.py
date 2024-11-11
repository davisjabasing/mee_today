from datetime import date
from django.db import models
from django.contrib.auth.models import User

from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
    # Link to the Django User model (one-to-one relationship)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    
    # Basic Details
    phone_number = models.CharField(max_length=15, unique=True)
    date_of_birth = models.DateField(null=True, blank=True)
    sex = models.CharField(max_length=10, choices=[('Male', 'Male'), ('Female', 'Female')])
    age = models.IntegerField(null=True, blank=True)  # Calculated from date_of_birth
    
    # Communication Details
    address = models.TextField()
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    district = models.CharField(max_length=100)
    pincode = models.CharField(max_length=10)
    
    # Professional Details
    profession = models.CharField(max_length=20, choices=[('Student', 'Student'), ('Professional', 'Professional')])
    designation = models.CharField(max_length=100, blank=True)  # Only for professionals
    company = models.CharField(max_length=100, blank=True)      # Only for professionals
    university = models.CharField(max_length=100, blank=True)   # Only for students
    field_of_study = models.CharField(max_length=100, blank=True)  # Only for students
    description = models.TextField(blank=True)
    
    # Optional Profile Photo
    photo = models.ImageField(upload_to='profile_pics/', blank=True, null=True)

    def save(self, *args, **kwargs):
        # Calculate age based on date_of_birth, if provided
        if self.date_of_birth:
            self.age = date.today().year - self.date_of_birth.year
        super(UserProfile, self).save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.user.username}'s profile"


class Appointment(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('modified', 'Modified'),
        ('rejected', 'Rejected'),
    ]

    requester = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_requests')
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_requests')
    date = models.DateTimeField()
    end_time = models.DateTimeField()  # New field for the end time
    reason = models.TextField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')

    def __str__(self):
        return f"Appointment from {self.requester.username} to {self.recipient.username} on {self.date}"

class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Notification for {self.user.username} at {self.created_at}"

class CalendarEvent(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    appointment = models.ForeignKey(Appointment, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)