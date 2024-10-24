from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from .models import CalendarEvent, UserProfile, Appointment
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.contrib.auth.hashers import make_password
from django.contrib import messages
import datetime


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
    name = profession = location = None
    users = suggested_users = None

    if request.method == "POST":
        name = request.POST.get('name')
        profession = request.POST.get('profession')
        location = request.POST.get('location')

        # Filter users based on search terms
        users = UserProfile.objects.all()
        if name:
            users = users.filter(user__username__icontains=name)
        if profession:
            users = users.filter(profession__icontains=profession)
        if location:
            users = users.filter(location__icontains=location)

        # Get suggested users if no results are found
        if not users.exists():
            suggested_users = UserProfile.objects.exclude(user=request.user).order_by('?')[:2]
        else:
            suggested_users = None

        # Stay on the same page but pass search results to the GET method
        return redirect(f'{request.path}?name={name}&profession={profession}&location={location}')

    # Handle GET request (after the redirect)
    if request.method == "GET":
        name = request.GET.get('name', '')
        profession = request.GET.get('profession', '')
        location = request.GET.get('location', '')

        if name or profession or location:
            users = UserProfile.objects.all()
            if name:
                users = users.filter(user__username__icontains=name)
            if profession:
                users = users.filter(profession__icontains=profession)
            if location:
                users = users.filter(location__icontains=location)

            if not users.exists():
                suggested_users = UserProfile.objects.exclude(user=request.user).order_by('?')[:2]

    context = {
        'users': users,
        'suggested_users': suggested_users,
        'name': name,  # Pass the search terms back to the template
        'profession': profession,
        'location': location,
    }

    return render(request, 'home.html', context)

# Profile View
@login_required
def profile_view(request, user_id):
    user_profile = UserProfile.objects.get(user_id=user_id)
    
    if request.method == 'POST':
        reason = request.POST.get('reason')
        date = request.POST.get('date')
        time_period = request.POST.get('time_period')

        # Parse the date correctly using datetime.datetime.strptime
        start_time = datetime.datetime.strptime(date, '%Y-%m-%dT%H:%M')

        # Default end_time in case no time_period is selected
        end_time = start_time

        # Determine the end time based on the time_period selected by the user
        if time_period == '15':
            end_time = start_time + datetime.timedelta(minutes=15)
        elif time_period == '30':
            end_time = start_time + datetime.timedelta(minutes=30)
        elif time_period == '45':
            end_time = start_time + datetime.timedelta(minutes=45)
        elif time_period == '60':
            end_time = start_time + datetime.timedelta(minutes=60)
        elif time_period == 'full_day':
            end_time = start_time + datetime.timedelta(hours=24)
        else:
            # If the time_period is invalid or missing, we could log this or return an error
            print("Invalid or missing time_period. Defaulting end_time to start_time.")
        
        # Save the appointment with the calculated time
        Appointment.objects.create(
            requester=request.user,
            recipient=user_profile.user,
            date=start_time,
            end_time=end_time,  # End time will always have a value now
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
        # Update the status of the appointment to 'accepted'
        appointment.status = 'accepted'
        appointment.save()

        # Update both calendars by creating events for both users
        CalendarEvent.objects.create(user=appointment.requester, appointment=appointment)
        CalendarEvent.objects.create(user=appointment.recipient, appointment=appointment)
        
        return redirect('notifications')

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

@login_required
def edit_profile(request):
    profile = request.user.userprofile  # Fetch UserProfile instance for the logged-in user
    
    if request.method == 'POST':
        # Update only fields that have changed
        if 'profession' in request.POST and request.POST['profession'] != profile.profession:
            profile.profession = request.POST['profession']

        if 'location' in request.POST and request.POST['location'] != profile.location:
            profile.location = request.POST['location']

        if 'description' in request.POST and request.POST['description'] != profile.description:
            profile.description = request.POST['description']

        if 'phone_number' in request.POST and request.POST['phone_number'] != profile.phone_number:
            profile.phone_number = request.POST['phone_number']

        if 'age' in request.POST and request.POST['age'] != str(profile.age):
            profile.age = request.POST['age']

        if 'sex' in request.POST and request.POST['sex'] != profile.sex:
            profile.sex = request.POST['sex']

        if 'photo' in request.FILES:
            profile.photo = request.FILES['photo']  # Update photo if a new one is uploaded

        profile.save()  # Save the changes to the profile
        messages.success(request, 'Profile updated successfully!')
        return redirect('home')  # Redirect to home after saving changes

    return render(request, 'edit_profile.html', {
        'user': request.user,
        'profile': profile
    })

def change_password(request):
    if request.method == 'POST':
        current_password = request.POST.get('current_password')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')

        user = request.user

        # Check if current password is correct
        if not user.check_password(current_password):
            messages.error(request, "Current password is incorrect. Please try again.")
            return redirect('edit_profile')

        # Check if new password and confirm password match
        if new_password != confirm_password:
            messages.error(request, "New passwords do not match. Please try again.")
            return redirect('edit_profile')

        # If everything is correct, show a confirmation prompt
        if request.POST.get('confirm_change') == 'yes':  # Assuming 'confirm_change' holds the value from the prompt
            # Change the password and update the session
            user.set_password(new_password)
            user.save()
            update_session_auth_hash(request, user)  # Prevents logout after password change

            # Show success message
            messages.success(request, "Password changed successfully.")
            return redirect('edit_profile')

        # If the user cancels the password change
        messages.info(request, "Password change cancelled.")
        return redirect('edit_profile')

    return render(request, 'edit_profile.html')

