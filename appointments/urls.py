from django.urls import path
from . import views
from .views import edit_profile_view

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('', views.home_view, name='home'),
    path('profile/<int:user_id>/', views.profile_view, name='profile'),
    path('calendar/', views.calendar_view, name='calendar'),
    path('logout/', views.logout_view, name='logout'),
    path('edit-profile/', edit_profile_view, name='edit_profile'),
    path('about-us/', views.about_us, name='about_us'),


    path('handle_appointment_status/', views.handle_appointment_status, name='handle_appointment_status'),



    path('check-username/', views.check_username, name='check_username'),
    path('check-email/', views.check_email, name='check_email'),


    #path('forgot-password/', views.forgot_password_view, name='forgot_password_view'),
    
    path('forgot-password/', views.forgot_password, name='forgot_password'),
    path('reset-password/<uidb64>/<token>/', views.reset_password, name='reset_password'),


    ############Edit page password change

    path('change-password/', views.change_password, name='change_password'),


    # path('send-otp/', views.send_otp, name='send_otp'),
    # path('verify-otp/', views.verify_otp, name='verify_otp'),
    # path('change-password/', views.change_password, name='change_password'),
    # path('resend-otp/', views.resend_otp, name='resend_otp'),



    path('delete_event/<int:event_id>/', views.delete_event, name='delete_event'),



    # path('notifications/', views.Notification, name='notifications'),
    # path('appointment/<int:appointment_id>/accept/', views.accept_appointment, name='accept_appointment'),
    path('users/', views.user_list, name='user_list'),
    # path('appointment/<int:appointment_id>/reject/', views.reject_appointment, name='reject_appointment'),
    # path('appointment/<int:appointment_id>/modify/', views.modify_appointment, name='modify_appointment'),
    


    path('profile/<int:user_id>/', views.profile_view, name='profile'),
    path('notifications/', views.notifications_view, name='notifications'),
    path('handle_request/<int:appointment_id>/', views.handle_request, name='handle_request'),
    path('modify_appointment/<int:appointment_id>/', views.modify_appointment, name='modify_appointment'),
]
