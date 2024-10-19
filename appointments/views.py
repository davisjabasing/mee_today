from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from .models import UserProfile, Appointment, Notification
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.contrib.auth.hashers import make_password
from django.contrib import messages

# Login View
def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            return render(request, 'login.html', {'error': 'Invalid credentials'})
    return render(request, 'login.html')

# Register View
def register_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        name = request.POST.get('name')
        profession = request.POST.get('profession')
        location = request.POST.get('location')
        description = request.POST.get('description', '')
        phone_number = request.POST.get('phone_number')
        age = request.POST.get('age')  # Age field
        password = request.POST.get('password')
        password_confirm = request.POST.get('password_confirm')
        photo = request.FILES.get('photo')  # Handle photo upload

        if password != password_confirm:
            return render(request, 'register.html', {'error': "Passwords do not match"})
        
        try:
            # Create the User object
            user = User.objects.create_user(username=username, password=password, first_name=name)
            
            # Create the UserProfile object and save additional details
            user_profile = UserProfile.objects.create(
                user=user,
                profession=profession,
                location=location,
                description=description,
                phone_number=phone_number,
                age=age,  # Save the age
                photo=photo  # Save the photo
            )
            
            # Automatically log in the user after successful registration
            login(request, user)
            return redirect('home')
        except Exception as e:
            return render(request, 'register.html', {'error': str(e)})
    
    return render(request, 'register.html')

# Home View (with Search functionality)
def home_view(request):
    if request.method == 'POST':
        search_name = request.POST.get('name')
        search_profession = request.POST.get('profession')
        search_location = request.POST.get('location')
        users = UserProfile.objects.all()
        if search_name:
            users = users.filter(user__username__icontains=search_name)
        if search_profession:
            users = users.filter(profession__icontains=search_profession)
        if search_location:
            users = users.filter(location__icontains=search_location)
        return render(request, 'home.html', {'users': users})
    return render(request, 'home.html')

# Profile View
def profile_view(request, user_id):
    user_profile = UserProfile.objects.get(user_id=user_id)
    if request.method == 'POST':
        reason = request.POST.get('reason')
        date = request.POST.get('date')
        Appointment.objects.create(
            requester=request.user, 
            recipient=user_profile.user, 
            date=date, 
            reason=reason, 
            status='pending'
        )
        return redirect('home')
    return render(request, 'profile.html', {'profile': user_profile})

# Calendar View
@login_required
def calendar_view(request):
    # Get only accepted appointments
    appointments = Appointment.objects.filter(recipient=request.user, status='accepted')
    return render(request, 'view_calendar.html', {'appointments': appointments})

@login_required
def notifications(request):
    user = request.user

    # Pending appointments
    received_pending_appointments = Appointment.objects.filter(recipient=user, status='pending')
    sent_pending_appointments = Appointment.objects.filter(requester=user, status='pending')

    # Accepted appointments
    received_accepted_appointments = Appointment.objects.filter(recipient=user, status='accepted')
    sent_accepted_appointments = Appointment.objects.filter(requester=user, status='accepted')

    # Rejected appointments
    received_rejected_appointments = Appointment.objects.filter(recipient=user, status='rejected')
    sent_cancelled_appointments = Appointment.objects.filter(requester=user, status='rejected')

    context = {
        'received_pending_appointments': received_pending_appointments,
        'sent_pending_appointments': sent_pending_appointments,
        'received_accepted_appointments': received_accepted_appointments,
        'sent_accepted_appointments': sent_accepted_appointments,
        'received_rejected_appointments': received_rejected_appointments,
        'sent_cancelled_appointments': sent_cancelled_appointments,
    }
    return render(request, 'notifications.html', context)

@login_required
def accept_appointment(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id)
    if request.method == 'POST' and appointment.recipient == request.user:
        appointment.status = 'accepted'
        appointment.save()
        return redirect('notifications')

@login_required
def reject_appointment(request, appointment_id):
    # Get the appointment object
    appointment = get_object_or_404(Appointment, id=appointment_id)

    # Check if the current user is the recipient (y) who can reject the request
    if appointment.recipient == request.user:
        # Update the status to 'rejected'
        appointment.status = 'rejected'
        appointment.save()
        
        # Notify the requester (x) that their appointment was rejected
        messages.success(request, "Appointment request rejected.")
        return redirect('notifications')  # Adjust this redirect as needed
    else:
        # If the user is not authorized to reject, show an error
        messages.error(request, "You are not authorized to reject this appointment.")
        return redirect('notifications')

@login_required
def modify_appointment(request, appointment_id):
    # Retrieve the appointment
    appointment = get_object_or_404(Appointment, id=appointment_id, recipient=request.user)

    if request.method == 'POST':
        # Process the form submission (modification)
        new_date = request.POST.get('new_date')
        new_reason = request.POST.get('new_reason')

        if new_date and new_reason:
            # Update the appointment with new values
            appointment.date = new_date
            appointment.reason = new_reason
            appointment.status = 'modified'
            appointment.save()

            # Redirect to notifications or any page after modification
            return redirect('notifications')
        else:
            return render(request, 'modify_appointment.html', {'appointment': appointment, 'error': 'All fields are required.'})

    # For GET requests, display the modification form
    return render(request, 'modify_appointment.html', {'appointment': appointment})

def notify_user(user, message):
    # Here, implement a notification system to notify the user (e.g., saving notifications in a model)
    pass

def logout_view(request):
    logout(request)
    return redirect('login')  # Redirect to the login page after logout

@login_required
def view_calendar(request):
    user = request.user
    appointments = Appointment.objects.filter(receiver=user)  # Appointments where the logged-in user is the receiver
    
    context = {
        'appointments': appointments
    }
    return render(request, 'view_calendar.html', context)

@login_required
def handle_appointment_status(request):
    if request.method == 'POST':
        appointment_id = request.POST.get('appointment_id')
        status = request.POST.get('status')
        
        appointment = Appointment.objects.get(id=appointment_id)
        if appointment.receiver == request.user:
            appointment.status = status
            appointment.save()
            return redirect('notifications')
        else:
            return redirect('home')
        
def check_username(request):
    username = request.GET.get('username', None)
    data = {
        'is_taken': User.objects.filter(username__iexact=username).exists()
    }
    return JsonResponse(data)

def forgot_password_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        phone_number = request.POST.get('phone_number')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')

        # Check if passwords match
        if new_password != confirm_password:
            return render(request, 'forgot_password.html', {'error': 'Passwords do not match'})
        
        try:
            # Get the user and check phone number
            user = User.objects.get(username=username)
            user_profile = UserProfile.objects.get(user=user)

            if user_profile.phone_number == phone_number:
                # Update the user's password if the phone number matches
                user.password = make_password(new_password)
                user.save()
                return redirect('login')  # Redirect to login after successful password reset
            else:
                return render(request, 'forgot_password.html', {'error': 'Username or phone number incorrect'})

        except User.DoesNotExist:
            return render(request, 'forgot_password.html', {'error': 'Username or phone number incorrect'})
    
    return render(request, 'forgot_password.html')






