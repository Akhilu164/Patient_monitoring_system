from django import forms
from .models import Patient

class PatientForm(forms.ModelForm):
    pdf_file = forms.FileField(required=False, label="Upload Medical Record (PDF)", help_text="Autofill vitals from PDF")
    
    chronic_conditions = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 3, 'placeholder': 'Enter conditions separated by commas e.g. Diabetes, Hypertension', 'class': 'form-control'}),
        required=False,
        help_text="Enter conditions separated by commas"
    )
    
    notes = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 4, 'placeholder': 'Enter clinical observations or notes...', 'class': 'form-control'}),
        required=False,
        label="Clinical Notes"
    )

    class Meta:
        model = Patient
        exclude = ['risk_score', 'risk_level', 'created_at', 'updated_at']
        widgets = {
            'admission_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Pre-fill chronic conditions as comma-separated string if instance exists
        if self.instance and self.instance.pk and self.instance.chronic_conditions:
            if isinstance(self.instance.chronic_conditions, list):
                self.fields['chronic_conditions'].initial = ", ".join(self.instance.chronic_conditions)

        for field in self.fields:
            if field not in ['wbc_flag', 'creatinine_flag', 'crp_flag']:
                self.fields[field].widget.attrs.update({'class': 'form-control'})
            else:
                 self.fields[field].widget.attrs.update({'class': 'form-check-input'})

    def clean_chronic_conditions(self):
        data = self.cleaned_data['chronic_conditions']
        if data:
            import re
            # Split by comma, semicolon, or newline
            return [x.strip() for x in re.split(r'[,\n;]+', data) if x.strip()]
        return []
