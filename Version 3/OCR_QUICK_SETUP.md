# OCR Quick Setup Guide

## Installation Steps

### Step 1: Install Python Dependencies
```bash
cd python_frontend
pip install -r requirements.txt
```

### Step 2: Install Tesseract OCR

#### Windows:
1. Download Tesseract installer:
   - Go to: https://github.com/UB-Mannheim/tesseract/wiki
   - Download latest version (e.g., `tesseract-ocr-w64-setup-5.3.3.20231005.exe`)

2. Run installer:
   - Install to default location: `C:\Program Files\Tesseract-OCR`
   - Check "Add to PATH" option during installation

3. Verify installation:
   ```bash
   tesseract --version
   ```

4. If Tesseract is not in PATH, update `webapp/ocr_utils.py`:
   ```python
   # Uncomment and set the correct path (around line 9)
   pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
   ```

#### Linux (Ubuntu/Debian):
```bash
sudo apt-get update
sudo apt-get install tesseract-ocr
```

#### macOS:
```bash
brew install tesseract
```

### Step 3: Test OCR Installation
```bash
cd python_frontend/webapp
python generate_test_images.py
```
This will create test medical report images in `test_images/` directory.

### Step 4: Start the Application
```bash
cd python_frontend/webapp
python app.py
```

### Step 5: Test OCR Functionality
1. Open browser: http://127.0.0.1:5000
2. Select a disease type
3. Click "Try OCR Upload"
4. Upload one of the test images from `test_images/`
5. Review extracted data
6. Confirm and get prediction

## Troubleshooting

### "Tesseract not found"
- **Windows**: Check if Tesseract is in PATH or update path in `ocr_utils.py`
- **Linux/Mac**: Run `which tesseract` to verify installation
- Restart terminal/IDE after installation

### "No module named 'pytesseract'"
```bash
pip install pytesseract
```

### "No module named 'PIL'"
```bash
pip install Pillow
```

### OCR Extracts No Fields
- Check image quality (must be clear and readable)
- Try generating test images with `generate_test_images.py`
- Review raw extracted text on review page
- Verify field format matches expected pattern (e.g., "Field: Value")

### Permission Errors
- Ensure `uploads/` directory has write permissions
- On Linux/Mac: `chmod 755 python_frontend/webapp/uploads`

## Quick Test

### Generate and Test
```bash
# 1. Generate test images
cd python_frontend/webapp
python generate_test_images.py

# 2. Start server
python app.py

# 3. Open browser and test
# Navigate to: http://127.0.0.1:5000
# Click on any disease → "Try OCR Upload"
# Upload: test_images/diabetes_report_test.png
```

## Expected Results

### Diabetes Test Image
Should extract:
- Pregnancies: 2
- Glucose: 148
- Blood Pressure: 85
- Skin Thickness: 25
- Insulin: 95
- BMI: 28.5
- Diabetes Pedigree Function: 0.627
- Age: 45

### Success Indicators
- ✅ Fields Found: 8/8
- ✅ Success Rate: 100%
- ✅ All fields marked in green (extracted)

## File Structure After Setup

```
python_frontend/
├── webapp/
│   ├── app.py (updated with OCR routes)
│   ├── ocr_utils.py (NEW)
│   ├── generate_test_images.py (NEW)
│   ├── uploads/ (NEW - auto-created)
│   ├── test_images/ (NEW - created by test script)
│   └── templates/
│       ├── ocr_upload.html (NEW)
│       ├── ocr_review.html (NEW)
│       └── form.html (updated)
└── requirements.txt (updated)
```

## Next Steps

1. Test with real medical reports
2. Adjust OCR patterns if needed (in `ocr_utils.py`)
3. Review [OCR_INTEGRATION_GUIDE.md](../OCR_INTEGRATION_GUIDE.md) for advanced usage
4. Customize templates to match your design preferences

## Support

If you encounter issues:
1. Check console output for error messages
2. Verify all dependencies are installed
3. Test with generated images first
4. Review full documentation in OCR_INTEGRATION_GUIDE.md
