"""
Mapping between user-friendly form fields and dataset features.
"""

# Dataset column mappings
DIABETES_COLUMNS = [
    'Pregnancies', 'Glucose', 'BloodPressure', 'SkinThickness',
    'Insulin', 'BMI', 'DiabetesPedigreeFunction', 'Age'
]

HEART_COLUMNS = [
    'age', 'sex', 'cp', 'trestbps', 'chol', 'fbs', 'restecg',
    'thalach', 'exang', 'oldpeak', 'slope', 'ca', 'thal'
]

BREAST_CANCER_COLUMNS = [
    'radius_mean', 'texture_mean', 'perimeter_mean', 'area_mean',
    'smoothness_mean', 'compactness_mean', 'concavity_mean',
    'concave points_mean', 'symmetry_mean', 'fractal_dimension_mean'
]

# User-friendly form field definitions
DIABETES_FIELDS = [
    {'name': 'pregnancies', 'label': 'Number of Pregnancies', 'type': 'number', 'min': 0, 'max': 20, 'default': 0},
    {'name': 'glucose', 'label': 'Fasting Glucose Level (mg/dL)', 'type': 'number', 'min': 0, 'max': 300, 'default': 100},
    {'name': 'blood_pressure', 'label': 'Blood Pressure (mm Hg)', 'type': 'number', 'min': 0, 'max': 200, 'default': 80},
    {'name': 'skin_thickness', 'label': 'Skin Thickness (mm)', 'type': 'number', 'min': 0, 'max': 100, 'default': 20},
    {'name': 'insulin', 'label': 'Insulin Level (µU/mL)', 'type': 'number', 'min': 0, 'max': 900, 'default': 0},
    {'name': 'bmi', 'label': 'Body Mass Index (BMI)', 'type': 'number', 'step': 0.1, 'min': 10, 'max': 70, 'default': 25},
    {'name': 'dpf', 'label': 'Diabetes Pedigree Function', 'type': 'number', 'step': 0.001, 'min': 0, 'max': 3, 'default': 0.5},
    {'name': 'age', 'label': 'Age (years)', 'type': 'number', 'min': 1, 'max': 120, 'default': 30}
]

HEART_FIELDS = [
    {'name': 'age', 'label': 'Age (years)', 'type': 'number', 'min': 1, 'max': 120, 'default': 50},
    {'name': 'sex', 'label': 'Sex', 'type': 'select', 'options': [('0', 'Female'), ('1', 'Male')], 'default': '1'},
    {'name': 'cp', 'label': 'Chest Pain Type', 'type': 'select', 
     'options': [('0', 'Typical Angina'), ('1', 'Atypical Angina'), ('2', 'Non-anginal Pain'), ('3', 'Asymptomatic')], 
     'default': '0'},
    {'name': 'trestbps', 'label': 'Resting Blood Pressure (mm Hg)', 'type': 'number', 'min': 80, 'max': 200, 'default': 120},
    {'name': 'chol', 'label': 'Serum Cholesterol (mg/dL)', 'type': 'number', 'min': 100, 'max': 600, 'default': 200},
    {'name': 'fbs', 'label': 'Fasting Blood Sugar > 120 mg/dL', 'type': 'select', 
     'options': [('0', 'No'), ('1', 'Yes')], 'default': '0'},
    {'name': 'restecg', 'label': 'Resting ECG Results', 'type': 'select',
     'options': [('0', 'Normal'), ('1', 'ST-T Wave Abnormality'), ('2', 'Left Ventricular Hypertrophy')],
     'default': '0'},
    {'name': 'thalach', 'label': 'Maximum Heart Rate Achieved', 'type': 'number', 'min': 60, 'max': 220, 'default': 150},
    {'name': 'exang', 'label': 'Exercise Induced Angina', 'type': 'select',
     'options': [('0', 'No'), ('1', 'Yes')], 'default': '0'},
    {'name': 'oldpeak', 'label': 'ST Depression (oldpeak)', 'type': 'number', 'step': 0.1, 'min': 0, 'max': 10, 'default': 0},
    {'name': 'slope', 'label': 'Slope of Peak Exercise ST Segment', 'type': 'select',
     'options': [('0', 'Upsloping'), ('1', 'Flat'), ('2', 'Downsloping')], 'default': '0'},
    {'name': 'ca', 'label': 'Number of Major Vessels (0-4)', 'type': 'number', 'min': 0, 'max': 4, 'default': 0},
    {'name': 'thal', 'label': 'Thalassemia', 'type': 'select',
     'options': [('1', 'Normal'), ('2', 'Fixed Defect'), ('3', 'Reversible Defect')], 'default': '2'}
]

BREAST_CANCER_FIELDS = [
    {'name': 'radius_mean', 'label': 'Mean Radius (mm)', 'type': 'number', 'step': 0.1, 'min': 5, 'max': 30, 'default': 14},
    {'name': 'texture_mean', 'label': 'Mean Texture', 'type': 'number', 'step': 0.1, 'min': 5, 'max': 40, 'default': 19},
    {'name': 'perimeter_mean', 'label': 'Mean Perimeter (mm)', 'type': 'number', 'step': 0.1, 'min': 40, 'max': 200, 'default': 92},
    {'name': 'area_mean', 'label': 'Mean Area (mm²)', 'type': 'number', 'step': 1, 'min': 100, 'max': 2500, 'default': 655},
    {'name': 'smoothness_mean', 'label': 'Mean Smoothness', 'type': 'number', 'step': 0.001, 'min': 0.05, 'max': 0.2, 'default': 0.096},
    {'name': 'compactness_mean', 'label': 'Mean Compactness', 'type': 'number', 'step': 0.001, 'min': 0.01, 'max': 0.4, 'default': 0.104},
    {'name': 'concavity_mean', 'label': 'Mean Concavity', 'type': 'number', 'step': 0.001, 'min': 0, 'max': 0.5, 'default': 0.089},
    {'name': 'concave_points_mean', 'label': 'Mean Concave Points', 'type': 'number', 'step': 0.001, 'min': 0, 'max': 0.3, 'default': 0.048},
    {'name': 'symmetry_mean', 'label': 'Mean Symmetry', 'type': 'number', 'step': 0.001, 'min': 0.1, 'max': 0.4, 'default': 0.181},
    {'name': 'fractal_dimension_mean', 'label': 'Mean Fractal Dimension', 'type': 'number', 'step': 0.001, 'min': 0.04, 'max': 0.1, 'default': 0.063}
]

DISEASE_CONFIG = {
    'diabetes': {
        'name': 'Diabetes',
        'description': 'Predicts risk of diabetes based on medical indicators',
        'fields': DIABETES_FIELDS,
        'columns': DIABETES_COLUMNS,
        'outcome_labels': {0: 'Low Risk', 1: 'High Risk'},
        'dataset': 'diabetes.csv',
        'target_column': 'Outcome'
    },
    'heart': {
        'name': 'Heart Disease',
        'description': 'Predicts presence of heart disease based on cardiac health indicators',
        'fields': HEART_FIELDS,
        'columns': HEART_COLUMNS,
        'outcome_labels': {0: 'Disease Present', 1: 'No Disease'},
        'dataset': 'heart.csv',
        'target_column': 'target'
    },
    'breast_cancer': {
        'name': 'Breast Cancer',
        'description': 'Predicts malignancy based on cell nucleus characteristics',
        'fields': BREAST_CANCER_FIELDS,
        'columns': BREAST_CANCER_COLUMNS,
        'outcome_labels': {0: 'Benign', 1: 'Malignant'},
        'dataset': 'breast_cancer.csv',
        'target_column': 'diagnosis',
        'target_mapping': {'M': 1, 'B': 0}  # M=Malignant, B=Benign
    }
}

def get_disease_config(disease_type):
    """Get configuration for a specific disease type."""
    return DISEASE_CONFIG.get(disease_type)

def extract_features_from_form(form_data, disease_type):
    """Extract and order features from form data according to dataset column order."""
    config = get_disease_config(disease_type)
    if not config:
        raise ValueError(f"Unknown disease type: {disease_type}")
    
    features = []
    for field in config['fields']:
        field_name = field['name']
        value = form_data.get(field_name, field.get('default', 0))
        
        # Convert to appropriate type
        if field['type'] == 'number':
            features.append(float(value))
        elif field['type'] == 'select':
            features.append(float(value))
    
    return features