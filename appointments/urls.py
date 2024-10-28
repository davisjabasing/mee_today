from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('', views.home_view, name='home'),
    path('profile/<int:user_id>/', views.profile_view, name='profile'),
    path('calendar/', views.calendar_view, name='calendar'),
    path('logout/', views.logout_view, name='logout'),
    path('Edit_Profile/', views.edit_profile, name='edit_profile'),


    path('handle_appointment_status/', views.handle_appointment_status, name='handle_appointment_status'),



    path('check-username/', views.check_username, name='check_username'),

    path('forgot-password/', views.forgot_password_view, name='forgot_password_view'),


    ############Edit page password change

    path('change-password/', views.change_password, name='change_password'),



    # path('notifications/', views.Notification, name='notifications'),
    # path('appointment/<int:appointment_id>/accept/', views.accept_appointment, name='accept_appointment'),
    # path('appointment/<int:appointment_id>/reject/', views.reject_appointment, name='reject_appointment'),
    # path('appointment/<int:appointment_id>/modify/', views.modify_appointment, name='modify_appointment'),
    


    path('profile/<int:user_id>/', views.profile_view, name='profile'),
    path('notifications/', views.notifications_view, name='notifications'),
    path('handle_request/<int:appointment_id>/', views.handle_request, name='handle_request'),
    path('modify_appointment/<int:appointment_id>/', views.modify_appointment, name='modify_appointment'),
]
