# 📝 Project Workflow Summary: Multi-Disease Detection System

This guide covers the full working pipeline for the Multi-Disease Detection Support System using a custom C++ (no external ML libs for saving/loading) decision tree and a Python Flask frontend.

---

## 1️⃣ How it Works

- **Decision Trees** are implemented purely in C++, integrated with Python via pybind11.
- **Model Serialization:**
  - Model saving/loading is done *entirely in C++*, via custom save/load methods—no machine learning library pickle/serialization is used.
  - Each model is stored as a readable `.txt` file for transparency and portability.
- **No external ML libraries** are used for model training or serialization—DSA concepts only!

---

## 2️⃣ Model Training Workflow

### Train & Save Models for All Diseases

#### Diabetes
```bash
cd python_frontend
python train.py --disease diabetes --dataset ../datasets/diabetes.csv --max-depth 8 --criterion entropy
```
- Output: `models/diabetes_model.txt`

#### Heart Disease
```bash
python train.py --disease heart --dataset ../datasets/heart.csv --max-depth 10 --criterion gini
```
- Output: `models/heart_model.txt`

#### Breast Cancer
```bash
python train.py --disease breast_cancer --dataset ../datasets/breast_cancer.csv --max-depth 6 --criterion entropy
```
- Output: `models/breast_cancer_model.txt`
- **Label Mapping:** correctly handles 'M' (Malignant → 1) and 'B' (Benign → 0) using the project config.

---

## 3️⃣ Launch & Use the Web App

### Steps to Launch
1. **Activate Python Environment** (if using venv or conda)
2. **Ensure all dependencies installed**
   ```bash
   pip install -r python_frontend/requirements.txt
   ```
3. **Run the Flask Web Application**
   ```bash
   cd python_frontend/webapp
   python app.py
   ```
4. **Access the App**
    - In your web browser, open: [http://127.0.0.1:5000](http://127.0.0.1:5000)
    - Use the menu to select the disease, fill the form, and get predictions!

**NOTE:** All models are now loaded from `.txt` (not `.pkl`). Make sure you have run training for all three disease models before using the web app.

---

## 4️⃣ Troubleshooting
- **C++ Module Import Error:**
  - Re-build and reinstall C++ module
    ```bash
    cd build
    cmake .. -Dpybind11_DIR="<your pybind11 cmake path>"
    cmake --build . --config Release
    cmake --install .
    ```
- **Model Not Found:**
  - Re-run the corresponding `python train.py ...` command
- **Breast Cancer Label Error:**
  - Should now be fixed! If you see errors, check your CSV file encoding and columns.
- **.pkl vs .txt:**
  - Only `.txt` model files are now used! You can remove or ignore older `.pkl` files.

---

**Education-focused, portable, and easy to debug. Enjoy using and exploring the system!**
