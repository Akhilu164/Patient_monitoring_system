from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

from django.utils import timezone

class Patient(models.Model):
    RISK_CHOICES = [
        ('LOW', 'Low'),
        ('MEDIUM', 'Medium'),
        ('HIGH', 'High'),
    ]

    full_name = models.CharField(max_length=255)
    age = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(120)])
    gender = models.CharField(max_length=20, choices=[('Male', 'Male'), ('Female', 'Female'), ('Other', 'Other')])
    contact_details = models.CharField(max_length=255, blank=True)
    admission_date = models.DateField(null=True, blank=True)
    
    # Vitals
    heart_rate = models.IntegerField(help_text="BPM")
    systolic_bp = models.IntegerField(help_text="mmHg")
    spo2 = models.IntegerField(help_text="%", validators=[MinValueValidator(0), MaxValueValidator(100)])
    temperature = models.FloatField(help_text="Celsius")
    respiratory_rate = models.IntegerField(help_text="Breaths/min")
    
    # Clinical History
    chronic_conditions = models.JSONField(default=list, blank=True, help_text="List of chronic conditions")
    er_visits = models.IntegerField(default=0, help_text="Number of ER visits in last 30 days")
    
    # Lab Indicators
    wbc_flag = models.BooleanField(default=False, verbose_name="Elevated WBC")
    creatinine_flag = models.BooleanField(default=False, verbose_name="Elevated Creatinine")
    crp_flag = models.BooleanField(default=False, verbose_name="Elevated CRP")
    
    # Clinical Observations
    notes = models.TextField(blank=True, verbose_name="Clinical Notes")
    
    # Risk Assessment (Auto-calculated)
    risk_score = models.IntegerField(default=0, editable=False)
    risk_level = models.CharField(max_length=10, choices=RISK_CHOICES, default='LOW', editable=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        # Always recalculate risk score and level before saving
        from risk_monitor.services.risk_engine import calculate_risk
        data = {
            'age': self.age,
            'heart_rate': self.heart_rate,
            'systolic_bp': self.systolic_bp,
            'spo2': self.spo2,
            'temperature': self.temperature,
            'respiratory_rate': self.respiratory_rate,
            'chronic_conditions': self.chronic_conditions or [],
            'er_visits': self.er_visits,
            'wbc_flag': self.wbc_flag,
            'creatinine_flag': self.creatinine_flag,
            'crp_flag': self.crp_flag,
        }
        result = calculate_risk(data)
        self.risk_score = result['total_score']
        self.risk_level = result['risk_level']
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.full_name} ({self.risk_level})"

class AuditLog(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='audit_logs')
    field_name = models.CharField(max_length=100)
    old_value = models.TextField(null=True, blank=True)
    new_value = models.TextField(null=True, blank=True)
    risk_before = models.CharField(max_length=10)
    risk_after = models.CharField(max_length=10)
    score_before = models.IntegerField(default=0)
    score_after = models.IntegerField(default=0)
    reason = models.TextField(blank=True, help_text="Risk trace reasoning")
    batch_id = models.UUIDField(null=True, blank=True, help_text="Groups multiple field changes from one update")
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Audit for {self.patient.full_name} - {self.field_name}"
