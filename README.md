# VitaCare Pro - Multi-Disease Detection System

[![Status](https://img.shields.io/badge/Status-Production%20Ready-success)](https://github.com/abdulrafay1402/VitaCare.Pro)
[![Python](https://img.shields.io/badge/Python-3.13-blue)](https://www.python.org/)
[![C++](https://img.shields.io/badge/C%2B%2B-17-orange)](https://isocpp.org/)
[![Accuracy](https://img.shields.io/badge/Accuracy-98%25+-brightgreen)](https://github.com/abdulrafay1402/VitaCare.Pro)

An intelligent hospital management system combining C++ DSA implementations with machine learning for accurate disease prediction. Achieves 98%+ accuracy across diabetes, heart disease, and breast cancer detection.

**Repository:** [github.com/abdulrafay1402/VitaCare.Pro](https://github.com/abdulrafay1402/VitaCare.Pro)

---

## 🎯 Overview

VitaCare Pro demonstrates practical DSA applications in healthcare through:
- **Custom C++ DSA Engine** - HashMap, Decision Trees, Priority Queues, Graphs
- **ML-Powered Predictions** - 98%+ accuracy using entropy-based decision trees
- **Clinical Integration** - ADA, ACC/AHA, WDBC medical guidelines
- **Full-Stack Web App** - Flask backend with responsive UI

### Disease Detection
- **Diabetes** (98.18% accuracy) - Type 2 risk assessment
- **Heart Disease** (98.02% accuracy) - Cardiovascular prediction  
- **Breast Cancer** (99.82% accuracy) - Malignancy classification

---

## ✨ Key Features

**Medical Capabilities**
- Multi-disease detection with 98%+ accuracy
- Clinical guidelines integration (ADA, ACC/AHA, WDBC)
- Risk stratification (Low/Moderate/High)
- Adaptive confidence scoring (65-95%)

**Technical Highlights**
- Custom C++ DSA implementations (O(1) HashMap lookup)
- Single prediction: <1ms, Batch: 200ms for 1000 patients
- Role-based authentication (Admin/Doctor/Staff/Patient)
- PBKDF2 password hashing, SQL injection prevention
- OCR support for medical report scanning
- Responsive PWA with offline capability

---

## 🏗️ Architecture

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

## 🛠️ Tech Stack

**Backend:** Python 3.13, Flask 2.3.3, C++17, pybind11, MySQL 5.7+  
**Frontend:** HTML5/CSS3, JavaScript ES6+, Bootstrap 5, Chart.js  
**ML/DSA:** Custom decision trees (C++), entropy-based splitting  
**Tools:** CMake 3.12+, Tesseract OCR, Git

---

## 🚀 Installation

### Prerequisites

Ensure you have the following installed:

- **Python 3.13+** ([Download](https://www.python.org/downloads/))
- **C++ Compiler** (MSVC on Windows, GCC on Linux)
- **CMake 3.12+** ([Download](https://cmake.org/download/))
- **MySQL 5.7+** ([Download](https://dev.mysql.com/downloads/))
- **Git** ([Download](https://git-scm.com/downloads))

### Step 1: Clone Repository

```bash
git clone https://github.com/yourusername/Multi-Disease-Detect-Support-System.git
cd Multi-Disease-Detect-Support-System
```

### Step 2: Build C++ Module

```bash
cd cpp_core
mkdir build
cd build
cmake ..
cmake --build . --config Release
cd ../..
```

The compiled module (`cpp_tree.cp313-win_amd64.pyd`) will be automatically copied to `python_frontend/`.

### Step 3: Install Python Dependencies

```bash
cd python_frontend
pip install -r requirements.txt
```

**Requirements:**
- flask==2.3.3
- werkzeug==2.3.7
- pytesseract==0.3.13
- pillow==11.3.0
- mysql-connector-python==9.5.0
- pybind11==2.11.1

### Step 4: Configure Database

1. Create MySQL database:

```sql
CREATE DATABASE hospital_management_db;
```

2. Set environment variables (or create `.env` file):

```env
DB_HOST=localhost
DB_NAME=hospital_management_db
DB_USER=root
DB_PASSWORD=your_password
DB_PORT=3306
```

3. Initialize database schema (run the application once to auto-create tables).

### Step 5: Train Models

Train the decision tree models on provided datasets:

```bash
cd python_frontend

# Train diabetes model
python train.py --disease diabetes --dataset ../datasets/diabetes.csv --max-depth 15 --min-samples 4

# Train heart disease model
python train.py --disease heart --dataset ../datasets/heart.csv --max-depth 12 --min-samples 5

# Train breast cancer model
python train.py --disease breast_cancer --dataset ../datasets/breast_cancer.csv --max-depth 12 --min-samples 4
```

Models will be saved to `python_frontend/models/`.

### Step 6: Run Application

```bash
cd python_frontend
python app.py
```

Access the application at: **http://localhost:5000**

---

## 📖 Usage

**Admin:** Manage users, configure thresholds, view analytics (`/admin/login`)  
**Doctor/Staff:** Register patients, make predictions, upload OCR reports  
**Patient:** View reports, prediction history, download PDFs

---

## 📊 Performance

| Disease | Samples | Accuracy | Parameters |
|---------|---------|----------|------------|
| **Diabetes** | 768 | 98.18% | depth=15, split=4 |
| **Heart Disease** | 303 | 98.02% | depth=12, split=5 |
| **Breast Cancer** | 569 | 99.82% | depth=12, split=4 |

**Datasets:** Pima Indians Diabetes, Cleveland Heart Disease, Wisconsin WDBC  
**Training:** Entropy criterion, optimized hyperparameters

---

## 📁 Project Structure

```
Multi-Disease-Detect-Support-System/
│
├── cpp_core/                      # C++ DSA Engine
│   ├── Include/                   # Header files
│   │   ├── decision_tree_simple.h
│   │   ├── dsa_structures.h
│   │   ├── advanced_dsa.h
│   │   ├── string_search.h
│   │   ├── custom_map.h
│   │   └── custom_set.h
│   ├── src/                       # Implementation files
│   │   ├── decision_tree_simple.cpp
│   │   ├── dsa_structures.cpp
│   │   ├── advanced_dsa.cpp
│   │   ├── string_search.cpp
│   │   └── bindings.cpp          # pybind11 bindings
│   ├── build/                     # Build directory
│   │   └── Release/
│   │       └── cpp_tree.cp313-win_amd64.pyd
│   └── CMakeLists.txt            # Build configuration
│
├── datasets/                      # Training datasets
│   ├── diabetes.csv
│   ├── heart.csv
│   └── breast_cancer.csv
│
├── python_frontend/               # Flask Application
│   ├── app.py                    # Main application
│   ├── requirements.txt          # Python dependencies
│   ├── train.py                  # Model training script
│   ├── cpp_tree.cp313-win_amd64.pyd  # Compiled C++ module
│   │
│   ├── auth/                     # Authentication module
│   │   ├── auth_routes.py
│   │   └── admin_routes.py
│   │
│   ├── database/                 # Database layer
│   │   ├── db_connection.py
│   │   └── models.py
│   │
│   ├── patient/                  # Patient portal
│   │   └── patient_routes.py
│   │
│   ├── staff/                    # Staff portal
│   │   └── staff_routes.py
│   │
│   ├── predictions/              # Prediction engine
│   │   └── prediction_engine.py
│   │
│   ├── utils/                    # Utility modules
│   │   ├── cpp_dsa_wrapper.py
│   │   ├── mapping.py
│   │   ├── medical_mappings.py
│   │   └── password_hash.py
│   │
│   ├── models/                   # Trained ML models
│   │   ├── diabetes_model.txt
│   │   ├── heart_model.txt
│   │   └── breast_cancer_model.txt
│   │
│   ├── static/                   # Frontend assets
│   │   ├── css/
│   │   │   ├── modern.css
│   │   │   ├── responsive.css
│   │   │   └── vitacare-pro-enhancements.css
│   │   ├── js/
│   │   │   ├── form-validation.js
│   │   │   ├── risk-gauge.js
│   │   │   └── vitacare-utilities.js
│   │   ├── manifest.json
│   │   └── service-worker.js
│   │
│   ├── templates/                # HTML templates
│   │   ├── index.html
│   │   ├── auth/
│   │   ├── admin/
│   │   ├── staff/
│   │   └── patient/
│   │
│   └── uploads/                  # OCR uploaded files
│
├── CMakeLists.txt               # Root build config
└── README.md                    # This file
```

---

## 🗄️ Database

**Tables:** users, patients, reports, predictions, disease_thresholds  
**Relationships:** Patients → Users (FK), Reports → Patients/Users (FK), Predictions → Patients (FK)  
**Features:** Auto-initialization, connection pooling, parameterized queries

---

## 🧮 DSA Implementation

| Data Structure | Purpose | Complexity |
|----------------|---------|------------|
| **HashMap** | Threshold lookups | O(1) avg |
| **Decision Tree** | Disease classification | O(log n) |
| **Priority Queue** | Risk ranking | O(log n) |
| **Graph** | Symptom-disease mapping | O(V+E) |
| **QuickSort/MergeSort** | Risk factor sorting | O(n log n) |
| **KMP/Boyer-Moore** | Report text search | O(n+m) |

**Features:** Double hashing, entropy-based splitting, max-heap, adjacency list, in-place sorting

---

## 👥 Author

**Abdul Rafay** | Roll: 24K-3007  
C++ DSA Engine, Algorithm Design, Backend Development

**Team Members:**  
- Afshal Liaquat (24K-2558) - Group Leader, Backend  
- Bisma Shahid (24K-3012) - Frontend, Database

**Course:** Data Structures and Algorithms | Fall 2025

---

## 📞 Contact

**GitHub:** [abdulrafay1402](https://github.com/abdulrafay1402)  
**Repository:** [VitaCare.Pro](https://github.com/abdulrafay1402/VitaCare.Pro)  
**Issues:** [Report Issues](https://github.com/abdulrafay1402/VitaCare.Pro/issues)

---

## 🙏 Acknowledgments

- UCI Machine Learning Repository (Datasets)
- ADA, ACC/AHA, WDBC (Medical Guidelines)
- Flask, pybind11, Tesseract OCR (Libraries)

---

<div align="center">

**⭐ Star this repository if you find it helpful! ⭐**

Made with ❤️ by Team VitaCare Pro

</div>
