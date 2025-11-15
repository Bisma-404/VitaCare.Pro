#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include "decision_tree_simple.h"
#include "../Include/dsa_structures.h"
namespace py = pybind11;

// Concrete types for pybind (templates can't be directly bound)
using StringStack = MedicalStack<std::string>;
using StringQueue = MedicalQueue<std::string>;
using StringLinkedList = MedicalLinkedList<std::string>;

PYBIND11_MODULE(cpp_tree, m) {
    m.doc() = "C++ Decision Tree and DSA structures for medical data management";

    // ========================================================================
    // DECISION TREE
    // ========================================================================
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

    // ========================================================================
    // DSA STRUCTURES
    // ========================================================================
    
    // HASH MAP
    py::class_<MedicalHashMap>(m, "HashMap")
        .def(py::init<>())
        .def("put", &MedicalHashMap::put, "Insert or update key-value pair")
        .def("get", &MedicalHashMap::get, py::arg("key"), py::arg("default_val") = "", "Get value for key")
        .def("contains", &MedicalHashMap::contains, "Check if key exists")
        .def("clear", &MedicalHashMap::clear, "Clear all items")
        .def("size", &MedicalHashMap::size, "Get number of items")
        .def("keys", &MedicalHashMap::keys, "Get all keys")
        .def("values", &MedicalHashMap::values, "Get all values");

    // PRIORITY QUEUE / HEAP
    py::class_<PriorityItem>(m, "PriorityItem")
        .def(py::init<>())
        .def(py::init<const std::string&, const std::string&, int, double, const std::string&>())
        .def_readwrite("disease_type", &PriorityItem::disease_type)
        .def_readwrite("disease_name", &PriorityItem::disease_name)
        .def_readwrite("prediction", &PriorityItem::prediction)
        .def_readwrite("risk_score", &PriorityItem::risk_score)
        .def_readwrite("risk_level", &PriorityItem::risk_level);

    py::class_<MedicalPriorityQueue>(m, "PriorityQueue")
        .def(py::init<bool>(), py::arg("max_heap") = true)
        .def("enqueue", &MedicalPriorityQueue::enqueue, "Add item with priority")
        .def("dequeue", &MedicalPriorityQueue::dequeue, "Remove highest priority item")
        .def("peek", &MedicalPriorityQueue::peek, "Get highest priority item without removing")
        .def("is_empty", &MedicalPriorityQueue::isEmpty, "Check if empty")
        .def("size", &MedicalPriorityQueue::size, "Get number of items")
        .def("clear", &MedicalPriorityQueue::clear, "Clear all items")
        .def("get_all", &MedicalPriorityQueue::getAll, "Get all items sorted by priority");

    // GRAPH
    py::class_<SymptomDiseaseGraph>(m, "SymptomDiseaseGraph")
        .def(py::init<>())
        .def("add_node", &SymptomDiseaseGraph::addNode, "Add a node to the graph")
        .def("add_edge", &SymptomDiseaseGraph::addEdge, 
             py::arg("from"), py::arg("to"), py::arg("bidirectional") = false,
             "Add an edge between nodes")
        .def("get_neighbors", &SymptomDiseaseGraph::getNeighbors, "Get neighbors of a node")
        .def("get_diseases_for_symptom", &SymptomDiseaseGraph::getDiseasesForSymptom, 
             "Get diseases associated with a symptom")
        .def("get_symptoms_for_disease", &SymptomDiseaseGraph::getSymptomsForDisease,
             "Get symptoms associated with a disease")
        .def("has_node", &SymptomDiseaseGraph::hasNode, "Check if node exists")
        .def("get_node_type", &SymptomDiseaseGraph::getNodeType, "Get type of node")
        .def("clear", &SymptomDiseaseGraph::clear, "Clear all nodes and edges")
        .def("size", &SymptomDiseaseGraph::size, "Get number of nodes");

    // SET
    py::class_<MedicalSet>(m, "Set")
        .def(py::init<>())
        .def("add", &MedicalSet::add, "Add item to set")
        .def("remove", &MedicalSet::remove, "Remove item from set")
        .def("contains", &MedicalSet::contains, "Check if item exists")
        .def("clear", &MedicalSet::clear, "Clear all items")
        .def("size", &MedicalSet::size, "Get number of items")
        .def("to_vector", &MedicalSet::toVector, "Get all items as vector");

    // STACK
    py::class_<StringStack>(m, "StringStack")
        .def(py::init<int>(), py::arg("max_size") = 5)
        .def("push", &StringStack::push, "Push item onto stack")
        .def("pop", &StringStack::pop, "Pop and return top item")
        .def("peek", &StringStack::peek, "Get top item without removing")
        .def("is_empty", &StringStack::isEmpty, "Check if empty")
        .def("size", &StringStack::size, "Get number of items")
        .def("clear", &StringStack::clear, "Clear all items")
        .def("get_all", &StringStack::getAll, "Get all items");

    // QUEUE
    py::class_<StringQueue>(m, "StringQueue")
        .def(py::init<>())
        .def("enqueue", &StringQueue::enqueue, "Add item to queue")
        .def("dequeue", &StringQueue::dequeue, "Remove and return front item")
        .def("peek", &StringQueue::peek, "Get front item without removing")
        .def("is_empty", &StringQueue::isEmpty, "Check if empty")
        .def("size", &StringQueue::size, "Get number of items")
        .def("clear", &StringQueue::clear, "Clear all items");

    // LINKED LIST
    py::class_<StringLinkedList>(m, "StringLinkedList")
        .def(py::init<>())
        .def("append", &StringLinkedList::append, "Add item to end")
        .def("prepend", &StringLinkedList::prepend, "Add item to beginning")
        .def("remove", &StringLinkedList::remove, "Remove item")
        .def("contains", &StringLinkedList::contains, "Check if item exists")
        .def("size", &StringLinkedList::size, "Get number of items")
        .def("clear", &StringLinkedList::clear, "Clear all items")
        .def("to_vector", &StringLinkedList::toVector, "Get all items as vector")
        .def("get", &StringLinkedList::get, "Get item at index");
}