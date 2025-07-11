from django.contrib import admin
from .models import *

# Register your models here.


admin.site.register(UserProfile)
admin.site.register(Patient)
admin.site.register(Doctor)
admin.site.register(MedicalRecord)
admin.site.register(Billing)


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ['patient', 'doctor', 'date', 'time', 'status']
