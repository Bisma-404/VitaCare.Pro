# VitaCare Pro - Features Documentation

## System Overview
Multi-Disease Detection Support System with role-based access control for Admin, Staff (Doctors/Lab Technicians), and Patients.

---

## 🔐 ADMIN ROLE FEATURES

### 1. **Dashboard** (`/admin/dashboard`)
**How it works:**
- Displays statistics: Doctor count, Lab Tech count, Patient count, Total reports
- Shows recent users (last 10 registered)
- Shows top 5 diseases by prediction frequency
- **Access:** Only ADMIN role

### 2. **User Management** (`/admin/users`)
**Features:**
- **View Users:** List all users filtered by role (All, Doctor, Lab Tech, Patient, Admin)
- **Add User:** Create new staff (Doctor/Lab Tech) or Patient accounts
  - Fields: Username, Email, Password, Role, Name, Phone
  - Password is hashed using SHA256
  - Validates duplicate email/username
- **Edit User:** Update user role, phone, name
- **Delete User:** Remove users (prevents deleting ADMIN accounts)

**How it works:**
- Uses `users` table with role ENUM (ADMIN, DOCTOR, LAB_TECH, PATIENT)
- Role mapping converts lowercase to uppercase ENUM values
- AJAX-based forms for seamless updates

### 3. **Symptom Management** (`/admin/symptoms`)
**Features:**
- **View Symptoms:** List all symptoms with frequency analytics
- **Add Symptom:** Add new symptoms to database
- **Delete Symptom:** Remove symptoms by ID
- **Search Symptoms:** Prefix-based search using C++ DSA (Binary Search Tree)

**How it works:**
- Uses `symptoms` table
- Integrates with C++ `SymptomManager` for efficient search
- Tracks symptom frequency from `patient_symptoms` table
- DSA provides O(log n) search performance

### 4. **Analytics** (`/admin/analytics`)
**Features:**
- **Disease Distribution:** Count of predictions per disease
- **Risk Level Distribution:** HIGH_RISK vs LOW_RISK predictions
- **Staff Predictions:** Prediction count per staff member

**How it works:**
- Queries `predictions` table joined with `disease_models` and `users`
- Groups by disease_name and risk_level
- Aggregates by staff_id from `patient_reports`

### 5. **Disease Detection** (`/admin/disease-detection`)
**Features:**
- Select disease type (Diabetes, Heart Disease, Breast Cancer)
- Manual input form for disease-specific parameters
- View prediction results

**How it works:**
- Uses `PredictionEngine` with ML models
- Form fields defined in `DISEASE_CONFIG`
- Returns prediction (0=Negative, 1=Positive) with confidence

---

## 👨‍⚕️ STAFF ROLE FEATURES (DOCTOR/LAB_TECH)

### 1. **Dashboard** (`/staff/dashboard`)
**How it works:**
- Shows statistics: Total patients, Total reports, Total predictions
- Lists recent reports (last 10)
- **Access:** DOCTOR, LAB_TECH, ADMIN roles

### 2. **View Patients** (`/staff/patients`)
**How it works:**
- Lists all patients from `users` table where role='PATIENT'
- Shows patient profiles with basic info

### 3. **View Reports** (`/staff/reports`)
**How it works:**
- Lists all patient reports from `patient_reports` table
- Shows report type, patient, date, staff who created it
- Links to run predictions on reports

### 4. **Upload Report** (`/staff/reports/upload`)
**Features:**
- Upload medical reports (PDF, Image, CSV)
- Select patient from dropdown
- Add notes
- Manual test data entry (JSON format)

**How it works:**
- **File Upload:** Saves to `uploads/` folder
- **CSV Parsing:** Extracts parameters using normalized names
- **OCR Processing:** For PDF/Images, uses `OCRParser` to extract:
  - Text extraction from images/PDFs
  - Pattern matching for disease parameters
  - Parameter normalization using `MedicalHashMap`
- **Test Data Storage:** Saves to `report_tests` table
- **Report Creation:** Creates entry in `patient_reports` table
- Redirects to prediction page after upload

### 5. **Run Prediction** (`/staff/reports/<id>/predict`)
**Features:**
- Select symptoms (checkboxes + text input)
- Choose prediction type: All diseases or specific (Diabetes/Heart/Breast Cancer)
- View comprehensive results

**How it works:**
- **All Diseases Mode:**
  - Loads C++ Decision Tree models for all 3 diseases
  - Extracts features from test data using disease configs
  - Normalizes parameter names
  - Uses default values for missing parameters
  - Runs predictions using C++ models
  - Checks symptom-disease correlation
  - Calculates risk scores based on:
    - Symptom matches
    - Abnormal parameter values
    - Prediction confidence
  - Saves predictions to `predictions` table
- **Specific Disease Mode:**
  - Loads single C++ model
  - Extracts features for that disease
  - Makes prediction
  - Saves to database

### 6. **View Thresholds** (`/staff/thresholds`)
**How it works:**
- Lists all disease thresholds from `disease_thresholds` table
- Shows parameter ranges for each disease

### 7. **Add Threshold** (`/staff/thresholds/add`)
**How it works:**
- Creates new threshold entry
- Links to disease and defines min/max values for parameters
- Used for risk assessment

### 8. **Disease Detection** (`/staff/disease-detection`)
**Same as Admin** - Manual prediction forms

---

## 👤 PATIENT ROLE FEATURES

### 1. **Dashboard** (`/patient/dashboard`)
**How it works:**
- Shows patient profile info
- Displays recent reports (last 5)
- Shows recent predictions (last 5)
- Statistics: Total reports, Total predictions

### 2. **View Reports** (`/patient/reports`)
**How it works:**
- Lists all reports for logged-in patient
- Filtered by `patient_id` from session
- Shows report type, date, notes

### 3. **Report Details** (`/patient/reports/<id>`)
**Features:**
- View full report information
- See all test parameters and values
- View predictions for that report
- Trend analysis comparing with historical reports

**How it works:**
- Fetches report, tests, and predictions
- Compares current test data with historical data
- Uses `PredictionEngine.analyze_trends()` to detect:
  - Improving trends
  - Worsening trends
  - Stable values

### 4. **View Predictions** (`/patient/predictions`)
**How it works:**
- Lists all predictions for the patient
- Shows disease, result, confidence, date
- Filtered by patient_id

### 5. **Trends Analysis** (`/patient/trends`)
**How it works:**
- Analyzes all historical reports
- Compares parameter values over time
- Identifies trends (improving/worsening/stable)
- Requires at least 2 reports for comparison

### 6. **Medical Summary** (`/patient/summary`)
**Features:**
- Printable/downloadable summary
- Includes profile, all reports, all predictions
- Print-friendly format

**How it works:**
- Aggregates all patient data
- Formats for printing
- Uses browser print functionality

### 7. **Disease Detection** (`/patient/disease-detection`)
**Same as Admin/Staff** - Manual prediction forms

---

## 🔧 TECHNICAL IMPLEMENTATION DETAILS

### Authentication Flow
1. User logs in via `/auth/login`
2. Credentials verified using `UserDAO.verify_password()`
3. Session stores: `user_id`, `role`, `name`
4. Role-based decorators (`@admin_required`, `@staff_required`, `@patient_required`) protect routes

### Database Schema
- **users:** User accounts (id, username, email, password, role, phone, name, status)
- **patient_profiles:** Extended patient info
- **patient_reports:** Medical reports (links to patient, staff, file path)
- **report_tests:** Test parameters and values per report
- **predictions:** Disease predictions (links to report, disease, result, confidence)
- **symptoms:** Available symptoms
- **patient_symptoms:** Symptom-disease mappings
- **disease_models:** Disease configurations
- **disease_thresholds:** Parameter ranges for diseases

### Prediction Engine
- **C++ Integration:** Decision Tree models loaded from `models/` folder
- **ML Models:** Python-based models as fallback
- **DSA Components:**
  - Binary Search Tree for symptom search
  - Hash Map for parameter normalization
  - Priority Queue for risk scoring

### OCR Processing
- Extracts text from PDF/Images
- Pattern matching for parameter extraction
- Normalizes parameter names (e.g., "Blood Sugar" → "glucose")
- Handles multiple disease types in single report

---

## 🔄 DATA FLOW EXAMPLES

### Report Upload → Prediction Flow:
1. Staff uploads report file
2. System extracts test data (CSV/OCR)
3. Test data saved to `report_tests`
4. Staff selects symptoms and prediction type
5. System loads C++ models
6. Features extracted and normalized
7. Predictions made for selected diseases
8. Results saved to `predictions` table
9. Patient can view results in their dashboard

### Symptom Search Flow:
1. Admin types symptom prefix
2. Frontend sends AJAX request
3. Backend loads all symptoms from DB
4. C++ SymptomManager performs binary search
5. Returns matching symptoms
6. Displayed in dropdown

---

## 🎯 KEY FEATURES SUMMARY

| Feature | Admin | Staff | Patient |
|---------|-------|-------|---------|
| Dashboard | ✅ | ✅ | ✅ |
| User Management | ✅ | ❌ | ❌ |
| Symptom Management | ✅ | ❌ | ❌ |
| Analytics | ✅ | ❌ | ❌ |
| Upload Reports | ❌ | ✅ | ❌ |
| Run Predictions | ❌ | ✅ | ❌ |
| View Reports | ❌ | ✅ | ✅ |
| View Predictions | ❌ | ❌ | ✅ |
| Trends Analysis | ❌ | ❌ | ✅ |
| Medical Summary | ❌ | ❌ | ✅ |
| Disease Detection | ✅ | ✅ | ✅ |

