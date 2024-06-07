from .models import PatientProfile, DoctorProfile, PharmacistProfile

def profile_context_processor(request):
    profile = None
    if request.user.is_authenticated:
        if request.user.role == 'PATIENT':
            profile = PatientProfile.objects.get(user=request.user)
        elif request.user.role == 'DOCTOR':
            profile = DoctorProfile.objects.get(user=request.user)
        elif request.user.role == 'PHARMACIST':
            profile = PharmacistProfile.objects.get(user=request.user)

    return {'profile': profile}