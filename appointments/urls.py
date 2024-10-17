from django.urls import path
from . import views
from .views import login_view, register_view, home_view, profile_view, calendar_view

urlpatterns = [
    path('login/', login_view, name='login'),
    path('register/', register_view, name='register'),
    path('', home_view, name='home'),
    path('profile/<int:user_id>/', profile_view, name='profile'),
    path('calendar/', calendar_view, name='calendar'),
    path('notifications/', views.notifications, name='notifications'),
    path('logout/', views.logout_view, name='logout'),


    path('handle_appointment_status/', views.handle_appointment_status, name='handle_appointment_status'),
]
