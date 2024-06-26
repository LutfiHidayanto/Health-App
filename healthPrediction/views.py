from django.shortcuts import render, redirect, get_object_or_404
from .forms import diabetesPredictionForm, LoginForm, PatientRegistrationForm, DoctorRegistrationForm, PatientProfileForm, DoctorProfileForm, PharmacistRegistrationForm, PharmacistProfileForm, MedicineForm, MedicalHistoryForm, PatientUpdateForm, DoctorUpdateForm, PharmacistUpdateForm, PasswordChangeForm, DoctorProfileUpdateForm
from .preprocessing import loadModel, scaleData, predict, convertFormData
from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.db import IntegrityError
from .models import User, Patient, Doctor, Pharmacist, PatientProfile, DoctorProfile, PharmacistProfile, ConsultationRequest, Medicine, Order, OrderItem, PurchaseRequest, MedicalHistory
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib import messages
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.db import transaction



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
    if request.user.is_authenticated and not request.user.role == 'PATIENT':
        usertype = "Patient"
        return render(request, PATIENT_DIR + 'error.html', {'usertype': usertype})
    return render(request, 'healthPrediction/index.html')

def landing(request):
    return render(request, 'healthPrediction/landing.html')

def profile_view(request):
    if not request.user.is_authenticated:
        page_name = "Profile"
        message = f"You have to login to access {page_name}"
        messages.add_message(request, messages.ERROR, message)
        return HttpResponseRedirect(reverse('login'))
    user = request.user
    profile = None
    roles = User.Role
    print(roles.ADMIN)
    
    if user.role == 'PATIENT':
        profile = PatientProfile.objects.get(user=user)       
        return render(request, PATIENT_DIR + 'profile.html', {'profile': profile})
    elif user.role == 'DOCTOR':
        profile = get_object_or_404(DoctorProfile, user=user)
        return render(request, DOCTOR_DIR + 'profile.html', {'profile': profile})
    elif user.role == 'PHARMACIST':
        profile = get_object_or_404(PharmacistProfile, user=user)
        return render(request, PHARMACIST_DIR + 'profile.html', {'profile': profile})
    
def medical_history_view(request):
    if not request.user.is_authenticated:
        page_name = "Medical History"
        message = f"You have to login to access {page_name}"
        messages.add_message(request, messages.ERROR, message)
        return HttpResponseRedirect(reverse('login'))
    user = request.user    
    patient_profile = get_object_or_404(PatientProfile, user=user)
    medical_history = MedicalHistory.objects.filter(patient=patient_profile)
    form = MedicalHistoryForm()

    if request.method == 'POST':
        form = MedicalHistoryForm(request.POST)
        if form.is_valid():
            medical_history_instance = form.save(commit=False)
            medical_history_instance.patient = patient_profile
            medical_history_instance.save()
            return redirect('medical_history')  # Redirect to the same view after saving
    
    return render(request, PATIENT_DIR + 'medical_history.html', {'form': form, 'medical_history': medical_history})


def edit_profile_view(request):
    if not request.user.is_authenticated:
        page_name = "Edit Profile"
        message = f"You have to login to access {page_name}"
        messages.add_message(request, messages.ERROR, message)
        return HttpResponseRedirect(reverse('login'))
    user = request.user
    if user.role == 'PATIENT':        
        profile = PatientProfile.objects.get(user=user)
        form_class = PatientProfileForm
        user_form_class = PatientUpdateForm
        dir = PATIENT_DIR
    elif user.role == 'DOCTOR':
        profile = get_object_or_404(DoctorProfile, user=user)
        form_class = DoctorProfileUpdateForm
        user_form_class = DoctorUpdateForm
        dir = DOCTOR_DIR
    elif user.role == 'PHARMACIST':
        profile = get_object_or_404(PharmacistProfile, user=user)
        form_class = PharmacistProfileForm
        user_form_class = PharmacistUpdateForm
        dir = PHARMACIST_DIR
    else:
        profile = None
        form_class = None
        user_form_class = None

    if request.method == 'POST':
        form = form_class(request.POST, request.FILES, instance=profile)
        user_form = user_form_class(request.POST, instance=user)

        if form.is_valid():
            form.save()
        if user_form.is_valid():
            print("bruh")
            username = user_form.cleaned_data.get('username')
            email = user_form.cleaned_data.get('email')
            first_name = user_form.cleaned_data.get('first_name')
            last_name = user_form.cleaned_data.get('last_name')

            print(username, email, first_name, last_name)
            User.objects.filter(pk=request.user.id).update(
                username=username, 
                email=email, 
                first_name=first_name,
                last_name=last_name    
            )
            
        messages.success(request, 'Your profile has been updated successfully!')
        return redirect('profile')


    else:
        form = form_class(instance=profile)
        user_form = user_form_class(instance=request.user)

    return render(request, dir + 'edit_profile.html', {'form': form, 'user_form': user_form})

def change_password_view(request):
    if not request.user.is_authenticated:
        page_name = "Change Password"
        message = f"You have to login to access {page_name}"
        messages.add_message(request, messages.ERROR, message)
        return HttpResponseRedirect(reverse('login'))

    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            newpassword = form.cleaned_data.get('new_password1')
            print(newpassword)
            user = User.objects.get(pk=request.user.id)
            print(user)
            user.set_password(newpassword)
            user.save()
            print(user.password)
            update_session_auth_hash(request, user)  # Important!
            messages.success(request, 'Your password was successfully updated!')
            return redirect('profile')
        else:
            messages.error(request, 'Please correct the error below.')
    else:
        form = PasswordChangeForm(request.user)
    
    context = {
        'form': form,
        'user': request.user,
    }

    if request.user.role == 'PATIENT':
        dir = PATIENT_DIR
    elif request.user.role == 'DOCTOR':
        dir = DOCTOR_DIR
    elif request.user.role == 'PHARMACIST':
        dir = PHARMACIST_DIR
    else:
        dir = 'generic/'  # Default directory for other roles

    return render(request, dir + 'change_password.html', context)

def diabetes_view(request):
    if not request.user.is_authenticated:
        page_name = "Consultations"
        message = f"You have to login to access {page_name}"
        messages.add_message(request, messages.ERROR, message)
        return HttpResponseRedirect(reverse('login'))
    elif not request.user.role == 'PATIENT':
        usertype = "Patient"
        return render(request, PATIENT_DIR + 'error.html', {'usertype': usertype})
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
        next_url = request.GET.get('next')
        if next_url:
            return redirect(next_url)
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
def consultations(request):
    if not request.user.is_authenticated:
        page_name = "Consultations"
        message = f"You have to login to access {page_name}"
        messages.add_message(request, messages.ERROR, message)
        return HttpResponseRedirect(reverse('login'))
    elif not request.user.role == 'PATIENT':
        usertype = "Patient"
        return render(request, PATIENT_DIR + 'error.html', {'usertype': usertype})
    doctors = DoctorProfile.objects.all()
    latest_request = ConsultationRequest.objects.filter(patient=request.user).order_by('-requested_at').first()

    latest_request_doctor_profile = None
    if latest_request:
        latest_request_doctor_profile = get_object_or_404(DoctorProfile, user=latest_request.doctor)

    print(latest_request_doctor_profile)

    doctor_in_consultations = None
    doctor_in_consultations = ConsultationRequest.objects.filter(status='accepted')
    doctors_accepted = [DoctorProfile.objects.get(user=request.doctor) for request in doctor_in_consultations]

    context = {
        'doctors': doctors,
        'latest_request': latest_request,
        'doctor_request': latest_request_doctor_profile,
        'latest_doctor': latest_request_doctor_profile
    }
    return render(request, PATIENT_DIR + 'consultations.html', context)

def consult_doctor(request, doctor_id):
    if not request.user.is_authenticated:
        page_name = "Consult Doctor"
        message = f"You have to login to access {page_name}"
        messages.add_message(request, messages.ERROR, message)
        return HttpResponseRedirect(reverse('login'))
    elif not request.user.role == 'PATIENT':
        usertype = "Patient"
        return render(request, PATIENT_DIR + 'error.html', {'usertype': usertype})
        
    doctor = get_object_or_404(DoctorProfile, doctor_id=doctor_id)
    return render(request, PATIENT_DIR + 'consult_doctor.html', {'doctor': doctor})

def request_consultation(request, doctor_id):
    if not request.user.is_authenticated:
        page_name = "Request Consultations"
        message = f"You have to login to access {page_name}"
        messages.add_message(request, messages.ERROR, message)
        return HttpResponseRedirect(reverse('login'))
    elif not request.user.role == 'PATIENT':
        usertype = "Patient"
        return render(request, PATIENT_DIR + 'error.html', {'usertype': usertype})
    message = ""
    doctor = get_object_or_404(DoctorProfile, doctor_id=doctor_id)
    doctors = DoctorProfile.objects.all()
    
    latest_request = ConsultationRequest.objects.filter(patient=request.user).order_by('-requested_at').first()
    if latest_request != None and latest_request.status != 'completed' and latest_request.status != 'rejected':
        messages.add_message(request, messages.ERROR, "Please wait before sending another consultation request!")
        return HttpResponseRedirect(reverse('consultations'))

    latest_doctor_request = ConsultationRequest.objects.filter(doctor=doctor.user).order_by('-requested_at').first()
    if latest_doctor_request != None and latest_doctor_request.status == 'accepted':
        messages.add_message(request, messages.ERROR, "Doctor is busy!")
        return HttpResponseRedirect(reverse('consultations'))

    print("bruh")
    ConsultationRequest.objects.create(patient=request.user, doctor=doctor.user)
    messages.add_message(request, messages.SUCCESS, "Consultation request sent.")
    return HttpResponseRedirect(reverse('consultations'))

def consultation_room(request, request_id):
    consultation_request = get_object_or_404(ConsultationRequest, id=request_id)
    doctor = consultation_request.doctor
    doctor_profile = get_object_or_404(DoctorProfile, user=doctor)
    context = {
        'doctor': doctor_profile,
    }
    return render(request, PATIENT_DIR + 'consultation_room.html', context)

# Meds Store
def medicine_list(request, success_message=None):
    if not request.user.is_authenticated:
        page_name = "Store"
        message = f"You have to login to access {page_name}"
        messages.add_message(request, messages.ERROR, message)
        return HttpResponseRedirect(reverse('login'))
    elif not request.user.role == 'PATIENT':
        usertype = "Patient"
        return render(request, PATIENT_DIR + 'error.html', {'usertype': usertype})
    medicines = Medicine.objects.all()
    return render(request, PATIENT_DIR + 'store.html', {'medicines': medicines, 'success_message': success_message})

def medicine_detail(request, medicine_id):
    if not request.user.is_authenticated:
        page_name = "Medicine Detail"
        message = f"You have to login to access {page_name}"
        messages.add_message(request, messages.ERROR, message)
        return HttpResponseRedirect(reverse('login'))
    elif not request.user.role == 'PATIENT':
        usertype = "Patient"
        return render(request, PATIENT_DIR + 'error.html', {'usertype': usertype})
    medicine = get_object_or_404(Medicine, id=medicine_id)
    return render(request, PATIENT_DIR + 'medicine_detail.html', {'medicine': medicine})

def add_to_cart(request, medicine_id):
    if not request.user.is_authenticated:
        page_name = "Add cart"
        message = f"You have to login to access {page_name}"
        messages.add_message(request, messages.ERROR, message)
        return HttpResponseRedirect(reverse('login'))
    elif not request.user.role == 'PATIENT':
        usertype = "Patient"
        return render(request, PATIENT_DIR + 'error.html', {'usertype': usertype})
    medicine = get_object_or_404(Medicine, id=medicine_id)
    order, created = Order.objects.get_or_create(user=request.user, status='pending')
    
    quantity = int(request.GET.get('quantity', 1))
    
    order_item, created = OrderItem.objects.get_or_create(order=order, medicine=medicine)
    order_item.quantity += quantity
    order_item.save()
    
    success_message = 'Item successfully added to cart'  # Add success message here
    
    return HttpResponseRedirect(reverse('medicine_list_with_message', kwargs={'success_message': success_message}))


def user_cart(request):
    if not request.user.is_authenticated:
        page_name = "Cart"
        message = f"You have to login to access {page_name}"
        messages.add_message(request, messages.ERROR, message)
        return HttpResponseRedirect(reverse('login'))
    elif not request.user.role == 'PATIENT':
        usertype = "Patient"
        return render(request, PATIENT_DIR + 'error.html', {'usertype': usertype})
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

def checkout(request):
    if not request.user.is_authenticated:
        page_name = "Checkout"
        message = f"You have to login to access {page_name}"
        messages.add_message(request, messages.ERROR, message)
        return HttpResponseRedirect(reverse('login'))
    elif not request.user.role == 'PATIENT':
        usertype = "Patient"
        return render(request, PATIENT_DIR + 'error.html', {'usertype': usertype})
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


def order_confirmation(request):
    if not request.user.is_authenticated:
        page_name = "Order"
        message = f"You have to login to access {page_name}"
        messages.add_message(request, messages.ERROR, message)
        return HttpResponseRedirect(reverse('login'))
    elif not request.user.role == 'PATIENT':
        usertype = "Patient"
        return render(request, PATIENT_DIR + 'error.html', {'usertype': usertype})
    return render(request, PATIENT_DIR + 'order_confirmation.html')


""" DOCTOR """

def doctor_login_view(request):
    if request.method == "POST":
        form = LoginForm(request, data=request.POST)
        next_url = request.GET.get('next')
        if next_url:
            return redirect(next_url)
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
                messages.add_message(request, messages.ERROR, "Username already taken")
                return HttpResponseRedirect(reverse('doctor_login'))
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
            
            messages.add_message(request, messages.SUCCESS, "Created account successful;y")
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
    if not request.user.is_authenticated:
        page_name = "Doctor Home"
        message = f"You have to login to access {page_name}"
        messages.add_message(request, messages.ERROR, message)
        return HttpResponseRedirect(reverse('doctor_login'))
    elif not request.user.role == 'DOCTOR':
        usertype = "Doctor"
        return render(request, PATIENT_DIR + 'error.html', {'usertype': usertype})
    return render(request, DOCTOR_DIR + 'index.html')

def doctor_consultation_room(request, request_id):
    consultation_request = get_object_or_404(ConsultationRequest, id=request_id)
    patient = consultation_request.patient
    patient_profile = get_object_or_404(ConsultationRequest, user=patient)
    context = {
        'patient': patient_profile,
    }
    return render(request, DOCTOR_DIR + 'consultation_room.html', context)

def doctor_dashboard(request):
    if not request.user.is_authenticated:
        page_name = "Doctor Dashboard"
        message = f"You have to login to access {page_name}"
        messages.add_message(request, messages.ERROR, message)
        return HttpResponseRedirect(reverse('doctor_login'))
    elif not request.user.role == 'DOCTOR':
        usertype = "Doctor"
        return render(request, PATIENT_DIR + 'error.html', {'usertype': usertype})
    if request.user.role != User.Role.DOCTOR:
        return HttpResponseRedirect(reverse('index')) 

    if request.method == 'POST':
        request_id = request.POST.get('request_id')
        action_type = request.POST.get('action_type')
        consultation_request = get_object_or_404(ConsultationRequest, id=request_id, doctor=request.user)

        if action_type == 'accept':
            is_in_consultation = ConsultationRequest.objects.filter(doctor=request.user, status='accepted')
            print(is_in_consultation)
            if is_in_consultation.exists():
                messages.error(request, "Please complete the current request first!")
                return HttpResponseRedirect(reverse('doctor_dashboard'))

            consultation_request.status = 'accepted'
            consultation_request.accepted_at = timezone.now()

            doctor_profile = DoctorProfile.objects.get(user=request.user)
            doctor_profile.is_available = False
            doctor_profile.save()

            messages.success(request, 'Consultation accepted successfully.')
        elif action_type == 'reject':
            consultation_request.status = 'rejected'
            messages.error(request, 'Consultation rejected successfully.')
        elif action_type == 'complete':
            consultation_request.status = 'completed'
            consultation_request.completed_at = timezone.now()
            
            # Update doctor's availability
            doctor_profile = DoctorProfile.objects.get(user=request.user)
            doctor_profile.is_available = True
            doctor_profile.save()

            messages.warning(request, 'Consultation marked as completed.')

        consultation_request.save()
        return redirect('doctor_dashboard')

    requests = ConsultationRequest.objects.filter(doctor=request.user).order_by('-requested_at')

    # Count requests by status
    rejected_count = requests.filter(status='rejected').count()
    in_progress_count = requests.filter(status='accepted').count()  # Assuming 'accepted' means in progress
    done_count = requests.filter(status='completed').count()

    context = {
        'requests': requests,
        'rejected_count': rejected_count,
        'in_progress_count': in_progress_count,
        'done_count': done_count,
    }

    return render(request, DOCTOR_DIR + 'dashboard.html', context)

def accept_consultation(request, request_id):
    if not request.user.is_authenticated:
        page_name = "Accept Consultations"
        message = f"You have to login to access {page_name}"
        messages.add_message(request, messages.ERROR, message)
        return HttpResponseRedirect(reverse('doctor_login'))
    elif not request.user.role == 'DOCTOR':
        usertype = "Doctor"
        return render(request, PATIENT_DIR + 'error.html', {'usertype': usertype})
    
    is_in_consultation = ConsultationRequest.objects.filter(doctor=request.user, status='accepted')
    print(is_in_consultation)
    if is_in_consultation != None:
        messages.error(request, "Please complete the current request first!")
        return HttpResponseRedirect(reverse('doctor_dashboard'))


    consultation_request = get_object_or_404(ConsultationRequest, id=request_id, doctor=request.user)
    consultation_request.status = 'accepted'
    consultation_request.accepted_at = timezone.now()

    try:
        doctor_profile = DoctorProfile.objects.get(user=request.user)
        doctor_profile.is_available = False
        doctor_profile.save()
    except Exception:
        messages.success(request, "Error OCcurred.")
        return HttpResponseRedirect(reverse('doctor_dashboard'))

    consultation_request.save()
    messages.success(request, "Consultation request accepted.")
    return HttpResponseRedirect(reverse('doctor_dashboard'))

def mark_consultation_completed(request, request_id):
    if not request.user.is_authenticated:
        page_name = "Consultation Completed"
        message = f"You have to login to access {page_name}"
        messages.add_message(request, messages.ERROR, message)
        return HttpResponseRedirect(reverse('doctor_login'))
    elif not request.user.role == 'DOCTOR':
        usertype = "Doctor"
        return render(request, PATIENT_DIR + 'error.html', {'usertype': usertype})
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


def reject_consultation(request, request_id):
    if not request.user.is_authenticated:
        page_name = "Reject Consultations"
        message = f"You have to login to access {page_name}"
        messages.add_message(request, messages.ERROR, message)
        return HttpResponseRedirect(reverse('doctor_login'))
    elif not request.user.role == 'DOCTOR':
        usertype = "Doctor"
        return render(request, PATIENT_DIR + 'error.html', {'usertype': usertype})
    consultation_request = get_object_or_404(ConsultationRequest, id=request_id, doctor=request.user)
    consultation_request.status = 'rejected'
    consultation_request.save()
    messages.success(request, "Consultation request rejected.")
    return HttpResponseRedirect(reverse('doctor_dashboard'))


def view_medical_history(request, request_id):
    # Retrieve the consultation request
    consultation_request = get_object_or_404(ConsultationRequest, id=request_id)
    
    # Ensure the request is accepted before accessing medical history
    if consultation_request.status != 'accepted':
        return render(request, 'error.html', {'message': 'Consultation request is not accepted.'})
    
    # Retrieve the patient's medical history
    patient_profile = get_object_or_404(PatientProfile, user=consultation_request.patient)

    medical_history = MedicalHistory.objects.filter(patient=patient_profile).order_by('-diagnosis_date')
    
    context = {
        'consultation_request': consultation_request,
        'medical_history': medical_history,
    }
    
    return render(request, DOCTOR_DIR + 'view_medical_history.html', context)


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("login"))

def doctor_logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("doctor_login"))

def pharmacist_logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("pharmacist_login"))


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
            profile_photo = profile_form.cleaned_data.get('profile_photo')

            print()
            print(profile_form.cleaned_data)

            # save profile
            # print(pharmacy_name, pharmacy_city, latitude, phone_number, longitude, profile_photo)
            profile = PharmacistProfile(
                user=user,
                pharmacy_name=pharmacy_name,
                pharmacy_city=pharmacy_city,
                latitude=latitude,
                phone_number=phone_number,
                longitude=longitude,
                profile_photo=profile_photo
            )
            profile.save()
            
            messages.add_message(request, messages.SUCCESS, "Created account successfully")
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


def manage_medicines(request):
    if not request.user.is_authenticated:
        page_name = "Manage Medicines"
        message = f"You have to login to access {page_name}"
        messages.add_message(request, messages.ERROR, message)
        return HttpResponseRedirect(reverse('pharmacist_login'))
    elif request.user.role != 'PHARMACIST':
        usertype = "Pharmacist"
        return render(request, 'patient/error.html', {'usertype': usertype})
    
    if request.method == 'POST':
        medicine_id = request.POST.get('medicine_id')
        medicine = get_object_or_404(Medicine, id=medicine_id, pharmacist=request.user)
        medicine.delete()
        messages.add_message(request, messages.SUCCESS, "Medicine deleted successfully.")
        return redirect('manage_medicines')

    medicines = Medicine.objects.filter(pharmacist=request.user)
    return render(request, PHARMACIST_DIR + 'manage_medicines.html', {'medicines': medicines})

def add_medicine(request):
    if not request.user.is_authenticated:
        page_name = "Add Medicines"
        message = f"You have to login to access {page_name}"
        messages.add_message(request, messages.ERROR, message)
        return HttpResponseRedirect(reverse('pharmacist_login'))
    elif not request.user.role == 'PHARMACIST':
        usertype = "Pharmacist"
        return render(request, PATIENT_DIR + 'error.html', {'usertype': usertype})
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

def edit_medicine(request, medicine_id):
    if not request.user.is_authenticated:
        page_name = "Edit Medicines"
        message = f"You have to login to access {page_name}"
        messages.add_message(request, messages.ERROR, message)
        return HttpResponseRedirect(reverse('pharmacist_login'))
    elif not request.user.role == 'PHARMACIST':
        usertype = "Pharmacist"
        return render(request, PATIENT_DIR + 'error.html', {'usertype': usertype})
    medicine = get_object_or_404(Medicine, id=medicine_id, pharmacist=request.user)
    if request.method == 'POST':
        form = MedicineForm(request.POST, request.FILES, instance=medicine)
        if form.is_valid():
            form.save()
            return redirect('manage_medicines')
    else:
        form = MedicineForm(instance=medicine)
    return render(request, PHARMACIST_DIR +  'edit_medicine.html', {'form': form})

def delete_medicine(request, medicine_id):
    if not request.user.is_authenticated:
        page_name = "Delete Medicines"
        message = f"You have to login to access {page_name}"
        messages.add_message(request, messages.ERROR, message)
        return HttpResponseRedirect(reverse('pharmacist_login'))
    elif not request.user.role == 'PHARMACIST':
        usertype = "Pharmacist"
        return render(request, PATIENT_DIR + 'error.html', {'usertype': usertype})
    medicine = get_object_or_404(Medicine, id=medicine_id, pharmacist=request.user)
    if request.method == 'POST':
        medicine.delete()
        return redirect('manage_medicines')
    return render(request, PHARMACIST_DIR + 'delete_medicine.html', {'medicine': medicine})

def pharmacist_dashboard(request):
    if not request.user.is_authenticated:
        page_name = "Pharmacist Dashboard"
        message = f"You have to login to access {page_name}"
        messages.add_message(request, messages.ERROR, message)
        return HttpResponseRedirect(reverse('pharmacist_login'))
    elif not request.user.role == 'PHARMACIST':
        usertype = "Pharmacist"
        return render(request, PATIENT_DIR + 'error.html', {'usertype': usertype})
    purchase_requests = PurchaseRequest.objects.filter(pharmacist=request.user)
    return render(request, PHARMACIST_DIR + 'dashboard.html', {'purchase_requests': purchase_requests})

def update_purchase_request_status(request, purchase_request_id, status):
    if not request.user.is_authenticated:
        page_name = "Update status"
        message = f"You have to login to access {page_name}"
        messages.add_message(request, messages.ERROR, message)
        return HttpResponseRedirect(reverse('pharmacist_login'))
    elif not request.user.role == 'PHARMACIST':
        usertype = "Pharmacist"
        return render(request, PATIENT_DIR + 'error.html', {'usertype': usertype})
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
    if not request.user.is_authenticated:
        page_name = "Pharmacist Home"
        message = f"You have to login to access {page_name}"
        messages.add_message(request, messages.ERROR, message)
        return HttpResponseRedirect(reverse('pharmacist_login'))
    elif not request.user.role == 'PHARMACIST':
        usertype = "Pharmacist"
        return render(request, PATIENT_DIR + 'error.html', {'usertype': usertype})
    return render(request, PHARMACIST_DIR + 'index.html')

def custom_404_view(request, exception=None):
    return render(request, PATIENT_DIR + '404.html', status=404)