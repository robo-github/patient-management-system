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
    path('patient/records/', views.view_medical_records,
         name='view_medical_records'),
    path('record/<int:record_id>/export/', views.export_pdf, name='export_pdf'),
    path('billing/add/', views.add_billing, name='add_billing'),
    path('billing/view/', views.view_bills, name='view_bills'),
    path('bill/<int:bill_id>/export/',
         views.export_bill_pdf, name='export_bill_pdf'),
    path('patient/bills/', views.patient_view_bills, name='patient_view_bills'),
    path('patient/payment-history/', views.patient_payment_history,
         name='patient_payment_history'),



]
