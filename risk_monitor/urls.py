from django.urls import path
from . import views

app_name = 'risk_monitor'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('patients/', views.patient_list, name='patient_list'),
    path('patients/add/', views.patient_create, name='patient_create'),
    path('patients/<int:pk>/edit/', views.patient_update, name='patient_edit'),
    path('patients/<int:pk>/delete/', views.patient_delete, name='patient_delete'),
    path('audit-log/', views.audit_log, name='audit_log'),
    path('audit-log/export/', views.export_audit_csv, name='export_audit_csv'),
]
