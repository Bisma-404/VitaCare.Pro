"""
OCR utilities for extracting medical data from images.
This module handles image processing and text extraction for medical reports.
"""

import re
import pytesseract
from PIL import Image
import os

# ==============================
# ✅ Configure Tesseract Path
# ==============================
CUSTOM_TESSERACT_PATH = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

if os.path.exists(CUSTOM_TESSERACT_PATH):
    pytesseract.pytesseract.tesseract_cmd = CUSTOM_TESSERACT_PATH
    print(f"✅ Tesseract path set to: {CUSTOM_TESSERACT_PATH}")
else:
    print(f"⚠️ Warning: Tesseract not found at {CUSTOM_TESSERACT_PATH}")
    print("Attempting to use Tesseract from system PATH...")
    # Let pytesseract try to find tesseract in system PATH
    # If not found, it will raise TesseractNotFoundError when actually used


class OCRParser:
    """
    Parser for extracting medical data from images using OCR.
    Supports diabetes, heart disease, and breast cancer reports.
    """

    def __init__(self):
        """Initialize OCR parser with field patterns."""
        self.patterns = self._init_patterns()

    def _init_patterns(self):
        """Initialize regex patterns for extracting medical values."""
        return {
            'diabetes': {
                'pregnancies': [
                    r'pregnanc(?:ies|y)[\s:]+(\d+)',
                    r'number\s+of\s+pregnanc(?:ies|y)[\s:]+(\d+)',
                ],
                'glucose': [
                    r'glucose[\s:]+(\d+\.?\d*)',
                    r'fasting\s+glucose[\s:]+(\d+\.?\d*)',
                    r'blood\s+glucose[\s:]+(\d+\.?\d*)',
                    r'sugar[\s:]+(\d+\.?\d*)',
                ],
                'blood_pressure': [
                    r'blood\s+pressure[\s:]+(\d+\.?\d*)',
                    r'bp[\s:]+(\d+\.?\d*)',
                    r'systolic[\s:]+(\d+\.?\d*)',
                ],
                'skin_thickness': [
                    r'skin\s+thickness[\s:]+(\d+\.?\d*)',
                    r'triceps[\s:]+(\d+\.?\d*)',
                ],
                'insulin': [
                    r'insulin[\s:]+(\d+\.?\d*)',
                    r'serum\s+insulin[\s:]+(\d+\.?\d*)',
                ],
                'bmi': [
                    r'bmi[\s:]+(\d+\.?\d*)',
                    r'body\s+mass\s+index[\s:]+(\d+\.?\d*)',
                ],
                'dpf': [
                    r'diabetes\s+pedigree[\s:]+(\d+\.?\d*)',
                    r'dpf[\s:]+(\d+\.?\d*)',
                    r'pedigree[\s:]+(\d+\.?\d*)',
                ],
                'age': [
                    r'age[\s:]+(\d+)',
                    r'patient\s+age[\s:]+(\d+)',
                ],
            },
            'heart': {
                'age': [r'age[\s:]+(\d+)', r'patient\s+age[\s:]+(\d+)'],
                'sex': [r'sex[\s:]+(\w+)', r'gender[\s:]+(\w+)'],
                'cp': [r'chest\s+pain[\s:]+(\d+)', r'cp\s+type[\s:]+(\d+)', r'angina\s+type[\s:]+(\d+)'],
                'trestbps': [
                    r'resting\s+blood\s+pressure[\s:]+(\d+\.?\d*)',
                    r'rest\s+bp[\s:]+(\d+\.?\d*)',
                    r'blood\s+pressure[\s:]+(\d+\.?\d*)',
                ],
                'chol': [
                    r'cholesterol[\s:]+(\d+\.?\d*)',
                    r'serum\s+cholesterol[\s:]+(\d+\.?\d*)',
                    r'chol[\s:]+(\d+\.?\d*)',
                ],
                'fbs': [r'fasting\s+blood\s+sugar[\s:]+(\d+)', r'fbs[\s:]+(\d+)'],
                'restecg': [r'resting\s+ecg[\s:]+(\d+)', r'rest\s+ecg[\s:]+(\d+)', r'ecg[\s:]+(\d+)'],
                'thalach': [
                    r'max(?:imum)?\s+heart\s+rate[\s:]+(\d+\.?\d*)',
                    r'thalach[\s:]+(\d+\.?\d*)',
                    r'max\s+hr[\s:]+(\d+\.?\d*)',
                ],
                'exang': [r'exercise\s+induced\s+angina[\s:]+(\d+)', r'exang[\s:]+(\d+)'],
                'oldpeak': [r'oldpeak[\s:]+(\d+\.?\d*)', r'st\s+depression[\s:]+(\d+\.?\d*)'],
                'slope': [r'slope[\s:]+(\d+)', r'st\s+slope[\s:]+(\d+)'],
                'ca': [r'major\s+vessels[\s:]+(\d+)', r'ca[\s:]+(\d+)', r'vessels[\s:]+(\d+)'],
                'thal': [r'thalassemia[\s:]+(\d+)', r'thal[\s:]+(\d+)'],
            },
            'breast_cancer': {
                'radius_mean': [r'radius\s+mean[\s:]+(\d+\.?\d*)', r'mean\s+radius[\s:]+(\d+\.?\d*)'],
                'texture_mean': [r'texture\s+mean[\s:]+(\d+\.?\d*)', r'mean\s+texture[\s:]+(\d+\.?\d*)'],
                'perimeter_mean': [r'perimeter\s+mean[\s:]+(\d+\.?\d*)', r'mean\s+perimeter[\s:]+(\d+\.?\d*)'],
                'area_mean': [r'area\s+mean[\s:]+(\d+\.?\d*)', r'mean\s+area[\s:]+(\d+\.?\d*)'],
                'smoothness_mean': [r'smoothness\s+mean[\s:]+(\d+\.?\d*)', r'mean\s+smoothness[\s:]+(\d+\.?\d*)'],
                'compactness_mean': [r'compactness\s+mean[\s:]+(\d+\.?\d*)', r'mean\s+compactness[\s:]+(\d+\.?\d*)'],
                'concavity_mean': [r'concavity\s+mean[\s:]+(\d+\.?\d*)', r'mean\s+concavity[\s:]+(\d+\.?\d*)'],
                'concave_points_mean': [
                    r'concave\s+points\s+mean[\s:]+(\d+\.?\d*)',
                    r'mean\s+concave\s+points[\s:]+(\d+\.?\d*)',
                ],
                'symmetry_mean': [r'symmetry\s+mean[\s:]+(\d+\.?\d*)', r'mean\s+symmetry[\s:]+(\d+\.?\d*)'],
                'fractal_dimension_mean': [
                    r'fractal\s+dimension\s+mean[\s:]+(\d+\.?\d*)',
                    r'mean\s+fractal\s+dimension[\s:]+(\d+\.?\d*)',
                ],
            },
        }

    def extract_text(self, image_path):
        """Extract text from an image using Tesseract OCR."""
        try:
            img = Image.open(image_path)
            img = img.convert("L")  # grayscale
            text = pytesseract.image_to_string(img)
            return text
        except Exception as e:
            raise Exception(f"OCR extraction failed: {str(e)}")

    def parse_value(self, text, patterns):
        """Parse a single value from text using regex patterns."""
        text_lower = text.lower()
        for pattern in patterns:
            match = re.search(pattern, text_lower, re.IGNORECASE)
            if match:
                value_str = match.group(1)
                if value_str.lower() in ["male", "m"]:
                    return 1
                elif value_str.lower() in ["female", "f"]:
                    return 0
                try:
                    return float(value_str)
                except ValueError:
                    continue
        return None

    def parse_report(self, image_path, disease_type):
        """Parse a medical report image and extract relevant fields."""
        raw_text = self.extract_text(image_path)
        if disease_type not in self.patterns:
            raise ValueError(f"Unknown disease type: {disease_type}")
        field_patterns = self.patterns[disease_type]
        parsed_data = {}
        for field_name, patterns in field_patterns.items():
            value = self.parse_value(raw_text, patterns)
            if value is not None:
                parsed_data[field_name] = value
        return {
            "raw_text": raw_text,
            "parsed_data": parsed_data,
            "fields_found": len(parsed_data),
        }


def get_default_values(disease_type):
    """Get default values for fields not found by OCR."""
    defaults = {
        "diabetes": {
            "pregnancies": 0,
            "glucose": 100,
            "blood_pressure": 80,
            "skin_thickness": 20,
            "insulin": 0,
            "bmi": 25.0,
            "dpf": 0.5,
            "age": 30,
        },
        "heart": {
            "age": 50,
            "sex": 1,
            "cp": 0,
            "trestbps": 120,
            "chol": 200,
            "fbs": 0,
            "restecg": 0,
            "thalach": 150,
            "exang": 0,
            "oldpeak": 0.0,
            "slope": 0,
            "ca": 0,
            "thal": 2,
        },
        "breast_cancer": {
            "radius_mean": 14.0,
            "texture_mean": 19.0,
            "perimeter_mean": 92.0,
            "area_mean": 655.0,
            "smoothness_mean": 0.096,
            "compactness_mean": 0.104,
            "concavity_mean": 0.089,
            "concave_points_mean": 0.048,
            "symmetry_mean": 0.181,
            "fractal_dimension_mean": 0.063,
        },
    }
    return defaults.get(disease_type, {})
