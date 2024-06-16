from django.urls import path
from . import views
from django.conf.urls.static import static
from django.conf import settings 


urlpatterns = [
    path('', views.landing, name="landing"),
    path('home/', views.index, name="index"),
    path('diabetes/', views.diabetes_view, name="diabetes-view"),
    path("login/", views.patient_login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("register/", views.patient_register_view, name="register"),

    path('profile/', views.profile_view, name='profile'),
    path('profile/edit/', views.edit_profile_view, name='edit_profile'),

    path('medical_history/', views.medical_history_view, name='medical_history'),


    path("consultations/", views.consultations, name="consultations"),
    path("consultations/<int:doctor_id>/", views.consult_doctor, name="consult_doctor"),
    path("consultations/request/<int:doctor_id>/", views.request_consultation, name="request_consultation"),
    path('doctor/', views.doctor_index, name="doctor_index"),
    path('doctor/dashboard', views.doctor_dashboard, name="doctor_dashboard"),
    path("doctor/register", views.doctor_register_view, name="doctor_register"),
    path("doctor/login", views.doctor_login_view, name="doctor_login"),
    path('doctor/accept/<int:request_id>/', views.accept_consultation, name='accept_consultation'),
    path('doctor/reject/<int:request_id>/', views.reject_consultation, name='reject_consultation'),
    path('doctor/complete/<int:request_id>/', views.mark_consultation_completed, name='mark_consultation_completed'),
    path('consultation_room/<int:request_id>/', views.consultation_room, name='consultation_room'),
    path('doctor/consultation_room/<int:request_id>/', views.doctor_consultation_room, name='doctor_consultation_room'),
    path('pharmacist/', views.pharmacist_index, name="pharmacist_index"),
    path("pharmacist/register", views.pharmacist_register_view, name="pharmacist_register"),
    path("pharmacist/login", views.pharmacist_login_view, name="pharmacist_login"),
    path("pharmacist/dashboard", views.pharmacist_dashboard, name="pharmacist_dashboard"),
    path('purchase_requests/<int:purchase_request_id>/status/<str:status>/', views.update_purchase_request_status, name='update_purchase_request_status'),

    # path("pharmacist/sell", views.pharmacist_sell_view, name="pharmacist_sell"),
    # path("pharmacist/request", views.pharmacist_request_view, name="pharmacist_request"),
    path('medicines/', views.medicine_list, name='medicine_list'),
    path('medicines/<str:success_message>/', views.medicine_list, name='medicine_list_with_message'),
    path('medicines/<int:medicine_id>/', views.medicine_detail, name='medicine_detail'),
    path('medicines/<int:medicine_id>/add_to_cart/', views.add_to_cart, name='add_to_cart'),
    path('cart/', views.user_cart, name='user_cart'),
    path('checkout/', views.checkout, name='checkout'),
    path('order_confirmation/', views.order_confirmation, name='order_confirmation'),
    path('pharmacist/manage_medicines/', views.manage_medicines, name='manage_medicines'),
    path('pharmacist/manage_medicines/add/', views.add_medicine, name='add_medicine'),
    path('pharmacist/manage_medicines/add/', views.add_medicine, name='add_medicine'),
    path('pharmacist/manage_medicines/<int:medicine_id>/edit/', views.edit_medicine, name='edit_medicine'),
    path('pharmacist/manage_medicines/<int:medicine_id>/delete/', views.delete_medicine, name='delete_medicine'),
    path('logout/', views.logout_view, name='logout'),
    path('doctor_logout/', views.doctor_logout_view, name='doctor_logout'),
    path('pharmacist_logout/', views.pharmacist_logout_view, name='pharmacist_logout'),


] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
 