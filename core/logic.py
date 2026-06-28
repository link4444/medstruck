def evaluate_metric_risk(metric_name: str, value: float) -> str:
    """
    Evaluates a single clinical lab metric and returns a risk category:
    'Normal', 'Elevated', 'High', or 'Unknown'.
    Uses standard clinical threshold approximations.
    """
    metric_name = metric_name.lower().strip()
    
    # Blood Glucose (Fasting)
    if "glucose" in metric_name or "fasting blood sugar" in metric_name:
        if value < 100:
            return "Normal"
        elif 100 <= value < 126:
            return "Elevated (Prediabetes)"
        else:
            return "High (Diabetes Risk)"
            
    # Blood Pressure - Systolic
    if "systolic" in metric_name:
        if value < 120:
            return "Normal"
        elif 120 <= value < 130:
            return "Elevated"
        elif 130 <= value < 140:
            return "High (Stage 1 Hypertension)"
        else:
            return "High (Stage 2 Hypertension)"
            
    # Blood Pressure - Diastolic
    if "diastolic" in metric_name:
        if value < 80:
            return "Normal"
        elif 80 <= value < 90:
            return "High (Stage 1 Hypertension)"
        else:
            return "High (Stage 2 Hypertension)"
            
    # LDL Cholesterol
    if "ldl" in metric_name or "bad cholesterol" in metric_name:
        if value < 100:
            return "Normal"
        elif 100 <= value <= 159:
            return "Elevated (Borderline High)"
        else:
            return "High"

    # HDL Cholesterol (Note: Lower is worse here)
    if "hdl" in metric_name:
        if value >= 60:
            return "Normal (Optimal)"
        elif 40 <= value < 60:
            return "Elevated (Borderline Low)"
        else:
            return "High (Major Risk Factor)"

    return "Unknown"


def compute_overall_risk(metrics: dict) -> str:
    """
    Computes an overall patient risk summary based on a dictionary of metrics.
    Example input: {"Glucose": 110, "Systolic": 135}
    Returns: "Low", "Medium", or "High"
    """
    high_count = 0
    elevated_count = 0
    
    for name, value_str in metrics.items():
        try:
            val = float(value_str)
            risk = evaluate_metric_risk(name, val)
            
            if "High" in risk:
                high_count += 1
            elif "Elevated" in risk:
                elevated_count += 1
        except (ValueError, TypeError):
            # Skip values that cannot be parsed as a float
            continue
            
    if high_count >= 1:
        return "High"
    elif elevated_count >= 1:
        return "Medium"
    else:
        return "Low"

if __name__ == "__main__":
    # Quick Test
    sample_patient = {
        "Glucose": 115,     # Elevated
        "Systolic": 118,    # Normal
        "Diastolic": 75,    # Normal
        "LDL": 165          # High
    }
    
    print("Evaluating Sample Patient Metrics:")
    for metric, val in sample_patient.items():
        print(f"- {metric}: {val} -> {evaluate_metric_risk(metric, val)}")
        
    print(f"\nOverall Patient Risk: {compute_overall_risk(sample_patient)}")
