# VitaCare Pro

<div align="center">

![VitaCare Pro](https://img.shields.io/badge/VitaCare-Pro-blue?style=for-the-badge)
![Status](https://img.shields.io/badge/Status-Production%20Ready-success?style=for-the-badge)
![Version](https://img.shields.io/badge/Version-1.0.0-informational?style=for-the-badge)

**A comprehensive hospital management and disease detection system demonstrating practical application of Data Structures and Algorithms (DSA) in machine learning and medical diagnosis.**

[Features](#-features) • [Quick Start](#-quick-start) • [Documentation](#-documentation) • [Team](#-team)

</div>

---

## 📖 About

**VitaCare Pro** is a production-ready hospital management system that showcases how fundamental DSA concepts can be leveraged to build efficient, scalable medical prediction systems. The project seamlessly integrates:

- 🚀 **C++ DSA Engine** - High-performance custom data structure implementations
- 🌐 **Python Flask Web Application** - User-friendly interface for doctors and patients
- 🤖 **Machine Learning Models** - Decision trees trained on real-world medical datasets
- 💾 **MySQL Database** - Patient records, thresholds, and prediction history
- ⚡ **Advanced Algorithms** - Symptom analysis, disease ranking, and risk scoring

## ✨ Features

### 🏥 Multi-Disease Detection
- **Diabetes Prediction** - 87% accuracy on 768 samples
- **Heart Disease Detection** - 85% accuracy on 303 samples
- **Breast Cancer Diagnosis** - 89% accuracy on 569 samples

### 🔐 Security & Access Control
- Role-based authentication (Admin, Doctor, Patient)
- PBKDF2 password hashing with salt
- Session management with secure cookies
- SQL injection prevention

### 📊 Performance
- Single prediction: **< 1ms**
- Batch processing (1000 patients): **~200ms**
- Scalable to **100,000+ patients**
- O(1) average lookup with custom hash map

### 🎯 Advanced DSA Implementation
- Binary Decision Trees
- Hash Maps with double hashing
- Priority Queues (Max-Heap)
- Stack & Queue structures
- Graph-based symptom mapping
- QuickSort & MergeSort
- KMP & Boyer-Moore string search

## 🚀 Quick Start

### Prerequisites

Before you begin, ensure you have the following installed:

- **Python** 3.13+
- **C++ Compiler** (MSVC on Windows, GCC on Linux)
- **CMake** 3.12+
- **MySQL** 5.7+

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/vitacare-pro.git
   cd vitacare-pro
   ```

2. **Build the C++ module**
   ```bash
   cd cpp_core
   mkdir build && cd build
   cmake ..
   cmake --build . --config Release
   cd ../..
   ```

3. **Install Python dependencies**
   ```bash
   cd python_frontend
   pip install -r requirements.txt
   ```

4. **Configure database**
   
   Create a `.env` file or set environment variables:
   ```env
   DB_HOST=localhost
   DB_NAME=hospital_management_db
   DB_USER=root
   DB_PASSWORD=your_password
   DB_PORT=3306
   ```

5. **Train the models**
   ```bash
   python train.py
   ```

6. **Run the application**
   ```bash
   python app.py
   ```

7. **Access the web interface**
   
   Navigate to `http://127.0.0.1:5000` in your browser

## 📁 Project Structure

```
VitaCare Pro/
├── 📂 cpp_core/                       # C++ DSA & ML Engine
│   ├── Include/
│   │   ├── decision_tree_simple.h    # Binary Decision Tree
│   │   ├── dsa_structures.h          # HashMap, Stack, Queue, Heap
│   │   ├── advanced_dsa.h            # Sorting, Searching algorithms
│   │   └── string_search.h           # KMP, Boyer-Moore
│   ├── src/
│   │   ├── decision_tree_simple.cpp
│   │   ├── dsa_structures.cpp
│   │   ├── advanced_dsa.cpp
│   │   ├── string_search.cpp
│   │   └── bindings.cpp              # PyBind11 interface
│   ├── build/                        # Compiled module
│   └── CMakeLists.txt
│
├── 📂 python_frontend/                # Flask Web Application
│   ├── app.py                        # Main Flask app
│   ├── train.py                      # Model training script
│   ├── database/
│   │   ├── db_connection.py          # MySQL connection pool
│   │   └── models.py                 # Data Access Objects
│   ├── predictions/
│   │   └── prediction_engine.py      # DSA-based predictions
│   ├── templates/                    # HTML templates
│   ├── static/                       # CSS, JavaScript
│   └── models/                       # Trained decision trees
│
├── 📂 datasets/                       # Training data
│   ├── diabetes.csv
│   ├── heart.csv
│   └── breast_cancer.csv
│
└── 📄 PROJECT_REPORT.md               # Full documentation
```

## 🛠️ Technology Stack

<table>
<tr>
<td>

**Backend**
- C++17
- PyBind11
- CMake

</td>
<td>

**Frontend**
- Flask 2.0+
- Jinja2
- HTML5/CSS3

</td>
<td>

**Database**
- MySQL 5.7+
- Connection Pooling

</td>
</tr>
</table>

## 📊 Data Structures & Algorithms

| Structure | Purpose | Complexity |
|-----------|---------|------------|
| **Binary Tree** | Decision tree classifier | O(log n) prediction |
| **Hash Map** | Disease threshold lookup | O(1) average |
| **Max-Heap** | Disease risk ranking | O(log n) operations |
| **Stack** | Report history (LIFO) | O(1) push/pop |
| **Queue** | Patient management | O(1) enqueue/dequeue |
| **Graph** | Symptom-disease mapping | O(V + E) traversal |
| **QuickSort** | Fast disease ranking | O(n log n) average |
| **Binary Search** | Symptom lookup | O(log n) |
| **KMP/Boyer-Moore** | Report text search | O(n + m) / O(n/m) |

## 💡 Usage Examples

### Making Predictions

```python
from predictions.prediction_engine import PredictionEngine

engine = PredictionEngine()

# Diabetes prediction
features = [1, 89, 66, 23, 94, 28.1, 0.167, 21]
result = engine.predict(features, disease_type='diabetes')

print(f"Risk Score: {result['risk_score']}")
print(f"Risk Level: {result['risk_level']}")
print(f"Prediction: {result['prediction']}")
```

### Accessing Patient Reports

```python
from database.models import PatientReportDAO

# Get last 5 reports (Stack LIFO)
reports = PatientReportDAO.get_recent_reports(patient_id=1, limit=5)

for report in reports:
    print(f"{report['date']} - {report['disease']}: {report['score']}")
```

### Training Custom Models

```bash
cd python_frontend
python train.py
```

## 📈 Performance Metrics

| Metric | Value |
|--------|-------|
| Single Prediction | < 1 ms |
| Batch (1000 patients) | ~200 ms |
| Hash Map Lookup | O(1) average |
| Disease Ranking | O(log n) |
| Scalability | 100,000+ patients |
| Diabetes Model Accuracy | ~87% |
| Heart Disease Accuracy | ~85% |
| Breast Cancer Accuracy | ~89% |

## 👥 Team

<table>
<tr>
<td align="center">
<h3>Group Leader</h3>
<b>Afshal Liaquat</b><br>
<i>Project Lead, Data Science & Testing</i><br>
<sub>Model training • Dataset preprocessing<br>System testing • Project coordination</sub>
</td>
</tr>
</table>

<table>
<tr>
<td align="center" width="50%">
<h3>Team Member</h3>
<b>Abdul Rafay</b><br>
<i>C++ Core Engine & Full UI Development</i><br>
<sub>Decision tree implementation<br>Core DSA structures<br>Python-C++ integration<br>Flask web application<br>Complete UI design</sub>
</td>
<td align="center" width="50%">
<h3>Team Member</h3>
<b>Bisma Shahid</b><br>
<i>Database Development & DSA Implementation</i><br>
<sub>MySQL schema design<br>Database optimization<br>Advanced DSA implementation<br>DAOs & testing</sub>
</td>
</tr>
</table>

## 🔮 Future Enhancements

- [ ] Ensemble methods (Random Forest, XGBoost)
- [ ] Real-time predictions via WebSocket
- [ ] Mobile applications (iOS/Android)
- [ ] HIPAA compliance audit

## 📚 Documentation

- [📖 Full Technical Report](PROJECT_REPORT.md)
- [📋 Project Index](PROJECT_INDEX.md)
- [📄 Professional Report](VitaCare_Pro_Project_Report.docx)

## 🤝 Contributing

We welcome contributions! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is part of a DSA course submission. All code and documentation are proprietary to the development team.

## 🙏 Acknowledgments

- **Pima Indians Diabetes Database** - Diabetes dataset
- **UCI Machine Learning Repository** - Heart disease and breast cancer datasets
- **PyBind11** - C++/Python binding framework
- **Flask** - Web application framework
- **MySQL** - Database management system

## 📞 Support

For questions or support, please open an issue in the repository.

---

<div align="center">

**Made with ❤️ by the VitaCare Pro Team**

⭐ Star us on GitHub — it motivates us a lot!

[Report Bug](https://github.com/yourusername/vitacare-pro/issues) • [Request Feature](https://github.com/abdulrafay1402/vitacare-pro/issues)

</div>