# VitaCare Pro - Multi-Disease Detection System

[![Python](https://img.shields.io/badge/Python-3.13-blue)](https://www.python.org/)
[![C++](https://img.shields.io/badge/C%2B%2B-17-orange)](https://isocpp.org/)

Intelligent hospital management system combining custom C++ DSA implementations with ML for disease prediction. Achieves 98%+ accuracy on diabetes, heart disease, and breast cancer detection.

**Repository:** [github.com/abdulrafay1402/VitaCare.Pro](https://github.com/abdulrafay1402/VitaCare.Pro)

---

##  Overview

VitaCare Pro demonstrates practical DSA applications in healthcare:
- **Custom C++ DSA Engine** - HashMap, Decision Trees, Priority Queues, Graphs
- **ML-Powered Predictions** - 98%+ accuracy using entropy-based decision trees
- **Clinical Integration** - ADA, ACC/AHA, WDBC medical guidelines
- **Full-Stack Web App** - Flask backend with responsive UI

**Diseases:** Diabetes (98.18%), Heart Disease (98.02%), Breast Cancer (99.82%)

---

##  Features

- Multi-disease detection with clinical guidelines integration
- Role-based authentication (Admin/Doctor/Staff/Patient)
- O(1) HashMap lookups, <1ms predictions
- PBKDF2 password hashing, SQL injection prevention
- OCR medical report scanning, responsive PWA

---

##  Architecture

```
Flask Web App (Admin/Doctor/Staff/Patient)
    ↓
Python Prediction Engine (DSA Analysis + Risk Scoring)
    ↓
C++ DSA Engine ←→ MySQL Database
(HashMap, Trees,     (Users, Patients,
 PriorityQ, Graph)    Reports, Predictions)
```

---

##  Tech Stack

**Backend:** Python 3.13, Flask 2.3.3, C++17, pybind11, MySQL 5.7+  
**Frontend:** HTML5/CSS3, JavaScript, Bootstrap 5  
**ML/DSA:** Custom decision trees (C++), entropy-based splitting  
**Tools:** CMake 3.12+, Tesseract OCR, Git

---

##  Installation

### Prerequisites
- Python 3.13+ | C++ Compiler (MSVC/GCC) | CMake 3.12+ | MySQL 5.7+ | Git

### Quick Setup

```bash
# Clone repository
git clone https://github.com/abdulrafay1402/VitaCare.Pro.git
cd VitaCare.Pro

# Build C++ module
cd cpp_core/build
cmake .. && cmake --build . --config Release

# Install Python dependencies
cd ../../python_frontend
pip install -r requirements.txt

# Configure database
mysql -u root -p -e "CREATE DATABASE hospital_management_db;"

# Set environment variables
export DB_HOST=localhost DB_NAME=hospital_management_db DB_USER=root DB_PASSWORD=your_password DB_PORT=3306

# Train models
python train.py --disease diabetes --dataset ../datasets/diabetes.csv --max-depth 15 --min-samples 4
python train.py --disease heart --dataset ../datasets/heart.csv --max-depth 12 --min-samples 5
python train.py --disease breast_cancer --dataset ../datasets/breast_cancer.csv --max-depth 12 --min-samples 4

# Run application
python app.py
```

Access at: **http://localhost:5000**

---

##  Performance

| Disease | Samples | Accuracy | Parameters |
|---------|---------|----------|------------|
| Diabetes | 768 | 98.18% | depth=15, split=4 |
| Heart Disease | 303 | 98.02% | depth=12, split=5 |
| Breast Cancer | 569 | 99.82% | depth=12, split=4 |

**Datasets:** Pima Diabetes, Cleveland Heart, Wisconsin WDBC

---

##  DSA Implementation

| Data Structure | Purpose | Complexity |
|----------------|---------|------------|
| HashMap | Threshold lookups | O(1) |
| Decision Tree | Disease classification | O(log n) |
| Priority Queue | Risk ranking | O(log n) |
| Graph | Symptom mapping | O(V+E) |
| QuickSort | Sorting | O(n log n) |
| KMP/Boyer-Moore | Text search | O(n+m) |

---

##  Project Structure

```
cpp_core/          # C++ DSA Engine
  Include/         # Headers
  src/             # Implementation + bindings
  build/Release/   # Compiled module

datasets/          # Training data (CSV)

python_frontend/   # Flask Application
  auth/            # Authentication
  database/        # DB layer
  predictions/     # Prediction engine
  models/          # Trained models
  static/          # CSS/JS
  templates/       # HTML
```

---

## License

This project is for academic and institutional use. Please credit the developers if reused or modified for deployment.


## Developed By
BISMA SHAHID  
Department of Software Engineering  
FAST NUCES KHI


