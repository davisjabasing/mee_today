from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    profession = models.CharField(max_length=100)
    location = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    phone_number = models.CharField(max_length=15)  # Phone number
    photo = models.ImageField(upload_to='profile_photos/', blank=True, null=True)  # Photo field
    sex = models.CharField(max_length=10)
    age = models.IntegerField(null=True, blank=True)  # New age field

    def __str__(self):
        return self.user.username

class Appointment(models.Model):
    requester = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_requests')
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_requests')
    date = models.DateTimeField()
    reason = models.TextField()
    status = models.CharField(max_length=10, choices=[('pending', 'Pending'), ('accepted', 'Accepted'), ('modified', 'Modified'), ('rejected', 'Rejected')])

class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    is_read = models.BooleanField(default=False)

# from django.db import models
# from django.contrib.auth.models import User
# from django.utils import timezone

# # Model for User Profile (Additional information apart from built-in User model)
# class UserProfile(models.Model):
#     user = models.OneToOneField(User, on_delete=models.CASCADE)
#     photo = models.ImageField(upload_to='profiles/', blank=True, null=True)  # Optional photo field
#     sex = models.CharField(max_length=10, blank=True)  # Gender of the user
#     address = models.TextField(blank=True)  # User address
#     profession = models.CharField(max_length=100)  # Profession (e.g., Doctor, Consultant)
#     description = models.TextField(blank=True)  # Optional description provided by the user

#     def __str__(self):
#         return self.user.username

# # Model for Appointment
# class Appointment(models.Model):
#     STATUS_CHOICES = (
#         ('pending', 'Pending'),
#         ('accepted', 'Accepted'),
#         ('rejected', 'Rejected'),
#         ('modified', 'Modified'),
#         ('completed', 'Completed'),
#     )

#     requester = models.ForeignKey(User, on_delete=models.CASCADE, related_name='requested_appointments')
#     receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_appointments')
#     date = models.DateField()  # Date of the appointment
#     time = models.TimeField()  # Time of the appointment
#     reason = models.TextField()  # Reason for the appointment
#     status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')  # Status of the appointment
#     modified_time = models.TimeField(blank=True, null=True)  # In case the receiver modifies the appointment time

#     created_at = models.DateTimeField(default=timezone.now)  # Set default to current timestamp
#     updated_at = models.DateTimeField(auto_now=True)  # Auto-update on modification

#     def __str__(self):
#         return f"Appointment with {self.receiver.username} on {self.date} at {self.time}"

# # Model for Notifications
# class Notification(models.Model):
#     APPOINTMENT_STATUS = (
#         ('request', 'Appointment Request'),
#         ('accepted', 'Appointment Accepted'),
#         ('modified', 'Appointment Modified'),
#         ('rejected', 'Appointment Rejected'),
#         ('cancelled', 'Appointment Cancelled'),
#     )

#     user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
#     appointment = models.ForeignKey(Appointment, on_delete=models.CASCADE, default=1)  # Set default appointment ID
#     message = models.TextField()  # Notification message
#     status = models.CharField(max_length=20, choices=APPOINTMENT_STATUS)
#     is_read = models.BooleanField(default=False)  # Track if the notification has been read
#     created_at = models.DateTimeField(default=timezone.now)  # When the notification was created

#     def __str__(self):
#         return f"Notification for {self.user.username} - {self.status}"
