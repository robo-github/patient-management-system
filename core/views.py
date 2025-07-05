from .models import Appointment, MedicalRecord, Doctor
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .models import UserProfile, Patient
from django.contrib.auth.models import User
from django.utils import timezone


def home(request):
    return render(request, 'home.html')


def signup_view(request):
    if request.method == 'POST':
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        username = request.POST['username']
        password = request.POST['password']
        age = request.POST['age']
        gender = request.POST['gender']
        contact = request.POST['contact']

        user = User.objects.create_user(
            username=username,
            password=password,
            first_name=first_name,
            last_name=last_name
        )

        # Set the role as 'patient' by default
        UserProfile.objects.create(user=user, role='patient')

        #  Create entry in Patient table
        Patient.objects.create(
            user=user,
            age=age,
            gender=gender,
            contact=contact
        )

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
        return redirect('dashboard')

    if request.method == 'POST':
        patient_id = request.POST.get('patient')
        doctor_id = request.POST.get('doctor')
        date = request.POST.get('date')
        time = request.POST.get('time')

        patient = Patient.objects.get(id=patient_id)
        doctor = Doctor.objects.get(id=doctor_id)

        Appointment.objects.create(
            patient=patient,
            doctor=doctor,
            date=date,
            time=time,
            status='Scheduled'
        )

        return redirect('dashboard')  # or a success page

    patients = Patient.objects.all()
    doctors = Doctor.objects.all()

    return render(request, 'book_appointment.html', {
        'patients': patients,
        'doctors': doctors
    })


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

# Add medical report


@login_required
def add_medical_record(request, appointment_id):
    if request.user.userprofile.role != 'doctor':
        return redirect('dashboard')

    appointment = get_object_or_404(Appointment, id=appointment_id)

    if request.method == 'POST':
        diagnosis = request.POST.get('diagnosis')
        prescription = request.POST.get('prescription')

        MedicalRecord.objects.create(
            appointment=appointment,
            diagnosis=diagnosis,
            prescription=prescription
        )
        return redirect('view_appointments')  # or doctor dashboard

    return render(request, 'add_medical_record.html', {'appointment': appointment})
