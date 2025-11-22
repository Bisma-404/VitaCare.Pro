"""
Test Medical Report Image Generator
Creates sample medical report images for testing OCR functionality.
"""
from PIL import Image, ImageDraw, ImageFont
import os

# Try to use a better font if available, otherwise use default
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    font_title = ImageFont.truetype("arial.ttf", 24)
    font_large = ImageFont.truetype("arial.ttf", 20)
    font_normal = ImageFont.truetype("arial.ttf", 16)
    logger.info("Successfully loaded TrueType fonts")
except Exception as e:
    logger.warning(f"Could not load TrueType fonts ({e}). Using default font.")
    font_title = ImageFont.load_default()
    font_large = ImageFont.load_default()
    font_normal = ImageFont.load_default()


def create_medical_report(filename, title, data, output_dir='test_images'):
    """
    Create a medical report image for OCR testing.
    
    Args:
        filename: Output filename
        title: Report title
        data: Dictionary of field:value pairs
        output_dir: Output directory
    """
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Calculate image height based on number of fields
    height = 150 + (len(data) * 50)
    img = Image.new('RGB', (800, height), color='white')
    draw = ImageDraw.Draw(img)
    
    # Draw title
    draw.text((50, 30), title, fill='black', font=font_title)
    draw.line([(50, 70), (750, 70)], fill='black', width=2)
    
    # Draw data fields
    y = 100
    for key, value in data.items():
        text = f"{key}: {value}"
        draw.text((80, y), text, fill='black', font=font_large)
        y += 45
    
    # Draw footer
    draw.text((50, height - 40), "For Testing Purposes Only", fill='gray', font=font_normal)
    
    # Save image
    filepath = os.path.join(output_dir, filename)
    img.save(filepath)
    print(f"Created: {filepath}")
    return filepath


def generate_all_test_images():
    """Generate test images for all disease types."""
    
    # Diabetes test data
    diabetes_data = {
        'Pregnancies': 2,
        'Glucose': 148,
        'Blood Pressure': 85,
        'Skin Thickness': 25,
        'Insulin': 95,
        'BMI': 28.5,
        'Diabetes Pedigree Function': 0.627,
        'Age': 45
    }
    create_medical_report(
        'diabetes_report_test.png',
        'DIABETES SCREENING REPORT',
        diabetes_data
    )
    
    # Heart disease test data
    heart_data = {
        'Age': 63,
        'Sex': 1,
        'Chest Pain Type': 3,
        'Resting Blood Pressure': 145,
        'Cholesterol': 233,
        'Fasting Blood Sugar': 1,
        'Resting ECG': 0,
        'Maximum Heart Rate': 150,
        'Exercise Induced Angina': 0,
        'Oldpeak': 2.3,
        'Slope': 0,
        'Major Vessels': 0,
        'Thalassemia': 1
    }
    create_medical_report(
        'heart_report_test.png',
        'CARDIAC HEALTH ASSESSMENT',
        heart_data
    )
    
    # Breast cancer test data
    breast_cancer_data = {
        'Mean Radius': 17.99,
        'Mean Texture': 10.38,
        'Mean Perimeter': 122.8,
        'Mean Area': 1001,
        'Mean Smoothness': 0.1184,
        'Mean Compactness': 0.2776,
        'Mean Concavity': 0.3001,
        'Mean Concave Points': 0.1471,
        'Mean Symmetry': 0.2419,
        'Mean Fractal Dimension': 0.07871
    }
    create_medical_report(
        'breast_cancer_report_test.png',
        'CELL CHARACTERISTICS ANALYSIS',
        breast_cancer_data
    )
    
    # Create a noisy version for testing OCR robustness
    print("\n" + "="*50)
    print("Creating challenging test images...")
    print("="*50)
    
    # Create image with some OCR challenges
    challenging_diabetes_data = {
        'Pregnancies': 3,
        'glucose': 160,  # lowercase
        'BLOOD PRESSURE': 90,  # uppercase
        'Skin  Thickness': 30,  # extra space
        'Insulin': 110,
        'bmi': 32.1,  # lowercase
        'dpf': 0.742,  # abbreviated
        'Age': 52
    }
    create_medical_report(
        'diabetes_report_challenging.png',
        'DIABETES TEST - CHALLENGING FORMAT',
        challenging_diabetes_data
    )
    
    print("\n" + "="*50)
    print("Test image generation complete!")
    print("="*50)
    print(f"\nGenerated images in: {os.path.abspath('test_images')}")
    print("\nYou can now test OCR by uploading these images through the web interface.")


if __name__ == '__main__':
    print("="*50)
    print("Medical Report Test Image Generator")
    print("="*50)
    print("This script creates sample medical report images")
    print("for testing the OCR functionality.\n")
    
    generate_all_test_images()
    
    print("\n" + "="*50)
    print("Usage Instructions:")
    print("="*50)
    print("1. Start the Flask application: python app.py")
    print("2. Navigate to disease prediction page")
    print("3. Click 'Try OCR Upload'")
    print("4. Upload one of the generated test images")
    print("5. Verify that OCR extracts the values correctly")
    print("="*50)
