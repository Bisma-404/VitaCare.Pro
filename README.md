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

**Running the Python App (Flask)**
1. Set up a Python virtual environment and install requirements:

```powershell
cd python_frontend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

2. Ensure the `cpp_tree` module is present in `python_frontend/` (or on `PYTHONPATH`).
3. Run the app:

```powershell
cd python_frontend
python app.py
```

- App serves on `http://127.0.0.1:5000` by default.

**VS Code IntelliSense (pybind11 headers not found)**
If VS Code shows errors like `cannot open source file "pybind11/pybind11.h"` in `bindings.cpp`, add the pybind11 include path to your C/C++ properties. A `c_cpp_properties.json` has been added under `.vscode/` with an example include path:

- `C:/.../Python313/Lib/site-packages/pybind11/include`
- `cpp_core/Include`

If your Python or pybind11 is in a different location, update `.vscode/c_cpp_properties.json` accordingly.

**Troubleshooting**
- "module 'cpp_tree' has no attribute 'HashMap'": indicates the `cpp_tree` module was built earlier without the DSA bindings. Rebuild `cpp_core` and reinstall (see Build steps).
- `pybind11` related CMake errors: ensure `pybind11` is installed in the Python environment used by CMake (e.g. `pip install pybind11`).
- Unicode/emoji print errors on Windows console: the repo adjusts `sys.stdout` to UTF-8 in `webapp/ocr_utils.py` to avoid these issues.
- Database warnings such as `Unread result found` show up as runtime DB connection pool issues — these are separate from the C++ build and relate to DB use.

**Developer Notes**
- The code intentionally uses Using-Directive Style for the Python wrapper: it imports C++ classes directly (e.g. `from cpp_tree import HashMap`) to keep usage concise.
- `MedicalHashMap.put()` serializes dicts/lists into JSON strings and handles `Decimal` by converting to `float` so the C++ `HashMap` stores only strings.
- Preference is to run C++ DSA implementations; the repo includes Python fallback implementations for environments where compiling the C++ extension isn't possible.

**Recommended Next Steps**
- Add CI to automatically build the C++ extension and run Python smoke tests.
- Add unit tests for C++-backed wrappers (Python tests that exercise `MedicalHashMap`, `PriorityQueue`, etc.).
- Package the extension for easier install (wheel) if distributing.

**Contact & License**
- Project owner / maintainer: `abdulrafay1402` (local workspace user: `Abdul Rafay`)
- License: (not included) — add a `LICENSE` file if you intend to open-source this repo.

---
README created by the development assistant — run the C++ build steps above before starting the app to ensure the high-performance C++ DSA core is available.