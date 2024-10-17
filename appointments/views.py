from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from .models import UserProfile, Appointment, Notification
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.contrib.auth.hashers import make_password

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
def calendar_view(request):
    appointments = Appointment.objects.filter(recipient=request.user, status='accepted')
    return render(request, 'view_calendar.html', {'appointments': appointments})

# Notifications View
# def notifications_view(request):
#     notifications = Notification.objects.filter(user=request.user)
#     return render(request, 'notifications.html', {'notifications': notifications})

@login_required
def notifications(request):
    user = request.user
    received_appointments = Appointment.objects.filter(receiver=user)
    sent_appointments = Appointment.objects.filter(requester=user)

    context = {
        'received_appointments': received_appointments,
        'sent_appointments': sent_appointments,
    }
    return render(request, 'notifications.html', context)

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






