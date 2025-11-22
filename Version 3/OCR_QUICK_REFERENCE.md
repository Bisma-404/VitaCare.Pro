# OCR Quick Reference Card

## 🚀 Quick Start (5 Minutes)

### 1. Install Dependencies
```bash
pip install pytesseract Pillow
```

### 2. Install Tesseract
- **Windows**: https://github.com/UB-Mannheim/tesseract/wiki
- **Linux**: `sudo apt-get install tesseract-ocr`
- **Mac**: `brew install tesseract`

### 3. Generate Test Images
```bash
cd python_frontend/webapp
python generate_test_images.py
```

### 4. Start Application
```bash
python app.py
```

### 5. Test OCR
1. Go to http://127.0.0.1:5000
2. Click any disease
3. Click "Try OCR Upload"
4. Upload `test_images/diabetes_report_test.png`
5. Review → Confirm → Get Results ✅

---

## 📁 New Files Overview

| File | Purpose | Size |
|------|---------|------|
| `ocr_utils.py` | OCR extraction & parsing | 282 lines |
| `ocr_upload.html` | Upload interface | 234 lines |
| `ocr_review.html` | Review interface | 275 lines |
| `generate_test_images.py` | Test image generator | 141 lines |

---

## 🔑 Key Functions

### Python
```python
# In ocr_utils.py
parser = OCRParser()
result = parser.parse_report(image_path, 'diabetes')
# Returns: {'raw_text': str, 'parsed_data': dict, 'fields_found': int}
```

### Flask Routes
```python
/ocr-upload/<disease_type>    # Upload image
/ocr-review/<disease_type>    # Review extracted data
```

---

## 💡 Tips for Best Results

### ✅ DO:
- Use high-resolution images (300+ DPI)
- Ensure good lighting
- Use typed/printed text
- Format: "Field: Value"

### ❌ DON'T:
- Upload handwritten notes
- Use blurry images
- Include unrelated text
- Exceed 16MB file size

---

## 🐛 Common Issues

| Problem | Solution |
|---------|----------|
| "Tesseract not found" | Install Tesseract + update `ocr_utils.py` path |
| "No fields extracted" | Check image quality + review raw text |
| "Invalid file type" | Use JPG, PNG, BMP, or TIFF only |
| "Model not found" | Run `train.py` for the disease type |

---

## 📊 Supported Formats

### Image Formats
✅ JPG/JPEG
✅ PNG  
✅ BMP
✅ TIFF

### Text Formats Recognized
- `Field: Value`
- `Field = Value`
- `Field - Value`
- Case insensitive
- Spaces optional

---

## 🎯 Success Indicators

On review page, look for:
- **Green fields** = Successfully extracted ✅
- **Orange fields** = Default value (verify!) ⚠️
- **Success Rate** = % of fields extracted
- **Fields Found** = Number extracted vs total

---

## 📖 Documentation Links

- **Full Guide**: [OCR_INTEGRATION_GUIDE.md](OCR_INTEGRATION_GUIDE.md)
- **Setup**: [OCR_QUICK_SETUP.md](OCR_QUICK_SETUP.md)
- **Summary**: [OCR_IMPLEMENTATION_SUMMARY.md](OCR_IMPLEMENTATION_SUMMARY.md)
- **Main README**: [README.md](README.md)

---

## 🔧 Configuration

### Update Tesseract Path (Windows)
Edit `webapp/ocr_utils.py` line 9:
```python
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
```

### Adjust OCR Confidence
Edit `webapp/ocr_utils.py` line 31:
```python
custom_config = r'--oem 3 --psm 6'  # Change PSM mode
```

---

## 🧪 Testing Checklist

- [ ] Install Tesseract
- [ ] Install Python packages
- [ ] Generate test images
- [ ] Start Flask app
- [ ] Upload test image
- [ ] Verify extraction
- [ ] Edit values
- [ ] Get prediction
- [ ] Check results

---

## 📞 Quick Troubleshooting

**OCR not working?**
```bash
# Check Tesseract installation
tesseract --version

# Check Python packages
pip list | grep pytesseract
pip list | grep Pillow
```

**No fields extracted?**
1. Check raw text on review page
2. Verify image quality
3. Try test images first
4. Review patterns in `ocr_utils.py`

**Upload fails?**
1. Check file size < 16MB
2. Verify file format (JPG, PNG, BMP, TIFF)
3. Check `uploads/` folder permissions
4. Review Flask console for errors

---

## 🎓 Learning Resources

### Key Concepts
- **OCR**: Optical Character Recognition
- **Tesseract**: Google's OCR engine
- **Regex**: Pattern matching for field extraction
- **Flask Sessions**: Temporary data storage

### Technologies Used
- `pytesseract`: Python wrapper for Tesseract
- `Pillow`: Image processing
- `Flask`: Web framework
- `Regex`: Text pattern matching

---

## ⚡ Performance Tips

- Resize large images before upload
- Use PNG for clarity, JPG for size
- Process one image at a time
- Clear old uploads regularly

**Average Processing Time**: 2-5 seconds per image

---

## 🔒 Security Notes

- Files deleted after processing
- No permanent storage
- Session-based data handling
- Secure filename sanitization
- Type and size validation

---

## 📈 Statistics

| Metric | Value |
|--------|-------|
| Total Lines Added | ~1,500 |
| New Files | 7 |
| Modified Files | 4 |
| Supported Diseases | 3 |
| Total Fields | 31 |
| Processing Time | 2-5 sec |
| Max File Size | 16 MB |

---

## ✨ Features at a Glance

✅ Image upload with drag-and-drop
✅ Automatic text extraction
✅ Smart field parsing
✅ Interactive data review
✅ Visual success indicators
✅ Default value handling
✅ Error recovery
✅ Dark/light theme support
✅ Mobile responsive
✅ Comprehensive documentation

---

**Need Help?** Check the full documentation in `OCR_INTEGRATION_GUIDE.md`

**Ready to Start?** Run: `python generate_test_images.py` then `python app.py`
