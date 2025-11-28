cmake_minimum_required(VERSION 3.12)
project(MultiDiseaseDetection)

# Find Python
find_package(Python 3.13 REQUIRED COMPONENTS Interpreter Development)

# Find pybind11
execute_process(
    COMMAND ${Python_EXECUTABLE} -m pybind11 --includes
    OUTPUT_VARIABLE pybind11_INCLUDE_DIR
    OUTPUT_STRIP_TRAILING_WHITESPACE
)
include_directories(${pybind11_INCLUDE_DIR})

# Include directories
include_directories(Include ${Python_INCLUDE_DIRS})

# Source files
set(SOURCES
    src/decision_tree_simple.cpp
    src/dsa_structures.cpp
    src/advanced_dsa.cpp
    src/string_search.cpp
)

# Create library
add_library(decision_tree_lib ${SOURCES})

# Python module - includes both decision tree and DSA structures
# Get pybind11 module file location
execute_process(
    COMMAND ${Python_EXECUTABLE} -c "import pybind11; print(pybind11.get_cmake_dir())"
    OUTPUT_VARIABLE pybind11_CMAKE_DIR
    OUTPUT_STRIP_TRAILING_WHITESPACE
)
list(APPEND CMAKE_PREFIX_PATH "${pybind11_CMAKE_DIR}")

find_package(pybind11 CONFIG REQUIRED)

pybind11_add_module(cpp_tree src/bindings.cpp src/decision_tree_simple.cpp src/dsa_structures.cpp src/advanced_dsa.cpp src/string_search.cpp)

# Include directories for the module
target_include_directories(cpp_tree PRIVATE Include)

# Install the module
install(TARGETS cpp_tree DESTINATION ${CMAKE_SOURCE_DIR}/../python_frontend)