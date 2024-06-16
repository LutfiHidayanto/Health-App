
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.utils import timezone
from django.db.models.signals import post_save
from django.db.models.functions import Cast
from django.dispatch import receiver

    

class User(AbstractUser):
    class Role(models.TextChoices):
        ADMIN = "ADMIN", "Admin"
        DOCTOR = "DOCTOR", "Doctor"
        PATIENT = "PATIENT", "Patient"
        PHARMACIST = "PHARMACIST", "Pharmacist"
        

    base_role = Role.ADMIN

    role = models.CharField(max_length=50, choices=Role.choices, default=Role.ADMIN)

    def save(self, *args, **kwargs):
        if not self.pk:
            self.role = self.base_role
            return super().save(*args, **kwargs)


""" PATIENT """

class PatientManager(BaseUserManager):
    def get_queryset(self, *args, **kwargs):
        results = super().get_queryset(*args, **kwargs)
        return results.filter(role=User.Role.PATIENT)


class Patient(User):

    base_role = User.Role.PATIENT

    patient = PatientManager()

    class Meta:
        proxy = True

    def welcome(self):
        return "Only for patients"


@receiver(post_save, sender=Patient)
def create_user_profile(sender, instance, created, **kwargs):
    if created and instance.role == "PATIENT":
        PatientProfile.objects.create(user=instance)


class PatientProfile(models.Model):
    SEX = [
        ('MALE', 'Male'),
        ('FEMALE', 'Female')
    ]

    patient_id = models.IntegerField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date_of_birth = models.DateField(null=True, blank=True)
    sex = models.CharField(max_length=10, choices=SEX, default=SEX[0])
    address = models.CharField(max_length=255, null=True, blank=True)
    phone_number = models.CharField(max_length=15, null=True, blank=True)
    profile_photo = models.ImageField(upload_to='patient_photos/', null=True, blank=True)

class MedicalHistory(models.Model):
    patient = models.ForeignKey(PatientProfile, related_name='medical_history', on_delete=models.CASCADE)
    condition = models.CharField(max_length=255)
    diagnosis_date = models.DateField()
    notes = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"Medical History of {self.patient.user.username}: {self.condition}"


""" DOCTOR """

class DoctorManager(BaseUserManager):
    def get_queryset(self, *args, **kwargs):
        results = super().get_queryset(*args, **kwargs)
        return results.filter(role=User.Role.DOCTOR)


class Doctor(User):

    base_role = User.Role.DOCTOR

    doctor = DoctorManager()

    class Meta:
        proxy = True

    def welcome(self):
        return "Only for doctors"


class DoctorProfile(models.Model):
    SPECIALTY_CHOICES = [
        ('Umum', 'Umum'),
        ('Anak', 'Anak'),
        ('Kulit', 'Kulit'),
        ('Penyakit Dalam', 'Penyakit Dalam'),
        ('Psikiater', 'Psikiater'),
        ('Kandungan', 'Kandungan'),
        ('Hewan', 'Hewan'),
        ('Psikolog Klinis', 'Psikolog Klinis'),
        ('THT', 'THT'),
        ('Urologi', 'Urologi'),
        ('Andrologi', 'Andrologi'),
        ('Jiwa', 'Jiwa'),
        ('Gizi', 'Gizi'),
        ('Paru', 'Paru'),
        ('Gigi', 'Gigi'),
        ('Bedah', 'Bedah'),
        ('Saraf', 'Saraf'),
        ('Jantung', 'Jantung'),
        ('Konselor Laktasi', 'Konselor Laktasi'),
        ('Kandungan', 'Kandungan'),
        ('Mata', 'Mata'),
        ('Fisioterapi', 'Fisioterapi'),
        ('Bidan', 'Bidan'),
    ]
     
    doctor_id = models.IntegerField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    specialty = models.CharField(max_length=50, choices=SPECIALTY_CHOICES, default=SPECIALTY_CHOICES[0])
    is_available = models.BooleanField(default=True)
    years_of_experience = models.IntegerField(null=True, blank=True)
    phone_number = models.CharField(max_length=15, null=True, blank=True)
    profile_photo = models.ImageField(upload_to='doctor_photos/', null=True, blank=True)


class PharmacistManager(BaseUserManager):
    def get_queryset(self, *args, **kwargs):
        results = super().get_queryset(*args, **kwargs)
        return results.filter(role=User.Role.PHARMACIST)


""" PHARMACIST """

class Pharmacist(User):

    base_role = User.Role.PHARMACIST

    pharmacist = PharmacistManager()

    class Meta:
        proxy = True

    def welcome(self):
        return "Only for pharmacists"


class PharmacistProfile(models.Model):
    pharmacist_id = models.IntegerField(primary_key=True)  
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    pharmacy_name = models.CharField(max_length=64, null=True, blank=True)
    pharmacy_city = models.CharField(max_length=64, null=True, blank=True)
    phone_number = models.CharField(max_length=15, null=True, blank=True)
    latitude = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True)
    longitude = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True)
    profile_photo = models.ImageField(upload_to='pharmacist_photos/', null=True, blank=True)


@receiver(post_save, sender=Pharmacist)
def create_user_profile(sender, instance, created, **kwargs):
    if created and instance.role == "PHARMACIST":
        PharmacistProfile.objects.create(user=instance)


""" CONSULTATIONS """

class ConsultationRequest(models.Model):
    patient = models.ForeignKey(Patient, related_name='patient_requests', on_delete=models.CASCADE)
    doctor = models.ForeignKey(Doctor, related_name='doctor_requests', on_delete=models.CASCADE)
    status = models.CharField(max_length=50, choices=[
        ('waiting', 'Waiting'),
        ('accepted', 'Accepted'),
        ('completed', 'Completed'),
        ('rejected', 'Rejected')
    ], default='waiting')
    requested_at = models.DateTimeField(auto_now_add=True)
    accepted_at = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"Consultation Request from {self.patient} to {self.doctor}"
    

""" ML PREDICTION """

class diabetesPrediction(models.Model):
    # Categorical features
    Diabetes_binary = models.BooleanField(default=False)
    HighBP = models.BooleanField(default=False)
    HighChol = models.BooleanField(default=False)
    CholCheck = models.BooleanField(default=False)
    Smoker = models.BooleanField(default=False)
    Stroke = models.BooleanField(default=False)
    HeartDiseaseorAttack = models.BooleanField(default=False)
    PhysActivity = models.BooleanField(default=False)
    Fruits = models.BooleanField(default=False)
    Veggies = models.BooleanField(default=False)
    HvyAlcoholConsump = models.BooleanField(default=False)
    AnyHealthcare = models.BooleanField(default=False)
    NoDocbcCost = models.BooleanField(default=False)
    DiffWalk = models.BooleanField(default=False)
    Sex = models.BooleanField(default=False)

    # Non-categorical features
    BMI = models.FloatField(default=0.0)
    GenHlth = models.FloatField(default=0.0)
    MentHlth = models.FloatField(default=0.0)
    PhysHlth = models.FloatField(default=0.0)
    Age = models.FloatField(default=0.0)

""" MEDS STORE MODEL """

class Medicine(models.Model):
    pharmacist = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'role': 'PHARMACIST'})
    name = models.CharField(max_length=100)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.IntegerField()
    image = models.ImageField(upload_to='medicine_images/', null=True, blank=True)

    def __str__(self):
        return self.name

class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'role': 'PATIENT'})
    ordered_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=50, choices=[
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('canceled', 'Canceled')
    ], default='pending')

    def __str__(self):
        return f"Order {self.id} by {self.user.username}"

    @property
    def total_quantity(self):
        return sum(item.quantity for item in self.items.all())

    @property
    def total_price(self):
        return sum(item.quantity * item.medicine.price for item in self.items.all())


class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    medicine = models.ForeignKey(Medicine, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.quantity} x {self.medicine.name}"
    
    @property
    def total_price(self):
        return self.quantity * self.medicine.price

class PurchaseRequest(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    pharmacist = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'role': 'PHARMACIST'})
    status = models.CharField(max_length=50, choices=[
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('completed', 'Completed'),
        ('rejected', 'Rejected')
    ], default='pending')
    requested_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Purchase Request {self.id} for Order {self.order.id}"