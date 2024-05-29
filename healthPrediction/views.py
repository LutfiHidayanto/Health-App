from django.shortcuts import render, redirect, get_object_or_404
from .forms import diabetesPredictionForm, LoginForm, PatientRegistrationForm, DoctorRegistrationForm, PatientProfileForm, DoctorProfileForm, PharmacistRegistrationForm, PharmacistProfileForm, MedicineForm
from .preprocessing import loadModel, scaleData, predict, convertFormData
from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.db import IntegrityError
from .models import User, Patient, Doctor, Pharmacist, PatientProfile, DoctorProfile, PharmacistProfile, ConsultationRequest, Medicine, Order, OrderItem, PurchaseRequest
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.db import transaction
from .utils import create_google_meet_link 


PATIENT_DIR = 'healthPrediction/'
DOCTOR_DIR = 'doctor/'
PHARMACIST_DIR = 'pharmacist/'
# Create your views here.

features = ['Diabetes_binary', 'HighBP', 'HighChol', 'CholCheck', 'Smoker',
       'Stroke', 'HeartDiseaseorAttack', 'PhysActivity', 'Fruits', 'Veggies',
       'HvyAlcoholConsump', 'AnyHealthcare', 'NoDocbcCost', 'DiffWalk', 'Sex',
       'BMI', 'GenHlth', 'MentHlth', 'PhysHlth', 'Age']

categorical_features= ['Diabetes_binary', 'HighBP', 'HighChol', 'CholCheck', 'Smoker', 'Stroke', 'HeartDiseaseorAttack', 'PhysActivity', 'Fruits', 'Veggies', 'HvyAlcoholConsump', 'AnyHealthcare', 'NoDocbcCost', 'DiffWalk', 'Sex']

def index(request):
    return render(request, 'healthPrediction/index.html')

def diabetes_view(request):
    result = ""
    if request.method == 'POST':
        form = diabetesPredictionForm(request.POST)
        if form.is_valid():
            cleaned_data = form.cleaned_data
            data = cleaned_data.items()

            data = convertFormData(data)
            print(data.head())

            data = scaleData(data)

            if data is None:
                return HttpResponse("Scaling data error")
            model = loadModel('healthPrediction/static/healthPrediction/models/xgboost_diabetes.pickle')
            if model is None:
                return HttpResponse("Loading model error")
            prediction = predict(data, model)
            if prediction == None:
                return Http404("Prediction Error")
            
            print(prediction)
            result = prediction[0]
            print(type(result))
    else:
        form = diabetesPredictionForm()
    return render(request, 'healthPrediction/diabetes.html', {
        'form': form,
        'result': result
    })

""" PATIENT """

def patient_login_view(request):
    if request.method == "POST":
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                if user.role == "PATIENT":
                    login(request, user)
                    return HttpResponseRedirect(reverse("index"))
                else:
                    messages.error(request, "You are not authorized to access this page.")
            else:
                messages.error(request, "Invalid username or password.")
        else:
            messages.error(request, "Invalid username or password.")
    else:
        form = LoginForm()
    return render(request, PATIENT_DIR + "login.html", {"form": form})

def patient_register_view(request):
    if request.method == "POST":
        form = PatientRegistrationForm(request.POST)
        profile_form = PatientProfileForm(request.POST, request.FILES)
        if form.is_valid() and profile_form.is_valid():
            # Regist
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password1')
            email = form.cleaned_data.get('email')
            first_name = form.cleaned_data.get('first_name')
            last_name = form.cleaned_data.get('last_name')

            print(username, password, email, first_name, last_name)
        

            try:
                user = Patient.objects.create_user(username=username, password=password, first_name=first_name, last_name=last_name, email=email)
                user.save()
            except IntegrityError:
                return render(request, "healthPrediction/register.html", {
                    "message": "Username already taken."
                })
            
            user = Patient.objects.get(username=username)
            print(user)

            date_of_birth = profile_form.cleaned_data.get('date_of_birth')
            address = profile_form.cleaned_data.get('address')
            phone_number = profile_form.cleaned_data.get('phone_number')
            profile_photo = profile_form.cleaned_data.get('profile_photo')

            print(date_of_birth, address, phone_number, profile_photo)
            profile = PatientProfile(
                user=user,
                date_of_birth=date_of_birth,
                address=address,
                phone_number=phone_number,
                profile_photo=profile_photo
            )
            profile.save()
            
            
            return HttpResponseRedirect(reverse("login"))
        else:
            messages.error(request, "Unsuccessful registration. Invalid information.")
    else:
        form = PatientRegistrationForm()
        profile_form = PatientProfileForm()
        
    context = {
        "form": form,
        "profile_form": profile_form
    }
    return render(request, PATIENT_DIR +  "register.html", context)

# Consultations
@login_required
def consultations(request):
    doctors = DoctorProfile.objects.all()
    latest_request = ConsultationRequest.objects.filter(patient=request.user).order_by('-requested_at').first()

    latest_request_doctor_profile = None
    if latest_request:
        latest_request_doctor_profile = get_object_or_404(DoctorProfile, user=latest_request.doctor)

    print(latest_request_doctor_profile)


    context = {
        'doctors': doctors,
        'latest_request': latest_request,
        'doctor_request': latest_request_doctor_profile
    }
    return render(request, PATIENT_DIR + 'consultations.html', context)

@login_required
def consult_doctor(request, doctor_id):
    doctor = get_object_or_404(DoctorProfile, doctor_id=doctor_id)
    return render(request, PATIENT_DIR + 'consult_doctor.html', {'doctor': doctor})

@login_required
def request_consultation(request, doctor_id):
    message = ""
    doctor = get_object_or_404(DoctorProfile, doctor_id=doctor_id)
    doctors = DoctorProfile.objects.all()
    latest_request = ConsultationRequest.objects.filter(patient=request.user).order_by('-requested_at').first()
    if latest_request.status != 'completed':
        messages.warning(request, "Please wait before sending another consultation request!")
        return HttpResponseRedirect(reverse('consultations'))

    ConsultationRequest.objects.create(patient=request.user, doctor=doctor.user)
    messages.success(request, "Consultation request sent.")
    return HttpResponseRedirect(reverse('consultations'))

def consultation_room(request, request_id):
    consultation_request = get_object_or_404(ConsultationRequest, id=request_id)
    doctor = consultation_request.doctor
    context = {
        'doctor': doctor,
    }
    return render(request, PATIENT_DIR + 'consultation_room.html', context)

# Meds Store
@login_required
def medicine_list(request):
    medicines = Medicine.objects.all()
    return render(request, PATIENT_DIR + 'store.html', {'medicines': medicines})

@login_required
def medicine_detail(request, medicine_id):
    medicine = get_object_or_404(Medicine, id=medicine_id)
    return render(request, PATIENT_DIR + 'medicine_detail.html', {'medicine': medicine})

@login_required
def add_to_cart(request, medicine_id):
    medicine = get_object_or_404(Medicine, id=medicine_id)
    order, created = Order.objects.get_or_create(user=request.user, status='pending')
    
    quantity = int(request.GET.get('quantity', 1))
    
    order_item, created = OrderItem.objects.get_or_create(order=order, medicine=medicine)
    order_item.quantity += quantity
    order_item.save()
    
    return HttpResponseRedirect(reverse('medicine_detail', args=[medicine_id]))

@login_required
def user_cart(request):
    cart = Order.objects.filter(user=request.user, status='pending').first()
    if cart is not None:
        cart_items = cart.items.all() 
        total_quantity = cart.total_quantity
        total_price = cart.total_price
        total_each_item = [item.total_price for item in cart_items]
    else:
        cart_items = []
        total_quantity = 0
        total_price = 0
        total_each_item = []

    context = {
        'cart_items': cart_items,
        'total_price': total_price,
        'total_quantity': total_quantity,
        'total_each_item': total_each_item
    }
    # return render(request, 'user_cart.html', context)

    return render(request, PATIENT_DIR + 'user_cart.html',context)

@login_required
def checkout(request):
    order = Order.objects.filter(user=request.user, status='pending').first()
    if request.method == 'POST' and order:
        try:
            with transaction.atomic():
                # Update the stock for each medicine in the order
                for item in order.items.all():
                    if item.medicine.stock >= item.quantity:
                        item.medicine.stock -= item.quantity
                        item.medicine.save()
                    else:
                        # Handle insufficient stock (optional)
                        return HttpResponse("Insufficient stock for some items.", status=400)

                # Mark the order as completed
                order.status = 'completed'
                order.save()

                # Create purchase requests for each pharmacist
                pharmacists = set(item.medicine.pharmacist for item in order.items.all())
                for pharmacist in pharmacists:
                    PurchaseRequest.objects.create(order=order, pharmacist=pharmacist)
                
                return redirect('order_confirmation')
        except Exception as e:
            return HttpResponse(f"An error occurred: {str(e)}", status=500)
    
    context = {
        'order': order,
        'total_quantity': order.total_quantity if order else 0,
        'total_price': order.total_price if order else 0
    }
    return render(request, PATIENT_DIR + 'checkout.html', context)


@login_required
def order_confirmation(request):
    return render(request, PATIENT_DIR + 'order_confirmation.html')


""" DOCTOR """

def doctor_login_view(request):
    if request.method == "POST":
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                if user.role == "DOCTOR":
                    login(request, user)
                    return HttpResponseRedirect(reverse("doctor_index"))
                else:
                    messages.error(request, "You are not authorized to access this page.")
            else:
                messages.error(request, "Invalid username or password.")
        else:
            messages.error(request, "Invalid username or password.")
    else:
        form = LoginForm()
    return render(request, DOCTOR_DIR + "login.html", {"form": form})


def doctor_register_view(request):
    if request.method == "POST":
        form = DoctorRegistrationForm(request.POST)
        profile_form = DoctorProfileForm(request.POST, request.FILES)
        if form.is_valid() and profile_form.is_valid():
            # User
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password1')
            email = form.cleaned_data.get('email')
            first_name = form.cleaned_data.get('first_name')
            last_name = form.cleaned_data.get('last_name')

            print(username, password, email, first_name, last_name)
            # Save user
            try:
                user = Doctor.objects.create_user(username=username, password=password, first_name=first_name, last_name=last_name, email=email)
                user.save()
            except IntegrityError:
                return render(request, "healthPrediction/register.html", {
                    "message": "Username already taken."
                })
            
            # Profile
            user = Doctor.objects.get(username=username)
            print(user)

            specialty = profile_form.cleaned_data.get('specialty')
            is_available = profile_form.cleaned_data.get('is_available')
            years_of_experience = profile_form.cleaned_data.get('years_of_experience')
            phone_number = profile_form.cleaned_data.get('phone_number')
            profile_photo = profile_form.cleaned_data.get('profile_photo')

            # save profile
            print(specialty, is_available, years_of_experience, phone_number, profile_photo)
            profile = DoctorProfile(
                user=user,
                specialty=specialty,
                years_of_experience=years_of_experience,
                phone_number=phone_number,
                profile_photo=profile_photo
            )
            profile.save()
            
            
            return HttpResponseRedirect(reverse("doctor_login"))
        else:
            messages.error(request, "Unsuccessful registration. Invalid information.")
    else:
        form = DoctorRegistrationForm()
        profile_form = DoctorProfileForm()
        
    context = {
        "form": form,
        "profile_form": profile_form
    }
    return render(request, DOCTOR_DIR +  "register.html", context)

def doctor_index(request):
    return render(request, DOCTOR_DIR + 'index.html')

def doctor_consultation_room(request, request_id):
    consultation_request = get_object_or_404(ConsultationRequest, id=request_id)
    patient = consultation_request.patient
    context = {
        'patient': patient,
    }
    return render(request, DOCTOR_DIR + 'consultation_room.html', context)

@login_required
def doctor_dashboard(request):
    if request.user.role != User.Role.DOCTOR:
        return HttpResponseRedirect(reverse('index')) 

    requests = ConsultationRequest.objects.filter(doctor=request.user)
    return render(request, DOCTOR_DIR + 'dashboard.html', {'requests': requests})

@login_required
def accept_consultation(request, request_id):
    consultation_request = get_object_or_404(ConsultationRequest, id=request_id, doctor=request.user)
    consultation_request.status = 'accepted'
    consultation_request.accepted_at = timezone.now()

    try:
        doctor_profile = DoctorProfile.objects.get(user=request.user)
        doctor_profile.is_available = False
        doctor_profile.save()
    except Exception:
        error = "doctor could not be found in the database"

    consultation_request.save()
    messages.success(request, "Consultation request accepted.")
    return HttpResponseRedirect(reverse('doctor_index'))

@login_required
def mark_consultation_completed(request, request_id):
    consultation_request = get_object_or_404(ConsultationRequest, id=request_id, doctor=request.user)
    consultation_request.status = 'completed'
    consultation_request.completed_at = timezone.now()
    consultation_request.save()
    
    # Update doctor's availability
    doctor_profile = DoctorProfile.objects.get(user=request.user)
    doctor_profile.is_available = True
    doctor_profile.save()

    messages.success(request, "Consultation marked as completed.")
    return HttpResponseRedirect(reverse('doctor_index'))


@login_required
def reject_consultation(request, request_id):
    consultation_request = get_object_or_404(ConsultationRequest, id=request_id, doctor=request.user)
    consultation_request.status = 'rejected'
    consultation_request.save()
    messages.success(request, "Consultation request rejected.")
    return HttpResponseRedirect(reverse('doctor_index'))



def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "healthPrediction/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "healthPrediction/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "healthPrediction/register.html")


drug_categories = [
    "Antihistamines",
    "Analgesics",
    "Cough Medicines",
    "Antacids",
    "Antipyretics",
    "Antihypertensives",
    "Antiarrhythmics",
    "Anticoagulants and Thrombolytics",
    "Antibiotics",
    "Antifungals",
    "Antivirals",
    "Antidiarrheals",
    "Laxatives",
    "Anticonvulsants",
    "Anxiolytics",
    "Antidepressants",
    "Anti-Inflammatories",
    "Antipsychotics",
    "Corticosteroids",
    "Immunosuppressants",
    "Other Drug Categories"
]

""" PHARMACIST """

def pharmacist_login_view(request):
    if request.method == "POST":
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                if user.role == "PHARMACIST":
                    login(request, user)
                    return HttpResponseRedirect(reverse("pharmacist_index"))
                else:
                    messages.error(request, "You are not authorized to access this page.")
            else:
                messages.error(request, "Invalid username or password.")
        else:
            messages.error(request, "Invalid username or password.")
    else:
        form = LoginForm()
    return render(request, PHARMACIST_DIR + "login.html", {"form": form})


def pharmacist_register_view(request):
    if request.method == "POST":
        form = PharmacistRegistrationForm(request.POST)
        profile_form = PharmacistProfileForm(request.POST)
        if form.is_valid() and profile_form.is_valid():
            # User
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password1')
            email = form.cleaned_data.get('email')
            first_name = form.cleaned_data.get('first_name')
            last_name = form.cleaned_data.get('last_name')

            print(username, password, email, first_name, last_name)
            # Save user
            try:
                user = Pharmacist.objects.create_user(username=username, password=password, first_name=first_name, last_name=last_name, email=email)
                user.save()
            except IntegrityError:
                return render(request, "healthPrediction/register.html", {
                    "message": "Username already taken."
                })
            
            # Profile
            user = Pharmacist.objects.get(username=username)
            print(user)

            pharmacy_name = profile_form.cleaned_data.get('pharmacy_name')
            pharmacy_city = profile_form.cleaned_data.get('pharmacy_city')
            latitude = profile_form.cleaned_data.get('latitude')
            phone_number = profile_form.cleaned_data.get('phone_number')
            longitude = profile_form.cleaned_data.get('longitude')

            # save profile
            print(pharmacy_name, pharmacy_city, latitude, phone_number, longitude)
            profile = PharmacistProfile(
                user=user,
                pharmacy_name=pharmacy_name,
                pharmacy_city=pharmacy_city,
                latitude=latitude,
                phone_number=phone_number,
                longitude=longitude
            )
            profile.save()
            
            
            return HttpResponseRedirect(reverse("pharmacist_login"))
        else:
            messages.error(request, "Unsuccessful registration. Invalid information.")
    else:
        form = PharmacistRegistrationForm()
        profile_form = PharmacistProfileForm()
        
    context = {
        "form": form,
        "profile_form": profile_form
    }
    return render(request, PHARMACIST_DIR +  "register.html", context)


@login_required
def manage_medicines(request):
    medicines = Medicine.objects.filter(pharmacist=request.user)
    print(Medicine)
    return render(request, PHARMACIST_DIR + 'manage_medicines.html', {'medicines': medicines})

@login_required
def add_medicine(request):
    if request.method == 'POST':
        form = MedicineForm(request.POST, request.FILES)
        if form.is_valid():
            medicine = form.save(commit=False)
            medicine.pharmacist = request.user
            medicine.save()
            return redirect('manage_medicines')
    else:
        form = MedicineForm()
    return render(request, PHARMACIST_DIR +  'add_medicine.html', {'form': form})

@login_required
def edit_medicine(request, medicine_id):
    medicine = get_object_or_404(Medicine, id=medicine_id, pharmacist=request.user)
    if request.method == 'POST':
        form = MedicineForm(request.POST, request.FILES, instance=medicine)
        if form.is_valid():
            form.save()
            return redirect('manage_medicines')
    else:
        form = MedicineForm(instance=medicine)
    return render(request, PHARMACIST_DIR +  'edit_medicine.html', {'form': form})

@login_required
def delete_medicine(request, medicine_id):
    medicine = get_object_or_404(Medicine, id=medicine_id, pharmacist=request.user)
    if request.method == 'POST':
        medicine.delete()
        return redirect('manage_medicines')
    return render(request, PHARMACIST_DIR + 'delete_medicine.html', {'medicine': medicine})

@login_required
def pharmacist_dashboard(request):
    purchase_requests = PurchaseRequest.objects.filter(pharmacist=request.user)
    return render(request, PHARMACIST_DIR + 'dashboard.html', {'purchase_requests': purchase_requests})

@login_required
def update_purchase_request_status(request, purchase_request_id, status):
    purchase_request = get_object_or_404(PurchaseRequest, id=purchase_request_id, pharmacist=request.user)
    purchase_request.status = status
    purchase_request.save()
    return redirect('pharmacist_dashboard')


@login_required
def pharmacist_sell_view(request):
    pass

def pharmacist_request_view(request):
    pass

def pharmacist_index(request):
    return render(request, PHARMACIST_DIR + 'index.html')
