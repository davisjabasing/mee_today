from datetime import date
from django.db import models
from django.contrib.auth.models import User

from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
    # Link to the Django User model (one-to-one relationship)
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    # Basic Details
    name = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=15, unique=True, blank=True, null=True)
    email = models.EmailField(unique=True, blank=True, null=True)  # Optional email for flexibility
    date_of_birth = models.DateField(null=True, blank=True)
    sex = models.CharField(
        max_length=10, 
        choices=[('Male', 'Male'), ('Female', 'Female'), ('NoPrefer', 'NoPrefer')],
        default='Not Specified'
    )
    age = models.PositiveIntegerField(null=True, blank=True)  # Calculated from date_of_birth

    # Communication Details
    address = models.TextField(blank=True)
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, blank=True)
    district = models.CharField(max_length=100, blank=True)
    pincode = models.CharField(max_length=10, blank=True)

    # Professional Details
    profession = models.CharField(
        max_length=20, 
        choices=[('Student', 'Student'), ('Professional', 'Professional')],
        blank=True
    )
    designation = models.CharField(max_length=100, blank=True)  # For professionals
    company = models.CharField(max_length=100, blank=True)      # For professionals
    university = models.CharField(max_length=100, blank=True)   # For students
    field_of_study = models.CharField(max_length=100, blank=True)  # For students
    description = models.TextField(blank=True)

    # Optional Profile Photo
    photo = models.ImageField(upload_to='profile_pics/', blank=True, null=True)

    def save(self, *args, **kwargs):
        if self.date_of_birth:
            today = date.today()
            self.age = today.year - self.date_of_birth.year - (
                (today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day)
            )
        super().save(*args, **kwargs)

    # def save(self, *args, **kwargs):
    #     # Calculate age based on date_of_birth, if provided
    #     if self.date_of_birth:
    #         today = date.today()
    #         self.age = today.year - self.date_of_birth.year - (
    #             (today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day)
    #         )
    #     super(UserProfile, self).save(*args, **kwargs)

    def clean(self):
        from django.core.exceptions import ValidationError
        # Ensure at least one of email or phone number is provided
        if not self.phone_number and not self.email:
            raise ValidationError("Either phone number or email must be provided.")

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