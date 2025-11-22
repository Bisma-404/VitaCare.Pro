# OCR Integration Documentation

## Overview
This document describes the OCR (Optical Character Recognition) functionality integrated into the Multi-Disease Detection System. The OCR feature allows users to upload images of medical reports and automatically extract relevant medical data for disease prediction.

## Architecture

### Components
1. **OCR Utility Module** (`ocr_utils.py`)
   - Handles text extraction from images
   - Parses medical data from extracted text
   - Maps extracted values to model input format

2. **Flask Routes** (in `app.py`)
   - `/ocr-upload/<disease_type>` - Image upload endpoint
   - `/ocr-review/<disease_type>` - Data review and editing page

3. **Templates**
   - `ocr_upload.html` - Image upload interface with drag-and-drop
   - `ocr_review.html` - Extracted data review and editing form
   - `form.html` (updated) - Added OCR upload option

## Workflow

### User Journey
```
1. User selects disease type
2. User clicks "Try OCR Upload" on form page
3. User uploads medical report image
4. System extracts text using Tesseract OCR
5. System parses text for relevant medical values
6. User reviews extracted data on review page
7. User edits incorrect values (if any)
8. User confirms data
9. System makes prediction using cpp_tree module
10. Results displayed on result page
```

### Data Flow
```
Image Upload → OCR Extraction → Text Parsing → Data Mapping → 
Review/Edit → Feature Extraction → Model Prediction → Results
```

## Installation & Setup

### Prerequisites
1. **Python Dependencies**
   ```bash
   pip install -r requirements.txt
   ```
   
   New dependencies added:
   - `pytesseract==0.3.10` - Python wrapper for Tesseract OCR
   - `Pillow==10.0.0` - Image processing library

2. **Tesseract OCR Engine**
   
   **Windows:**
   - Download installer from: https://github.com/UB-Mannheim/tesseract/wiki
   - Run the installer (recommended path: `C:\Program Files\Tesseract-OCR`)
   - Add Tesseract to system PATH, or update `ocr_utils.py`:
     ```python
     pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
     ```
   
   **Linux:**
   ```bash
   sudo apt-get install tesseract-ocr
   ```
   
   **macOS:**
   ```bash
   brew install tesseract
   ```

3. **Verify Installation**
   ```bash
   tesseract --version
   ```

## Usage

### For End Users

1. **Navigate to Disease Assessment**
   - Select disease type from home page
   - Click "Try OCR Upload" button

2. **Upload Medical Report**
   - Click upload area or drag and drop image
   - Supported formats: JPG, PNG, BMP, TIFF
   - Maximum file size: 16MB

3. **Review Extracted Data**
   - Green fields: Successfully extracted from image
   - Orange fields: Using default values (manual verification needed)
   - Edit any incorrect values
   - Click "Confirm & Get Prediction"

4. **View Results**
   - Prediction outcome displayed
   - Medical recommendations provided
   - Input values shown for reference

### Tips for Best OCR Results

1. **Image Quality**
   - Use high-resolution images (300 DPI or higher)
   - Ensure good lighting and contrast
   - Avoid shadows and glare

2. **Text Format**
   - Typed/printed text works best
   - Clear, readable fonts
   - Avoid handwritten notes

3. **Report Structure**
   - Include field labels and values
   - Format: "Field: Value" or "Field = Value"
   - Example: "Glucose: 120" or "BMI = 25.5"

4. **Image Orientation**
   - Ensure text is upright
   - Crop unnecessary areas
   - Center the relevant information

## Technical Details

### OCR Parser Class

```python
class OCRParser:
    def extract_text(image_path)
    def parse_diabetes_report(text)
    def parse_heart_report(text)
    def parse_breast_cancer_report(text)
    def parse_report(image_path, disease_type)
```

### Field Mapping

#### Diabetes
- Pregnancies
- Glucose (mg/dL)
- Blood Pressure (mm Hg)
- Skin Thickness (mm)
- Insulin (µU/mL)
- BMI
- Diabetes Pedigree Function
- Age

#### Heart Disease
- Age
- Sex (0=Female, 1=Male)
- Chest Pain Type (0-3)
- Resting Blood Pressure (mm Hg)
- Cholesterol (mg/dL)
- Fasting Blood Sugar > 120 mg/dL (0=No, 1=Yes)
- Resting ECG Results (0-2)
- Maximum Heart Rate
- Exercise Induced Angina (0=No, 1=Yes)
- ST Depression (oldpeak)
- Slope (0-2)
- Number of Major Vessels (0-4)
- Thalassemia (1-3)

#### Breast Cancer
- Mean Radius (mm)
- Mean Texture
- Mean Perimeter (mm)
- Mean Area (mm²)
- Mean Smoothness
- Mean Compactness
- Mean Concavity
- Mean Concave Points
- Mean Symmetry
- Mean Fractal Dimension

### Pattern Recognition

The OCR parser uses regular expressions to identify medical values:

```python
patterns = {
    'field_name': r'field\s*[:\-=]\s*(\d+\.?\d*)',
    # Matches: "field: 123", "field = 45.6", "field - 78.9"
}
```

### Default Values

When OCR cannot extract a field, default values are used:
- Defaults are defined in `get_default_values()` function
- Users are warned to verify these values
- Visual indicators (orange borders) highlight default fields

## Error Handling

### Common Errors and Solutions

1. **"Tesseract not found"**
   - Solution: Install Tesseract and configure path in `ocr_utils.py`

2. **"Invalid file type"**
   - Solution: Upload only JPG, PNG, BMP, or TIFF images

3. **"OCR extraction failed"**
   - Possible causes: Corrupted image, unsupported format, insufficient permissions
   - Solution: Try a different image or check file permissions

4. **"No fields extracted"**
   - Causes: Poor image quality, unclear text, unexpected format
   - Solution: Improve image quality or use manual entry

5. **"Model not found"**
   - Cause: Models not trained yet
   - Solution: Run `train.py` to generate model files

## Security Considerations

1. **File Upload Security**
   - Filename sanitization using `secure_filename()`
   - File type validation (whitelist approach)
   - File size limit (16MB maximum)
   - Temporary file cleanup after processing

2. **Session Management**
   - OCR data stored in Flask session
   - Session data cleared after prediction
   - Secret key required for session encryption

3. **Input Validation**
   - All extracted values validated against field constraints
   - Min/max ranges enforced on review page
   - Type checking for numeric fields

## Performance Considerations

1. **OCR Processing Time**
   - Typical: 2-5 seconds for standard medical reports
   - Factors: Image size, resolution, text complexity

2. **Memory Usage**
   - Images loaded into memory during processing
   - Files deleted immediately after extraction
   - Session storage for extracted data (lightweight)

3. **Optimization Tips**
   - Resize large images before upload
   - Use appropriate image format (PNG for clarity, JPG for size)
   - Consider batch processing for multiple reports

## Testing

### Creating Test Images

For testing purposes, create medical report images with the following format:

**Example Diabetes Report:**
```
PATIENT MEDICAL REPORT
=====================

Pregnancies: 2
Glucose: 148
Blood Pressure: 85
Skin Thickness: 25
Insulin: 95
BMI: 28.5
Diabetes Pedigree Function: 0.627
Age: 45
```

### Generating Test Images

You can use this Python script to generate test report images:

```python
from PIL import Image, ImageDraw, ImageFont

def create_test_report(filename, data):
    img = Image.new('RGB', (800, 600), color='white')
    draw = ImageDraw.Draw(img)
    font = ImageFont.load_default()
    
    y = 50
    for key, value in data.items():
        text = f"{key}: {value}"
        draw.text((50, y), text, fill='black', font=font)
        y += 40
    
    img.save(filename)

# Example usage
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

create_test_report('test_diabetes_report.png', diabetes_data)
```

## Future Enhancements

### Planned Features
1. **Multi-language OCR support**
   - Configure Tesseract for additional languages
   - Add language selection option

2. **Batch Processing**
   - Upload multiple reports at once
   - Generate comparison reports

3. **OCR Confidence Scores**
   - Display confidence level for each extracted field
   - Allow users to prioritize low-confidence fields for review

4. **Template Learning**
   - Learn from user corrections
   - Improve extraction accuracy over time

5. **Advanced Image Preprocessing**
   - Automatic rotation correction
   - Noise reduction
   - Contrast enhancement

6. **Export Functionality**
   - Save extracted data to CSV/JSON
   - Generate downloadable reports

## Troubleshooting

### Debug Mode

Enable debug logging in `ocr_utils.py`:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Add to extract_text method:
logger.debug(f"Extracting text from: {image_path}")
logger.debug(f"Extracted text: {text}")
```

### Common Issues

1. **Poor OCR Accuracy**
   - Check image quality and resolution
   - Verify Tesseract installation
   - Try different OCR configuration:
     ```python
     custom_config = r'--psm 4 --oem 3'  # Different page segmentation mode
     ```

2. **Missing Fields**
   - Review raw extracted text
   - Check if field names match regex patterns
   - Adjust patterns in `ocr_utils.py` if needed

3. **Performance Issues**
   - Reduce image size before upload
   - Check server resources
   - Consider async processing for production

## API Reference

### OCR Routes

#### POST /ocr-upload/<disease_type>
Upload medical report image for OCR processing.

**Parameters:**
- `disease_type` (path): Disease type ('diabetes', 'heart', 'breast_cancer')
- `ocr_image` (file): Image file to process

**Response:**
- Redirect to `/ocr-review/<disease_type>` on success
- Flash error message and reload page on failure

**Session Data:**
```python
{
    'raw_text': str,          # Extracted text
    'parsed_data': dict,      # Parsed field values
    'fields_found': int,      # Number of extracted fields
    'disease_type': str,      # Disease type
    'filename': str           # Original filename
}
```

#### GET /ocr-review/<disease_type>
Display review page with extracted data.

**Parameters:**
- `disease_type` (path): Disease type

**Response:**
- Render `ocr_review.html` template

#### POST /ocr-review/<disease_type>
Process edited data and make prediction.

**Parameters:**
- `disease_type` (path): Disease type
- Form data: All field values

**Response:**
- Render `result.html` with prediction results

## Support

For issues, questions, or contributions:
1. Check this documentation
2. Review error messages in Flask console
3. Verify Tesseract installation
4. Test with sample images
5. Check file permissions in `uploads/` directory

## License and Disclaimer

**Educational Use Only**: This OCR system is for educational and demonstration purposes. It should not be used for actual medical diagnosis or clinical decision-making.

**Data Privacy**: Uploaded images are processed locally and deleted immediately after extraction. No medical data is stored permanently.

**Accuracy**: OCR accuracy depends on image quality and report format. Always verify extracted values before using for predictions.
