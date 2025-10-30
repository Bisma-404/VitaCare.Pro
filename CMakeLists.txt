cmake_minimum_required(VERSION 3.12)
project(MultiDiseaseDetection)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Find Python
find_package(Python COMPONENTS Interpreter Development REQUIRED)

# Find pybind11
find_package(pybind11 CONFIG REQUIRED)

# Add subdirectory for C++ core
add_subdirectory(cpp_core)