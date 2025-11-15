#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include "decision_tree_simple.h"
namespace py = pybind11;

PYBIND11_MODULE(cpp_tree, m) {
    m.doc() = "Pure C++ Simple Decision Tree for demo/educational use.";

    py::class_<DataPointS>(m, "DataPoint")
        .def(py::init<>())
        .def(py::init<const std::vector<double>&, int>())
        .def_readwrite("features", &DataPointS::features)
        .def_readwrite("label", &DataPointS::label);

    py::class_<SimpleDecisionTree>(m, "DecisionTree")
        .def(py::init<>())
        .def("train", &SimpleDecisionTree::train,
             py::arg("data"), py::arg("max_depth") = 3, py::arg("min_samples") = 2, py::arg("criterion") = "entropy",
             "Train the decision tree")
        .def("predict", &SimpleDecisionTree::predict, py::arg("features"), "Predict the class for a single sample")
        .def("predict_batch", &SimpleDecisionTree::predictBatch, py::arg("features_batch"), "Predict classes for multiple samples")
        .def("save", &SimpleDecisionTree::save, py::arg("path"), "Save tree to a file")
        .def("load", &SimpleDecisionTree::load, py::arg("path"), "Load tree from a file");
}