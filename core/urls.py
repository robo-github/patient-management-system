from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('book/', views.book_appointment, name='book_appointment'),
    path('doctor/dashboard/', views.doctor_dashboard, name='doctor_dashboard'),
    path('patient/appointments/', views.patient_appointments,
         name='patient_appointments'),
    path('signup/', views.signup_view, name='signup'),
    path('doctor/appointments/', views.view_appointments, name='view_appointments'),
    path('doctor/appointment/<int:appointment_id>/record/',
         views.add_medical_record, name='add_medical_record'),
]
