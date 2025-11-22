cmake_minimum_required(VERSION 3.12)

# Include directories
include_directories(include)

# Source files
set(SOURCES
    src/decision_tree_simple.cpp
)

# Create library
add_library(decision_tree_lib ${SOURCES})

# Python module using only the simple version
pybind11_add_module(cpp_tree src/bindings.cpp src/decision_tree_simple.cpp)

# Include directories for the module
# No change needed; include/include already set.

# Install the module
install(TARGETS cpp_tree DESTINATION ${CMAKE_SOURCE_DIR}/python_frontend)