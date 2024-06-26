from django import forms
from .models import diabetesPrediction, User, Patient, Doctor, Pharmacist, PatientProfile, DoctorProfile, PharmacistProfile, Medicine, MedicalHistory
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.forms import PasswordChangeForm as DjangoPasswordChangeForm


class LoginForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Username'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'}))

""" PATIENT FORM """
class PatientRegistrationForm(UserCreationForm):
    class Meta:
        model = Patient
        fields = ['username', 'password1', 'password2', 'first_name', 'last_name', 'email']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
            field.widget.attrs['placeholder'] = field.label

class PatientUpdateForm(forms.ModelForm):
    class Meta:
        model = Patient
        fields = ['username', 'password', 'first_name', 'last_name', 'email']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
            field.widget.attrs['placeholder'] = field.label

class DoctorUpdateForm(forms.ModelForm):
    class Meta:
        model = Doctor
        fields = ['username', 'password', 'first_name', 'last_name', 'email']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
            field.widget.attrs['placeholder'] = field.label


class PharmacistUpdateForm(forms.ModelForm):
    class Meta:
        model = Pharmacist
        fields = ['username', 'password', 'first_name', 'last_name', 'email']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
            field.widget.attrs['placeholder'] = field.label



class PatientProfileForm(forms.ModelForm):
    sex = forms.ChoiceField(choices=PatientProfile.SEX, required=True)
    date_of_birth = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))

    class Meta:
        model = PatientProfile
        fields = ['date_of_birth', 'sex', 'address', 'phone_number', 'profile_photo']

""" MEDICAL HISTORY FORM """
class MedicalHistoryForm(forms.ModelForm):
    diagnosis_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))

    class Meta:
        model = MedicalHistory
        fields = ['condition', 'diagnosis_date', 'notes']


""" DOCTOR FORM """
class DoctorRegistrationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'password1', 'password2', 'first_name', 'last_name', 'email']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
            field.widget.attrs['placeholder'] = field.label

class DoctorProfileForm(forms.ModelForm):
    specialty = forms.ChoiceField(choices=DoctorProfile.SPECIALTY_CHOICES, required=True)

    class Meta: 
        model = DoctorProfile
        fields = ['specialty', 'years_of_experience', 'phone_number', 'profile_photo']

class DoctorProfileUpdateForm(forms.ModelForm):
    specialty = forms.ChoiceField(choices=DoctorProfile.SPECIALTY_CHOICES, required=True)

    class Meta: 
        model = DoctorProfile
        fields = ['specialty', 'years_of_experience', 'is_available', 'phone_number', 'profile_photo']


""" PHARMACIST FORM """
class PharmacistRegistrationForm(UserCreationForm):
    class Meta:
        model = Pharmacist
        fields = ['username', 'password1', 'password2', 'first_name', 'last_name', 'email']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
            field.widget.attrs['placeholder'] = field.label

class PharmacistProfileForm(forms.ModelForm):
    class Meta:
        model = PharmacistProfile
        fields = ['pharmacy_name', 'pharmacy_city', 'phone_number', 'latitude', 'longitude', 'profile_photo']

class diabetesPredictionForm(forms.ModelForm):
    class Meta:
        model = diabetesPrediction
        exclude = ['Diabetes_binary']
        labels = {
            'HighBP': 'High Blood Pressure',
            'HighChol': 'High Cholesterol',
            'CholCheck': 'Cholesterol Check',
            'Smoker': 'Smoker',
            'Stroke': 'Stroke',
            'HeartDiseaseorAttack': 'Heart Disease or Attack',
            'PhysActivity': 'Physical Activity',
            'Fruits': 'Fruits Consumption',
            'Veggies': 'Vegetables Consumption',
            'HvyAlcoholConsump': 'Heavy Alcohol Consumption',
            'AnyHealthcare': 'Any Healthcare',
            'NoDocbcCost': 'No Doctor Due to Cost',
            'DiffWalk': 'Difficulty Walking',
            'Sex': 'Sex',
            'BMI': 'Body Mass Index',
            'GenHlth': 'General Health(1-5)',
            'MentHlth': 'Mental Health(0-30)',
            'PhysHlth': 'Physical Health(0-30)',
            'Age': 'Age'
        }


""" MEDS STORE FORM """

class MedicineForm(forms.ModelForm):
    class Meta:
        model = Medicine
        fields = ['name', 'description', 'price', 'stock', 'image']

class PasswordChangeForm(DjangoPasswordChangeForm):
    old_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Old Password'}),
        label="Old Password"
    )
    new_password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'New Password'}),
        label="New Password"
    )
    new_password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Confirm New Password'}),
        label="Confirm New Password"
    )

