from typing import Dict, Any, List

def calculate_risk(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Calculates patient risk score based on demographics, vitals, and clinical history.
    
    Args:
        data: Dictionary containing patient data
        
    Returns:
        Dictionary with total_score, risk_level, escalation_flag, and reasons.
    """
    score = 0
    reasons: List[str] = []
    escalation_flag = False

    # Extract data with safe defaults
    age = data.get('age', 0)
    heart_rate = data.get('heart_rate', 0)
    systolic_bp = data.get('systolic_bp', 0)
    spo2 = data.get('spo2', 100)
    temperature = data.get('temperature', 37.0)
    respiratory_rate = data.get('respiratory_rate', 0)
    chronic_conditions = data.get('chronic_conditions', [])
    er_visits = data.get('er_visits', 0)
    
    # Lab indicators - assume passed as boolean flags or count
    lab_issue_count = sum([
        1 for k in ['wbc_flag', 'creatinine_flag', 'crp_flag'] 
        if data.get(k, False)
    ])

    # --- 1. Demographics ---
    if 60 <= age <= 75:
        score += 1
        reasons.append("Age 60-75 (+1)")
    elif age > 75:
        score += 2
        reasons.append("Age >75 (+2)")

    # --- 2. Vitals ---
    # Heart Rate
    if 100 <= heart_rate <= 120:
        score += 1
        reasons.append("HR 100-120 (+1)")
    elif heart_rate > 120:
        score += 2
        reasons.append("HR >120 (+2)")

    # Systolic BP
    if systolic_bp < 90:
        score += 2
        reasons.append("Systolic BP <90 (+2)")

    # SpO2
    if 90 <= spo2 <= 93:
        score += 1
        reasons.append("SpO2 90-93 (+1)")
    elif spo2 < 90:
        score += 2
        reasons.append("SpO2 <90 (+2)")

    # Temperature
    if 38 <= temperature <= 39:
        score += 1
        reasons.append("Temp 38-39 (+1)")
    elif temperature > 39:
        score += 2
        reasons.append("Temp >39 (+2)")

    # Respiratory Rate
    if respiratory_rate > 24:
        score += 1
        reasons.append("Resp Rate >24 (+1)")

    # --- 3. Clinical History ---
    # Specific Chronic Conditions: Diabetes, COPD, Cardiac (+1 each)
    target_conditions = ["diabetes", "copd", "cardiac"]
    if chronic_conditions:
        for condition in chronic_conditions:
            clean_condition = str(condition).strip().lower()
            if any(target in clean_condition for target in target_conditions):
                score += 1
                reasons.append(f"Chronic Condition: {condition} (+1)")

    # ER Visits (Last 30 days)
    if 2 <= er_visits <= 3:
        score += 1
        reasons.append("ER Visits 2-3 (+1)")
    elif er_visits > 3:
        score += 2
        reasons.append("ER Visits >3 (+2)")

    # --- 4. Lab Indicators ---
    # Elevated WBC, High Creatinine, or High CRP (+1 each)
    if data.get('wbc_flag', False):
        score += 1
        reasons.append("Elevated WBC (+1)")
    if data.get('creatinine_flag', False):
        score += 1
        reasons.append("High Creatinine (+1)")
    if data.get('crp_flag', False):
        score += 1
        reasons.append("High CRP (+1)")

    # --- 5. Risk Classification ---
    if score >= 6:
        risk_level = "HIGH"
    elif score >= 3:
        risk_level = "MEDIUM"
    else:
        risk_level = "LOW"

    return {
        "total_score": score,
        "risk_level": risk_level,
        "escalation_flag": escalation_flag,
        "reasons": reasons
    }
