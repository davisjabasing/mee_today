from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from .models import UserProfile, Appointment, Notification
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse

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
        # Get all required data from POST request
        username = request.POST.get('username')
        password = request.POST.get('password')
        name = request.POST.get('name')
        profession = request.POST.get('profession')
        location = request.POST.get('location')
        description = request.POST.get('description')
        
        # Check for existing username
        if User.objects.filter(username=username).exists():
            return render(request, 'register.html', {'error': 'Username already taken'})
        
        # Create user and user profile
        user = User.objects.create_user(username=username, password=password)
        UserProfile.objects.create(user=user, profession=profession, location=location, description=description)
        return redirect('login')
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








