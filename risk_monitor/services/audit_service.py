from risk_monitor.models import Patient, AuditLog
from risk_monitor.services.risk_engine import calculate_risk
from django.forms.models import model_to_dict
import json

def update_patient_risk_and_audit(patient_id, new_data):
    """
    Updates patient data, recalculates risk, and logs changes with a detailed risk trace.
    """
    try:
        patient = Patient.objects.get(id=patient_id)
        # model_to_dict can sometimes return weird formats for JSONFields if not careful
        old_data = {field.name: getattr(patient, field.name) for field in patient._meta.fields}
    except Patient.DoesNotExist:
        return None

    # Calculate risks
    old_risk = calculate_risk(old_data)
    new_risk = calculate_risk(new_data)
    
    # Track changes
    changed_fields = []
    
    for field, value in new_data.items():
        if hasattr(patient, field):
            old_val = getattr(patient, field)
            
            # Special case for lists/JSON comparison
            if isinstance(value, list) and isinstance(old_val, list):
                if sorted(value) != sorted(old_val):
                    setattr(patient, field, value)
                    changed_fields.append({
                        'field': field,
                        'old': old_val,
                        'new': value
                    })
            elif old_val != value:
                setattr(patient, field, value)
                changed_fields.append({
                    'field': field,
                    'old': old_val,
                    'new': value
                })

    # Risk Trace Logic
    added_reasons = set(new_risk['reasons']) - set(old_risk['reasons'])
    removed_reasons = set(old_risk['reasons']) - set(new_risk['reasons'])
    
    trace_parts = []
    if new_risk['risk_level'] != old_risk['risk_level']:
        trace_parts.append(f"Risk {old_risk['risk_level']} → {new_risk['risk_level']}")
    
    # Explicitly show score change if it exists
    if new_risk['total_score'] != old_risk['total_score']:
        trace_parts.append(f"Score {old_risk['total_score']} → {new_risk['total_score']}")

    if added_reasons:
        trace_parts.append(f"Added: {', '.join(added_reasons)}")
    if removed_reasons:
        trace_parts.append(f"Removed: {', '.join(removed_reasons)}")
        
    risk_trace = " | ".join(trace_parts) if trace_parts else "No significant risk factor changes"

    # Update patient risk level/score
    patient.risk_score = new_risk['total_score']
    patient.risk_level = new_risk['risk_level']
    patient.save()

    # Log changes
    import uuid
    batch_id = uuid.uuid4()

    def format_val(v):
        if isinstance(v, list):
            return ", ".join(v) if v else "None"
        return str(v)

    for change in changed_fields:
        AuditLog.objects.create(
            patient=patient,
            field_name=change['field'].replace('_', ' ').title(),
            old_value=format_val(change['old']),
            new_value=format_val(change['new']),
            risk_before=old_risk['risk_level'],
            risk_after=new_risk['risk_level'],
            score_before=old_risk['total_score'],
            score_after=new_risk['total_score'],
            reason=risk_trace,
            batch_id=batch_id
        )

    return patient

def create_patient_with_risk(data):
    """
    Creates a new patient and calculates initial risk.
    """
    risk_result = calculate_risk(data)
    
    # Remove risk fields from data if they exist to avoid clashes, 
    # though they shouldn't be in form data usually.
    
    patient = Patient(**data)
    patient.risk_score = risk_result['total_score']
    patient.risk_level = risk_result['risk_level']
    patient.save()

    # Log creation
    AuditLog.objects.create(
        patient=patient,
        field_name="Patient Record",
        old_value="-",
        new_value="Created",
        risk_before="-",
        risk_after=risk_result['risk_level'],
        score_before=0,
        score_after=risk_result['total_score'],
        reason="Initial Patient Registration"
    )
    
    return patient
