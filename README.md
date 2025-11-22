# VitaCare Pro — Multi-Disease Detect Support System

**Overview**
- **What:** A medical support system that combines a C++-implemented Decision Tree + DSA (data structures & algorithms) core with a Python Flask frontend. It performs disease predictions, report OCR, threshold lookups and manages in-memory DSA structures (HashMap, Stack, Queue, PriorityQueue, Graph, Set, LinkedList).
- **Why:** High-performance core algorithms implemented in C++ (exposed to Python via pybind11) for fast lookups and ranking, while the Python frontend provides web UI, database access, and glue logic.

**Repository Layout (key folders)**
- `cpp_core/` — C++ source, headers, and CMake config. Produces `cpp_tree` Python extension module (pybind11).
  - `Include/` — `dsa_structures.h` and other headers.
  - `src/` — `dsa_structures.cpp`, `decision_tree_simple.cpp`, `bindings.cpp` (pybind11 bindings).
- `python_frontend/` — Flask application, utilities, prediction engine, wrappers and templates.
  - `utils/cpp_dsa_wrapper.py` — Python wrapper using direct imports from `cpp_tree` (using-directive style) and JSON serialization for complex values.
  - `webapp/` — OCR tools, templates, and helpers.
  - `predictions/` — `prediction_engine.py` that uses `MedicalHashMap`, `SymptomDiseaseGraph`, `MedicalPriorityQueue`, etc.
- `datasets/` — CSV datasets used for training / examples.

**Features & Design Notes**
- C++ DSA module (`cpp_tree`) exposes: `HashMap`, `StringStack`, `StringQueue`, `PriorityQueue`/`PriorityItem`, `SymptomDiseaseGraph`, `Set`, `StringLinkedList`, `DecisionTree`, `DataPoint`.
- Python wrapper uses *Using-Directive Style*: `from cpp_tree import HashMap, StringStack, ...` so code calls C++ classes directly.
- `MedicalHashMap` wrapper serializes Python dicts/lists (and converts `Decimal` to `float`) into JSON strings when storing into the C++ `HashMap`, and deserializes on retrieval.
- There is a fallback Python implementation in the repo, but the current recommended flow is to build and use the C++ `cpp_tree` extension for performance.

**Prerequisites**
- Windows (development done on Windows) or Linux/macOS with equivalent toolchain
- CMake 3.12+
- A C++ toolchain:
  - Windows: Visual Studio 2022 (with Desktop development with C++) or MSVC build tools
  - Linux/macOS: GCC or Clang
- Python 3.13 (the project uses that for local builds in this workspace)
- `pybind11` Python package
- `pytesseract` + Tesseract OCR installed for OCR features

**Quick Build & Install (C++ extension)**
Open a developer PowerShell (so MSVC tools are available) and run:

```powershell
cd cpp_core
mkdir build
cd build
cmake .. -G "Visual Studio 17 2022" -A x64 -DCMAKE_BUILD_TYPE=Release
cmake --build . --config Release
cmake --install . --config Release
```

- After `cmake --install`, the extension will be copied to `python_frontend/` (e.g. `cpp_tree.cp313-win_amd64.pyd`).
- If you develop on Linux/macOS, use an appropriate generator, e.g. `cmake ..` then `cmake --build .`.

# VitaCare Pro — Multi-Disease Detect Support System

## Overview
VitaCare Pro is a hybrid medical support system that combines a high-performance C++ DSA + Decision Tree core with a Python Flask frontend. It performs disease predictions (diabetes, heart disease, breast cancer), optional OCR of reports, and saves predictions to the database when available.

## Repository layout (high level)
- `cpp_core/` — C++ sources, pybind11 bindings and CMake configuration. Builds the `cpp_tree` extension used by the Python app.
- `python_frontend/` — Flask application, templates, prediction engine, DB models and utilities.
- `datasets/` — CSV files used to compute percentile thresholds and for evaluation.

Notable components inside `python_frontend`:
- `predictions/prediction_engine.py` — engine implementing DSA-first flow, percentile checks, clinical heuristics and ML fallback.
- `utils/` — helpers and wrappers for the C++ DSA extension.
- `templates/` — Jinja2 templates for Admin, Staff and Patient result pages.

## Key features
- DSA-first prediction flow with ML fallback.
- Dataset-driven percentile thresholds computed from CSVs.
- Disease-specific clinical heuristics that adjust a combined risk score and produce a short `remark` and a verbose `severity_reason`.
- Clean UI: templates present a concise `remark` and hide verbose technical details in a collapsible `Details` element.
- Optional OCR support via `pytesseract`.

## Prerequisites
- Python 3.11+ (3.13 used in development environment here)
- `pip` packages listed in `python_frontend/requirements.txt`
- CMake and a native C++ toolchain (to build `cpp_core` for best performance)
- Tesseract OCR (optional)

## Quick Python setup
1. Create and activate a virtual environment:

```powershell
cd python_frontend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

2. Place the built `cpp_tree` extension into `python_frontend/` or add it to `PYTHONPATH`.

3. Run the app:

```powershell
cd python_frontend
python app.py
```

The app serves on `http://127.0.0.1:5000` by default.

## Build C++ extension (brief)
On Windows with Visual Studio 2022 (example):

```powershell
cd cpp_core
mkdir build
cd build
cmake .. -G "Visual Studio 17 2022" -A x64 -DCMAKE_BUILD_TYPE=Release
cmake --build . --config Release
cmake --install . --config Release
```

Adjust generator and commands for other systems (Ninja, Makefiles, etc.). After install, copy the produced `.pyd`/`.so` file to `python_frontend` or make it available on `PYTHONPATH`.

## Notes & troubleshooting
- If templates show raw technical lines, the engine now provides a short `remark` and the full technical `severity_reason` is available under the Details block.
- The prediction engine ensures ML fallback results include DSA metadata so templates always receive `severity_label`, `severity_reason`, and `risk_score` when available.

## Next steps & contributions
- Add CI to build the C++ extension and run tests.
- Add unit tests for prediction rules and wrappers.
- Package `cpp_tree` as a wheel to simplify installation across systems.

---
Updated README — please refer to `FEATURES_DOCUMENTATION.md` for a more complete description of the prediction engine and design.