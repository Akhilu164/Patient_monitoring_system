from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Count
from django.utils import timezone
from django.http import HttpResponse
import json
import csv

from .models import Patient, AuditLog
from .forms import PatientForm
from .services.risk_engine import calculate_risk
from .services.audit_service import update_patient_risk_and_audit, create_patient_with_risk
from .utils.pdf_parser import extract_vitals_from_pdf

def dashboard(request):
    """
    Renders the dashboard with analytics.
    """
    total_patients = Patient.objects.count()
    high_risk_count = Patient.objects.filter(risk_level='HIGH').count()
    recent_admissions = Patient.objects.order_by('-admission_date')[:5]

    # Risk Distribution for Pie Chart
    risk_distribution = list(Patient.objects.values('risk_level').annotate(count=Count('risk_level')))
    
    context = {
        'total_patients': total_patients,
        'high_risk_count': high_risk_count,
        'recent_admissions': recent_admissions,
        'risk_distribution': json.dumps(list(risk_distribution)), 
    }
    return render(request, 'dashboard.html', context)

def patient_list(request):
    patients = Patient.objects.all().order_by('-created_at')
    return render(request, 'patient_list.html', {'patients': patients})

from django.contrib import messages

def patient_create(request):
    if request.method == 'POST':
        # Handle Autofill separate from Save
        if 'autofill' in request.POST:
            extracted_data = {}
            if request.FILES.get('pdf_file'):
                pdf_file = request.FILES['pdf_file']
                print(f"DEBUG: Processing PDF {pdf_file.name}, size: {pdf_file.size}")
                try:
                    # Reset file pointer if needed
                    pdf_file.seek(0)
                    extracted_data = extract_vitals_from_pdf(pdf_file)
                    print(f"DEBUG: Extracted Data: {extracted_data}")
                    
                    if extracted_data:
                        count = len(extracted_data)
                        messages.success(request, f"Successfully extracted {count} fields from PDF.")
                    else:
                        messages.warning(request, "PDF processed but no data could be extracted. Please check the file format.")
                        
                except Exception as e:
                    print(f"DEBUG: PDF Error: {e}")
                    messages.error(request, "Error processing PDF file.")
            else:
                print("DEBUG: No PDF file found in request.FILES")
                messages.error(request, "Please upload a PDF file to autofill data.")
            
            data = request.POST.copy()
            for k, v in extracted_data.items():
                if v:
                    data[k] = v
            
            form = PatientForm(data)
            return render(request, 'patient_form.html', {'form': form, 'autofilled': True})

        form = PatientForm(request.POST, request.FILES)
        if form.is_valid():
            patient_data = form.cleaned_data.copy()
            if 'pdf_file' in patient_data:
                del patient_data['pdf_file']
            
            try:
                create_patient_with_risk(patient_data)
                messages.success(request, "Patient record created successfully.")
                return redirect('risk_monitor:dashboard')
            except Exception as e:
                # Error logged via Django messages below
                messages.error(request, f"Total creation failure: {e}")
        else:
            # Errors handled via form.errors in template
            messages.error(request, "Please correct the errors below.")
    else:
        form = PatientForm()

    return render(request, 'patient_form.html', {'form': form})

def patient_update(request, pk):
    patient = get_object_or_404(Patient, pk=pk)
    
    if request.method == 'POST':
        form = PatientForm(request.POST, request.FILES, instance=patient)
        if form.is_valid():
            new_data = form.cleaned_data.copy()
            if 'pdf_file' in new_data:
                del new_data['pdf_file']
                
            update_patient_risk_and_audit(patient.id, new_data)
            return redirect('risk_monitor:patient_list')
    else:
        form = PatientForm(instance=patient)
    
    raw_logs = patient.audit_logs.all().order_by('-timestamp')
    audit_logs = []
    
    # Group logs by batch_id
    from itertools import groupby
    from operator import attrgetter
    
    # Sort by batch_id and timestamp if needed, but they are already ordered by timestamp
    # We use batch_id for grouping, but the set might have None for old logs
    for key, group in groupby(raw_logs, key=attrgetter('batch_id')):
        logs_in_group = list(group)
        # For entries without batch_id, treat each as its own group
        if key is None:
            for log in logs_in_group:
                audit_logs.append({
                    'timestamp': log.timestamp,
                    'reason': log.reason,
                    'risk_before': log.risk_before,
                    'risk_after': log.risk_after,
                    'score_before': log.score_before,
                    'score_after': log.score_after,
                    'changes': [log]
                })
        else:
            first_log = logs_in_group[0]
            audit_logs.append({
                'timestamp': first_log.timestamp,
                'batch_id': key,
                'reason': first_log.reason,
                'risk_before': first_log.risk_before,
                'risk_after': first_log.risk_after,
                'score_before': first_log.score_before,
                'score_after': first_log.score_after,
                'changes': logs_in_group
            })
            
    return render(request, 'patient_form.html', {
        'form': form, 
        'patient': patient, 
        'audit_logs': audit_logs
    })

def patient_delete(request, pk):
    patient = get_object_or_404(Patient, pk=pk)
    if request.method == 'POST':
        patient.delete()
        messages.success(request, "Patient record deleted successfully.")
        return redirect('risk_monitor:patient_list')
    return render(request, 'patient_confirm_delete.html', {'patient': patient})

def audit_log(request):
    logs = AuditLog.objects.select_related('patient').order_by('-timestamp')
    return render(request, 'audit_log.html', {'logs': logs})

def export_audit_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="audit_logs.csv"'

    writer = csv.writer(response)
    writer.writerow(['Timestamp', 'Patient', 'Field', 'Old Value', 'New Value', 'Risk Before', 'Risk After'])

    logs = AuditLog.objects.select_related('patient').all().order_by('-timestamp')
    for log in logs:
        writer.writerow([
            log.timestamp,
            log.patient.full_name,
            log.field_name,
            log.old_value,
            log.new_value,
            log.risk_before,
            log.risk_after
        ])

    return response
