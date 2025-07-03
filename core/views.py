from .models import Appointment
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .models import UserProfile, Patient
from django.contrib.auth.models import User


def home(request):
    return render(request, 'home.html')


def signup_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        age = request.POST['age']
        gender = request.POST['gender']
        contact = request.POST['contact']

        # Create user
        user = User.objects.create_user(username=username, password=password)
        # Create UserProfile with patient role
        UserProfile.objects.create(user=user, role='patient')
        # Create Patient profile
        Patient.objects.create(
            user=user, age=age, gender=gender, contact=contact)

        return redirect('login')

    return render(request, 'signup.html')


def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect('dashboard')
        else:
            return render(request, 'login.html', {'error': 'Invalid credentials'})
    return render(request, 'login.html')


@login_required
def dashboard(request):
    role = request.user.userprofile.role

    if role == 'admin':
        return render(request, 'dashboard_admin.html')
    elif role == 'doctor':
        return render(request, 'dashboard_doctor.html')
    elif role == 'receptionist':
        return render(request, 'dashboard_receptionist.html')
    elif role == 'patient':
        return render(request, 'dashboard_patient.html')
    else:
        return redirect('logout')  # Unknown role


def logout_view(request):
    logout(request)
    return redirect('login')


@login_required
def book_appointment(request):
    if request.user.userprofile.role != 'receptionist':
        # ❌ Block users who are not receptionist
        return redirect('dashboard')

    # ✅ Allowed receptionist can continue here
    return render(request, 'book_appointment.html')


@login_required
def doctor_dashboard(request):
    if request.user.userprofile.role != 'doctor':
        return redirect('dashboard')  # block other users

    # doctor’s content
    return render(request, 'dashboard_doctor.html')


@login_required
def patient_appointments(request):
    if request.user.userprofile.role != 'patient':
        return redirect('dashboard')  # block other roles

    # Only show appointments of this patient
    patient = request.user.patient
    appointments = Appointment.objects.filter(patient=patient)

    return render(request, 'patient_appointments.html', {'appointments': appointments})

# view appointment


@login_required
def view_appointments(request):
    if request.user.userprofile.role != 'doctor':
        return redirect('dashboard')

    doctor = request.user.doctor
    appointments = Appointment.objects.filter(doctor=doctor)
    return render(request, 'doctor_appointments.html', {'appointments': appointments})
