"""
Medical data mappings for disease prediction system.
Contains parameter aliases, symptom-disease relationships, and normal ranges.
"""

# Parameter name aliases - maps common variations to standard names
parameter_aliases = {
    "hb": "hemoglobin",
    "hgb": "hemoglobin",
    "blood sugar": "glucose",
    "blood glucose": "glucose",
    "fasting glucose": "glucose",
    "sugar": "glucose",
    "chol": "cholesterol",
    "total cholesterol": "cholesterol",
    "serum cholesterol": "cholesterol",
    "bp": "blood_pressure",
    "blood pressure": "blood_pressure",
    "systolic": "blood_pressure",
    "resting bp": "blood_pressure",
    "trestbps": "blood_pressure",
    "bmi": "bmi",
    "body mass index": "bmi",
    "age": "age",
    "patient age": "age",
    "pregnancies": "pregnancies",
    "pregnancy": "pregnancies",
    "insulin": "insulin",
    "serum insulin": "insulin",
    "skin thickness": "skin_thickness",
    "triceps": "skin_thickness",
    "dpf": "dpf",
    "diabetes pedigree": "dpf",
    "pedigree function": "dpf",
    "chest pain": "cp",
    "cp": "cp",
    "angina": "cp",
    "sex": "sex",
    "gender": "sex",
    "fbs": "fbs",
    "fasting blood sugar": "fbs",
    "restecg": "restecg",
    "resting ecg": "restecg",
    "ecg": "restecg",
    "thalach": "thalach",
    "max heart rate": "thalach",
    "heart rate": "thalach",
    "exang": "exang",
    "exercise angina": "exang",
    "oldpeak": "oldpeak",
    "st depression": "oldpeak",
    "slope": "slope",
    "st slope": "slope",
    "ca": "ca",
    "vessels": "ca",
    "major vessels": "ca",
    "thal": "thal",
    "thalassemia": "thal",
    "radius": "radius_mean",
    "radius mean": "radius_mean",
    "texture": "texture_mean",
    "texture mean": "texture_mean",
    "perimeter": "perimeter_mean",
    "perimeter mean": "perimeter_mean",
    "area": "area_mean",
    "area mean": "area_mean",
    "smoothness": "smoothness_mean",
    "smoothness mean": "smoothness_mean",
    "compactness": "compactness_mean",
    "compactness mean": "compactness_mean",
    "concavity": "concavity_mean",
    "concavity mean": "concavity_mean",
    "concave points": "concave_points_mean",
    "concave points mean": "concave_points_mean",
    "symmetry": "symmetry_mean",
    "symmetry mean": "symmetry_mean",
    "fractal dimension": "fractal_dimension_mean",
    "fractal dimension mean": "fractal_dimension_mean",
}

# Symptom to disease mapping
symptom_disease_map = {
    "chest pain": ["heart"],
    "chest discomfort": ["heart"],
    "angina": ["heart"],
    "shortness of breath": ["heart", "diabetes"],
    "breathlessness": ["heart", "diabetes"],
    "fatigue": ["heart", "diabetes", "breast_cancer"],
    "tiredness": ["heart", "diabetes", "breast_cancer"],
    "blurred vision": ["diabetes"],
    "vision problems": ["diabetes"],
    "frequent urination": ["diabetes"],
    "excessive urination": ["diabetes"],
    "polyuria": ["diabetes"],
    "dizziness": ["heart", "diabetes"],
    "lightheadedness": ["heart", "diabetes"],
    "nausea": ["heart", "diabetes", "breast_cancer"],
    "weight changes": ["diabetes", "breast_cancer"],
    "weight loss": ["diabetes", "breast_cancer"],
    "weight gain": ["diabetes"],
    "unexplained weight loss": ["diabetes", "breast_cancer"],
    "breast lump": ["breast_cancer"],
    "breast changes": ["breast_cancer"],
    "breast pain": ["breast_cancer"],
    "skin changes": ["breast_cancer"],
    "nipple discharge": ["breast_cancer"],
}

# Normal ranges for medical parameters
normal_ranges = {
    "glucose": (70, 140),  # mg/dL (fasting)
    "cholesterol": (125, 200),  # mg/dL
    "hemoglobin": (12, 16),  # g/dL (varies by sex, using general range)
    "blood_pressure": (90, 140),  # mm Hg (systolic)
    "bmi": (18.5, 24.9),  # kg/m²
    "age": (0, 120),  # years (no abnormal range, just for reference)
    "pregnancies": (0, 20),  # count
    "insulin": (0, 25),  # µU/mL (fasting)
    "skin_thickness": (10, 50),  # mm
    "dpf": (0, 2.5),  # diabetes pedigree function
    "cp": (0, 3),  # chest pain type (categorical)
    "sex": (0, 1),  # 0=female, 1=male
    "fbs": (0, 1),  # 0=no, 1=yes
    "restecg": (0, 2),  # resting ECG (categorical)
    "thalach": (60, 200),  # max heart rate
    "exang": (0, 1),  # exercise angina (0=no, 1=yes)
    "oldpeak": (0, 6),  # ST depression
    "slope": (0, 2),  # ST slope (categorical)
    "ca": (0, 4),  # major vessels (categorical)
    "thal": (1, 3),  # thalassemia (categorical)
    "radius_mean": (5, 25),  # mm
    "texture_mean": (5, 40),  # unitless
    "perimeter_mean": (40, 200),  # mm
    "area_mean": (100, 2500),  # mm²
    "smoothness_mean": (0.05, 0.2),  # unitless
    "compactness_mean": (0.01, 0.4),  # unitless
    "concavity_mean": (0, 0.5),  # unitless
    "concave_points_mean": (0, 0.3),  # unitless
    "symmetry_mean": (0.1, 0.4),  # unitless
    "fractal_dimension_mean": (0.04, 0.1),  # unitless
}

def normalize_parameter_name(param_name):
    """
    Normalize parameter name using aliases.
    Returns standardized parameter name or original if not found.
    """
    param_lower = param_name.lower().strip()
    return parameter_aliases.get(param_lower, param_lower)

def get_diseases_for_symptom(symptom):
    """
    Get list of diseases associated with a symptom.
    Returns empty list if symptom not found.
    """
    symptom_lower = symptom.lower().strip()
    return symptom_disease_map.get(symptom_lower, [])

def is_parameter_normal(param_name, value):
    """
    Check if parameter value is within normal range.
    Returns (is_normal, range_tuple) where range_tuple is (min, max).
    """
    normalized_name = normalize_parameter_name(param_name)
    if normalized_name in normal_ranges:
        min_val, max_val = normal_ranges[normalized_name]
        is_normal = min_val <= value <= max_val
        return is_normal, (min_val, max_val)
    return None, None

def calculate_risk_score(prediction, confidence_factors=None):
    """
    Calculate risk score for a disease prediction.
    prediction: 0 (low risk) or 1 (high risk)
    confidence_factors: dict of additional factors affecting risk
    Returns risk score (0-100, higher = more risk)
    """
    base_score = 50 if prediction == 1 else 20
    
    if confidence_factors:
        # Adjust based on confidence factors
        if confidence_factors.get('symptom_match', False):
            base_score += 15
        if confidence_factors.get('abnormal_values', False):
            base_score += 10
        if confidence_factors.get('trend_worsening', False):
            base_score += 15
    
    return min(100, max(0, base_score))

