from django.http import HttpResponse
from .models import Appointment, MedicalRecord, Doctor, UserProfile, Patient, Billing
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.template.loader import get_template
from xhtml2pdf import pisa
from django.db.models import Sum


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

# All role wise dashboard


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
        patient = request.user.patient

        # Get counts
        appointments_count = Appointment.objects.filter(
            patient=patient, status='Scheduled').count()
        records_count = MedicalRecord.objects.filter(
            appointment__patient=patient).count()
        bills_total = Billing.objects.filter(patient=patient).aggregate(Sum('amount'))[
            'amount__sum'] or 0

        return render(request, 'dashboard_patient.html', {
            'appointments_count': appointments_count,
            'records_count': records_count,
            'bills_total': bills_total
        })
    else:
        return redirect('logout')  # Unknown role

# Login view (  )


def logout_view(request):
    logout(request)
    return redirect('login')

# Book appointment (Receptionist side)


@login_required
def book_appointment(request):
    if request.user.userprofile.role != 'receptionist':
        return redirect('dashboard')

    if request.method == 'POST':
        patient_id = request.POST['patient']
        doctor_id = request.POST['doctor']
        date = request.POST['date']
        time = request.POST['time']

        # Save appointment
        Appointment.objects.create(
            patient=Patient.objects.get(id=patient_id),
            doctor=Doctor.objects.get(id=doctor_id),
            date=date,
            time=time,
            status='Scheduled'
        )

        messages.success(request, 'Appointment booked successfully.')
        return redirect('book_appointment')

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

# view appointment (Patient side)


@login_required
def patient_appointments(request):
    if request.user.userprofile.role != 'patient':
        return redirect('dashboard')  # block other roles

    # Only show appointments of this patient
    patient = request.user.patient
    appointments = Appointment.objects.filter(
        patient=patient).order_by('date', 'time')

    return render(request, 'patient_appointments.html', {'appointments': appointments})

# view appointment (Doctor side )


@login_required
def view_appointments(request):
    if request.user.userprofile.role != 'doctor':
        return redirect('dashboard')

    try:
        doctor = request.user.doctor
    except:
        return HttpResponse("Doctor profile not found. Contact admin.")
    appointments = Appointment.objects.filter(
        doctor=doctor).order_by('date', 'time')
    return render(request, 'doctor_appointments.html', {'appointments': appointments})

# Add medical report (Doctor side )


@login_required
def add_medical_record(request, appointment_id):
    if request.user.userprofile.role != 'doctor':
        return redirect('dashboard')

    appointment = get_object_or_404(Appointment, id=appointment_id)

    if request.method == 'POST':
        diagnosis = request.POST.get('diagnosis')
        prescription = request.POST.get('prescription')

        record = MedicalRecord.objects.create(
            appointment=appointment,
            diagnosis=diagnosis,
            prescription=prescription
        )
        print("Record ID:", record.id)
        appointment.status = 'Completed'
        appointment.save()

        messages.success(request, "Medical record added successfully.")
        return redirect('view_appointments')

    return render(request, 'add_medical_record.html', {'appointment': appointment})


# view medical records (Patient side)


@login_required
def view_medical_records(request):
    if request.user.userprofile.role != 'patient':
        return redirect('dashboard')

    patient = request.user.patient
    records = MedicalRecord.objects.filter(appointment__patient=patient)

    return render(request, 'patient_medical_records.html', {'records': records})

# pdf generate


@login_required
def export_pdf(request, record_id):
    record = MedicalRecord.objects.get(id=record_id)
    template_path = 'export_pdf.html'
    context = {'record': record}
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="medical_record.pdf"'
    template = get_template(template_path)
    html = template.render(context)
    pisa.CreatePDF(html, dest=response)
    return response

# Add Billing (receptionist side)


@login_required
def add_billing(request):
    if request.user.userprofile.role != 'receptionist':
        return redirect('dashboard')

    patients = Patient.objects.all()

    if request.method == 'POST':
        patient_id = request.POST.get('patient')
        service = request.POST.get('service')
        amount = request.POST.get('amount')

        patient = Patient.objects.get(id=patient_id)

        Billing.objects.create(
            patient=patient,
            service=service,
            amount=amount
        )

        messages.success(request, "Billing record added.")
        return redirect('add_billing')

    return render(request, 'add_billing.html', {'patients': patients})

# View Billing (receptionist side)


@login_required
def view_bills(request):
    if request.user.userprofile.role not in ['receptionist', 'admin']:
        return redirect('dashboard')

    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    bills = Billing.objects.all().order_by('-date')

    if start_date and end_date:
        bills = bills.filter(date__range=[start_date, end_date])

    total_amount = bills.aggregate(Sum('amount'))['amount__sum'] or 0

    return render(request, 'view_bills.html', {
        'bills': bills,
        'total_amount': total_amount,
        'start_date': start_date,
        'end_date': end_date
    })
# Export bill pdf


@login_required
def export_bill_pdf(request, bill_id):
    bill = Billing.objects.get(id=bill_id)
    template_path = 'export_bill_pdf.html'
    context = {'bill': bill}
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="bill.pdf"'
    template = get_template(template_path)
    html = template.render(context)
    pisa.CreatePDF(html, dest=response)
    return response

# patient bill view (patient side)


@login_required
def patient_view_bills(request):
    if request.user.userprofile.role != 'patient':
        return redirect('dashboard')

    bills = Billing.objects.filter(
        patient=request.user.patient).order_by('-date')
    return render(request, 'patient_view_bills.html', {'bills': bills})

# patient payment history


@login_required
def patient_payment_history(request):
    if request.user.userprofile.role != 'patient':
        return redirect('dashboard')

    bills = Billing.objects.filter(
        patient=request.user.patient).order_by('-date')

    return render(request, 'patient_payment_history.html', {'bills': bills})
