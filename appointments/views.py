import json
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from .models import UserProfile, Appointment, Notification
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.contrib.auth.hashers import make_password
from django.contrib import messages
from datetime import datetime, timedelta
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.db.models import Q
from django.db import transaction
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.conf import settings
from django.utils.timezone import now
from django.contrib.auth.tokens import PasswordResetTokenGenerator
import random




token_generator = PasswordResetTokenGenerator()



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

def register_view(request):
    if request.method == 'POST':
        # Get all form inputs
        username = request.POST.get('username')
        name = request.POST.get('name')
        profession = request.POST.get('profession', '')
        address = request.POST.get('address', '')
        city = request.POST.get('city', '')
        state = request.POST.get('state', '')
        district = request.POST.get('district', '')
        pincode = request.POST.get('pincode', '')
        designation = request.POST.get('designation', '')
        company = request.POST.get('company', '')
        university = request.POST.get('university', '')
        field_of_study = request.POST.get('field_of_study', '')
        description = request.POST.get('description', '')
        phone_number = request.POST.get('phone_number', '')
        email = request.POST.get('email')
        date_of_birth_str = request.POST.get('date_of_birth')
        sex = request.POST.get('sex')
        password = request.POST.get('password')
        password_confirm = request.POST.get('password_confirm')
        photo = request.FILES.get('photo')

        # Convert date_of_birth string to a date object
        try:
            date_of_birth = datetime.strptime(date_of_birth_str, '%Y-%m-%d').date()
        except ValueError:
            return render(request, 'register.html', {'error': "Invalid Date of Birth format."})

        # Check if passwords match
        if password != password_confirm:
            return render(request, 'register.html', {'error': "Passwords do not match."})

        # Ensure email is provided
        if not email:
            return render(request, 'register.html', {'error': "Email is mandatory."})

        try:
            with transaction.atomic():
                # Create the User object
                user = User.objects.create_user(username=username, password=password, first_name=name)

                # Create the UserProfile object
                UserProfile.objects.create(
                    user=user,
                    name=name,
                    profession=profession,
                    phone_number=phone_number if phone_number else None,
                    email=email,
                    date_of_birth=date_of_birth,
                    sex=sex,
                    address=address,
                    city=city,
                    state=state,
                    district=district,
                    pincode=pincode,
                    designation=designation,
                    company=company,
                    university=university,
                    field_of_study=field_of_study,
                    description=description,
                    photo=photo
                )

                # Send a welcome email
                try:
                    send_mail(
                        subject="Welcome to Mee Today!",
                        message=f"Hi {name},\n\nThank you for choosing Mee Today! We’re excited to provide you with an exceptional experience.",
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        recipient_list=[email],
                    )
                except Exception as e:
                    return render(request, 'register.html', {'error': f"Error sending email: {str(e)}"})

                # Automatically log in the user and redirect to the home page
                login(request, user)
                return redirect('home')

        except Exception as e:
            # Catch errors and ensure no partial data is saved
            return render(request, 'register.html', {'error': str(e)})

    return render(request, 'register.html')

def check_email(request):
    email = request.GET.get('email', '').strip()
    is_taken = UserProfile.objects.filter(email=email).exists()

    return JsonResponse({'is_taken': is_taken})

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
            users = users.filter(
                Q(city__icontains=location) | 
                Q(state__icontains=location) | 
                Q(address__icontains=location)
            )

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
                users = users.filter(
                    Q(city__icontains=location) | 
                    Q(state__icontains=location)
                )

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

def logout_view(request):
    logout(request)
    return redirect('login')

def check_username(request):
    username = request.GET.get('username', None)
    data = {
        'is_taken': User.objects.filter(username__iexact=username).exists()
    }
    return JsonResponse(data)

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

@login_required
def profile_view(request, user_id):
    user_profile = get_object_or_404(UserProfile, user_id=user_id)
    received_requests = Appointment.objects.filter(recipient=request.user, status='pending')
    
    # Profession-specific details
    if user_profile.profession == "Student":
        profession_details = f" {user_profile.field_of_study} @ {user_profile.university}"
    elif user_profile.profession == "Professional":
        profession_details = f" {user_profile.designation} @ {user_profile.company}"
    else:
        profession_details = "Profession details not available."

    if request.method == 'POST':
        reason = request.POST.get('reason')
        date = request.POST.get('date')
        duration = request.POST.get('duration')

        start_time = datetime.strptime(date, '%Y-%m-%dT%H:%M')
        end_time = start_time + timedelta(minutes=int(duration))

        Appointment.objects.create(
            requester=request.user,
            recipient=user_profile.user,
            date=start_time,
            end_time=end_time,
            reason=reason,
            status='pending'
        )
        return redirect('home')

    return render(
        request,
        'profile.html',
        {'profile': user_profile, 'profession_details': profession_details, 'received_requests': received_requests}
    )

@login_required
def notifications_view(request):
    received_requests = Appointment.objects.filter(recipient=request.user, status='pending')
    accepted_appointments = Appointment.objects.filter(
        (Q(recipient=request.user) | Q(requester=request.user)) & Q(status='accepted')
    )
    cancelled_appointments = Appointment.objects.filter(
        (Q(recipient=request.user) | Q(requester=request.user)) & Q(status='rejected')
    )
    completed_appointments = Appointment.objects.filter(
        (Q(recipient=request.user) | Q(requester=request.user)) & Q(date__lt=timezone.now()) & Q(status='accepted')
    )
    notifications = Notification.objects.filter(user=request.user)
    
    context = {
        'received_requests': received_requests,
        'accepted_appointments': accepted_appointments,
        'cancelled_appointments': cancelled_appointments,
        'completed_appointments': completed_appointments,
        'notifications': notifications,
        'user': request.user,
    }
    return render(request, 'notifications.html', context)

@login_required
def handle_request(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id)
    action = request.POST.get('action')

    if action == 'accept':
        appointment.status = 'accepted'
        appointment.save()
        # Notify both users
        Notification.objects.create(user=appointment.requester, message=f"Hi {appointment.requester.username}, You have an Appointment with {appointment.recipient.username} on {appointment.date} for {appointment.reason}")
        Notification.objects.create(user=appointment.recipient, message=f"Hi {appointment.recipient.username}, You have an Appointment with {appointment.requester.username} on {appointment.date} for {appointment.reason}")
    elif action == 'cancel':
        appointment.status = 'rejected'
        appointment.save()
        # Notify both users
        Notification.objects.create(user=appointment.requester, message=f"Hi {appointment.requester.username}, your Appointment with {appointment.recipient.username} has been cancelled")
        Notification.objects.create(user=appointment.recipient, message=f"Hi {appointment.recipient.username}, You cancelled the Appointment with {appointment.requester.username}")
    elif action == 'modify':
        # Redirect to a modification form
        return redirect('modify_appointment', appointment_id=appointment.id)

    return redirect('notifications')

@login_required
def modify_appointment(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id)

    if request.method == 'POST':
        new_date = request.POST.get('date')
        new_reason = request.POST.get('reason')
        duration = request.POST.get('duration')

        new_start_time = datetime.datetime.strptime(new_date, '%Y-%m-%dT%H:%M')
        new_end_time = new_start_time + datetime.timedelta(minutes=int(duration))

        appointment.date = new_start_time
        appointment.end_time = new_end_time
        appointment.reason = new_reason
        appointment.status = 'modified'
        appointment.save()

        # Notify the requester
        Notification.objects.create(user=appointment.requester, message=f"Your Appointment is Modified by {appointment.recipient.username} to {new_start_time} for {new_reason}.")
        return redirect('notifications')

    return render(request, 'modify_appointment.html', {'appointment': appointment})

@login_required
def calendar_view(request):
    # Get accepted, cancelled, and pending appointments
    appointments = Appointment.objects.filter(
        Q(recipient=request.user) | Q(requester=request.user),
        status__in=['accepted', 'rejected', 'pending']
    )

    # Add color logic
    for appointment in appointments:
        if appointment.status == 'rejected':
            appointment.color = 'red'
        elif appointment.status == 'pending':
            appointment.color = 'orange'
        else:
            appointment.color = 'blue'

    return render(request, 'view_calendar.html', {'appointments': appointments})

@login_required
def delete_event(request, event_id):
    if request.method == 'POST':
        appointment = Appointment.objects.get(id=event_id)
        appointment.delete()
        return redirect('calendar')

  # Redirect to the login page after logout

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

@login_required
def edit_profile_view(request):
    user_profile = get_object_or_404(UserProfile, user=request.user)
    
    fields = [
        'name', 'profession', 'address', 'city', 'state', 'district',
        'pincode', 'designation', 'company', 'university', 
        'field_of_study', 'description', 'phone_number', 
        'email', 'date_of_birth', 'sex'
    ]

    if request.method == 'POST':
        user_profile.name = request.POST.get('name')
        user_profile.profession = request.POST.get('profession')
        user_profile.address = request.POST.get('address')
        user_profile.city = request.POST.get('city')
        user_profile.state = request.POST.get('state')
        user_profile.district = request.POST.get('district')
        user_profile.pincode = request.POST.get('pincode')
        user_profile.designation = request.POST.get('designation', '')
        user_profile.company = request.POST.get('company', '')
        user_profile.university = request.POST.get('university', '')
        user_profile.field_of_study = request.POST.get('field_of_study', '')
        user_profile.description = request.POST.get('description', '')
        user_profile.phone_number = request.POST.get('phone_number')
        user_profile.email = request.POST.get('email')
        user_profile.sex = request.POST.get('sex')
        user_profile.photo = request.FILES.get('photo', user_profile.photo)

        # Convert date_of_birth string to a date object
        date_of_birth_str = request.POST.get('date_of_birth')
        try:
            user_profile.date_of_birth = datetime.strptime(date_of_birth_str, '%Y-%m-%d').date()
        except ValueError:
            return render(request, 'edit_profile.html', {
                'error': "Invalid Date of Birth format", 
                'user_profile': user_profile, 
                'fields': fields
            })

        user_profile.save()
        return redirect('home')

    return render(request, 'edit_profile.html', {'user_profile': user_profile, 'fields': fields})

def about_us(request):
    return render(request, 'about_us.html')

def forgot_password(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        try:
            # Check if the email exists in the UserProfile model
            user_profile = get_object_or_404(UserProfile, email=email)
            user = user_profile.user  # Get the associated User object

            # Generate password reset token and link
            token = token_generator.make_token(user)
            uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
            reset_link = request.build_absolute_uri(f"/reset-password/{uidb64}/{token}/")
            
            # Send email
            send_mail(
                subject="Reset Your Password",
                message=f"Click the link below to reset your password:\n\n{reset_link}",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[email],
            )
            messages.success(request, "Password reset link has been sent to your email.")
            return redirect('login')
        except UserProfile.DoesNotExist:
            return render(request, 'forgot_password.html', {'error': "Email not found in our system."})
    
    return render(request, 'forgot_password.html')

def reset_password(request, uidb64, token):
    try:
        # Decode UID and get the user
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User.objects.get(pk=uid)
    except (User.DoesNotExist, ValueError, TypeError):
        messages.error(request, "Invalid or expired reset link.")
        return redirect('login')

    # Validate token
    token_generator = PasswordResetTokenGenerator()
    if not token_generator.check_token(user, token):
        messages.error(request, "Invalid or expired reset link.")
        return redirect('login')

    # Handle POST request to update password
    if request.method == 'POST':
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')
        if new_password != confirm_password:
            messages.error(request, "Passwords do not match.")
        else:
            user.set_password(new_password)
            user.save()
            messages.success(request, "Password reset successfully.")
            return redirect('login')

    # Render reset password form
    return render(request, 'reset_password.html', {'uidb64': uidb64, 'token': token})




