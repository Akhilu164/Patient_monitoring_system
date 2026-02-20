import PyPDF2
import re
from typing import Dict, Any

def extract_vitals_from_pdf(pdf_file) -> Dict[str, Any]:
    """
    Extracts vitals and patient data from a PDF file stream using regex.
    """
    text = ""
    try:
        reader = PyPDF2.PdfReader(pdf_file)
        for page in reader.pages:
            text += page.extract_text() or ""
        text += "\n" 
        print(f"DEBUG PDF RAW TEXT:\n{text}\nEND DEBUG")
    except Exception as e:
        print(f"Error reading PDF: {e}")
        return {}

    data = {}
    text_lower = text.lower()

    # --- Regex Patterns ---
    patterns = {
        # Vitals: Case insensitive, handles "HR: 110" or "HR 110"
        'heart_rate': r'(?:heart rate|hr|pulse)\s*[:=\s]+\s*(\d{2,3})',
        'systolic_bp': r'(?:systolic bp|bp|blood pressure|b\.p\.)\s*[:=\s]+\s*(\d{2,3})(?:/\d{2,3})?', 
        'spo2': r'(?:spo2|oxygen|saturation|o2 sat)\s*[:=\s]+\s*(\d{2,3})',
        'temperature': r'(?:temperature|temp|\bT)\s*[:=\s]+\s*(\d{2,3}(?:[\.,]\d)?)',
        'respiratory_rate': r'(?:respiratory rate|resp rate|rr)\s*[:=\s]+\s*(\d{1,2})',
        
        # Demographics
        'age': r'(?:age|y/o|years old)\s*[:=\s]+\s*(\d{1,3})',
        'full_name': r'(?:patient name|name|patient)\s*[:=]\s*([a-zA-Z \t\.]+)',
        'gender': r'(?:gender|sex)\s*[:=\s]+\s*(male|female|other|m|f)',
        'admission_date': r'(?:admission date|date|admitted)\s*[:=\s]+\s*(\d{4}-\d{2}-\d{2}|\d{2}/\d{2}/\d{4}|\d{2}\.\d{2}\.\d{4})'
    }

    for field, pattern in patterns.items():
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            value = match.group(1).strip()
            # Type Conversions
            if field in ['heart_rate', 'systolic_bp', 'spo2', 'respiratory_rate', 'age']:
                try: data[field] = int(value)
                except: pass
            elif field == 'temperature':
                try: 
                    # Handle comma decimal separator
                    value = value.replace(',', '.')
                    data[field] = float(value)
                except: pass
            elif field == 'gender':
                val = value.lower()
                if val in ['m', 'male']: data[field] = 'Male'
                elif val in ['f', 'female']: data[field] = 'Female'
                else: data[field] = 'Other'
            elif field == 'admission_date':
                from datetime import datetime
                # Try parsing YYYY-MM-DD, DD/MM/YYYY, MM/DD/YYYY, DD.MM.YYYY
                formats = ('%Y-%m-%d', '%d/%m/%Y', '%m/%d/%Y', '%d.%m.%Y')
                for fmt in formats:
                    try:
                        dt = datetime.strptime(value, fmt)
                        # Create standard date string for Django form (YYYY-MM-DD usually, 
                        # but depends on widget usually expects standard format)
                        # Actually standard HTML date input expects YYYY-MM-DD
                        data[field] = dt.strftime('%Y-%m-%d')
                        break
                    except ValueError:
                        pass
            else:
                data[field] = value

    # --- Chronic Conditions (Keyword Search) ---
    conditions = []
    condition_keywords = {
        'Diabetes': ['diabetes', 'diabetic'],
        'COPD': ['copd', 'chronic obstructive'],
        'Hypertension': ['hypertension', 'high blood pressure'],
        'Asthma': ['asthma'],
        'Cardiac Disease': ['cardiac', 'heart disease', 'failure']
    }
    
    for condition, keywords in condition_keywords.items():
        if any(k in text_lower for k in keywords):
            conditions.append(condition)
            
    if conditions:
        data['chronic_conditions'] = ", ".join(conditions)

    # --- Lab Indicators ---
    if "elevated wbc" in text_lower or "high wbc" in text_lower: data['wbc_flag'] = True
    if "elevated creatinine" in text_lower or "high creatinine" in text_lower: data['creatinine_flag'] = True
    if "elevated crp" in text_lower or "high crp" in text_lower: data['crp_flag'] = True

    # --- Notes / Observations ---
    # Capture text after "Notes:" or "Observations:" until end or new section
    notes_match = re.search(r'(?:notes|observations|comments)\s*[:=]\s*(.*)', text, re.IGNORECASE | re.DOTALL)
    if notes_match:
        # Take up to 500 chars, stripping whitespace
        data['notes'] = notes_match.group(1).strip()[:500]

    return data
