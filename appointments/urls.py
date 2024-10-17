from django.urls import path
from . import views
from .views import login_view, register_view, home_view, profile_view, calendar_view

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('', views.home_view, name='home'),
    path('profile/<int:user_id>/', views.profile_view, name='profile'),
    path('calendar/', views.calendar_view, name='calendar'),
    path('notifications/', views.notifications, name='notifications'),
    path('logout/', views.logout_view, name='logout'),


    path('handle_appointment_status/', views.handle_appointment_status, name='handle_appointment_status'),



    path('check-username/', views.check_username, name='check_username'),

    path('forgot-password/', views.forgot_password_view, name='forgot_password_view'),
    
]
