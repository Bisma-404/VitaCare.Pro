"""
Python wrapper for C++ DSA structures.
This module provides a Python interface to the C++ DSA implementations.
"""

import sys
import os

# Try to import C++ DSA structures from cpp_tree module (same as decision tree)
try:
    import cpp_tree
    CPP_DSA_AVAILABLE = True
except ImportError:
    print("Warning: cpp_tree module not found. Using Python fallback implementations.")
    CPP_DSA_AVAILABLE = False
    cpp_tree = None


class HashMap:
    """Wrapper for C++ HashMap."""
    
    def __init__(self, initial_capacity=16):
        if CPP_DSA_AVAILABLE:
            self._cpp_map = cpp_tree.HashMap()
        else:
            from utils.dsa_structures import MedicalHashMap
            self._cpp_map = MedicalHashMap()
            self._is_python = True
    
    def put(self, key, value):
        """Insert or update key-value pair."""
        if CPP_DSA_AVAILABLE:
            self._cpp_map.put(str(key), str(value))
        else:
            self._cpp_map.put(str(key), str(value))
    
    def get(self, key, default=None):
        """Get value for key."""
        if CPP_DSA_AVAILABLE:
            result = self._cpp_map.get(str(key), "")
            return result if result else default
        else:
            return self._cpp_map.get(str(key), default)
    
    def contains(self, key):
        """Check if key exists."""
        if CPP_DSA_AVAILABLE:
            return self._cpp_map.contains(str(key))
        else:
            return self._cpp_map.contains(str(key))
    
    def clear(self):
        """Clear all items."""
        self._cpp_map.clear()
    
    def size(self):
        """Get number of items."""
        return self._cpp_map.size()


class Stack:
    """Wrapper for C++ Stack."""
    
    def __init__(self, max_size=5):
        if CPP_DSA_AVAILABLE:
            self._cpp_stack = cpp_tree.StringStack(max_size)
        else:
            from utils.dsa_structures import Stack as PyStack
            self._cpp_stack = PyStack(max_size)
            self._is_python = True
    
    def push(self, item):
        """Push item onto stack."""
        self._cpp_stack.push(str(item))
    
    def pop(self):
        """Pop and return top item."""
        return self._cpp_stack.pop()
    
    def peek(self):
        """Get top item without removing."""
        return self._cpp_stack.peek()
    
    def is_empty(self):
        """Check if empty."""
        return self._cpp_stack.is_empty()
    
    def size(self):
        """Get number of items."""
        return self._cpp_stack.size()
    
    def clear(self):
        """Clear all items."""
        self._cpp_stack.clear()
    
    def get_all(self):
        """Get all items."""
        return self._cpp_stack.get_all()


class Queue:
    """Wrapper for C++ Queue."""
    
    def __init__(self):
        if CPP_DSA_AVAILABLE:
            self._cpp_queue = cpp_tree.StringQueue()
        else:
            from utils.dsa_structures import Queue as PyQueue
            self._cpp_queue = PyQueue()
            self._is_python = True
    
    def enqueue(self, item):
        """Add item to queue."""
        self._cpp_queue.enqueue(str(item))
    
    def dequeue(self):
        """Remove and return front item."""
        return self._cpp_queue.dequeue()
    
    def peek(self):
        """Get front item without removing."""
        return self._cpp_queue.peek()
    
    def is_empty(self):
        """Check if empty."""
        return self._cpp_queue.is_empty()
    
    def size(self):
        """Get number of items."""
        return self._cpp_queue.size()
    
    def clear(self):
        """Clear all items."""
        self._cpp_queue.clear()


class PriorityQueue:
    """Wrapper for C++ PriorityQueue."""
    
    def __init__(self, max_heap=True):
        if CPP_DSA_AVAILABLE:
            self._cpp_pq = cpp_tree.PriorityQueue(max_heap)
        else:
            from utils.dsa_structures import PriorityQueue as PyPQ
            self._cpp_pq = PyPQ()
            self._is_python = True
    
    def enqueue(self, item, priority):
        """Add item with priority."""
        if CPP_DSA_AVAILABLE:
            # Create PriorityItem
            priority_item = cpp_tree.PriorityItem(
                item.get('disease_type', ''),
                item.get('disease_name', ''),
                item.get('prediction', 0),
                float(priority),
                item.get('risk_level', '')
            )
            self._cpp_pq.enqueue(priority_item)
        else:
            self._cpp_pq.enqueue(item, priority)
    
    def dequeue(self):
        """Remove and return highest priority item."""
        if CPP_DSA_AVAILABLE:
            item = self._cpp_pq.dequeue()
            return {
                'disease_type': item.disease_type,
                'disease_name': item.disease_name,
                'prediction': item.prediction,
                'risk_score': item.risk_score,
                'risk_level': item.risk_level
            }
        else:
            return self._cpp_pq.dequeue()
    
    def peek(self):
        """Get highest priority item without removing."""
        if CPP_DSA_AVAILABLE:
            item = self._cpp_pq.peek()
            return {
                'disease_type': item.disease_type,
                'disease_name': item.disease_name,
                'prediction': item.prediction,
                'risk_score': item.risk_score,
                'risk_level': item.risk_level
            }
        else:
            return self._cpp_pq.peek()
    
    def is_empty(self):
        """Check if empty."""
        return self._cpp_pq.is_empty()
    
    def size(self):
        """Get number of items."""
        return self._cpp_pq.size()
    
    def clear(self):
        """Clear all items."""
        self._cpp_pq.clear()


class SymptomDiseaseGraph:
    """Wrapper for C++ SymptomDiseaseGraph."""
    
    def __init__(self):
        if CPP_DSA_AVAILABLE:
            self._cpp_graph = cpp_tree.SymptomDiseaseGraph()
        else:
            from dsa_engine.graphs import SymptomDiseaseGraph as PyGraph
            self._cpp_graph = PyGraph()
            self._is_python = True
    
    def add_node(self, node, node_type):
        """Add a node to the graph."""
        self._cpp_graph.add_node(str(node), str(node_type))
    
    def add_edge(self, from_node, to_node, bidirectional=False):
        """Add an edge between nodes."""
        self._cpp_graph.add_edge(str(from_node), str(to_node), bidirectional)
    
    def get_diseases_for_symptom(self, symptom):
        """Get diseases associated with a symptom."""
        return self._cpp_graph.get_diseases_for_symptom(str(symptom))
    
    def get_symptoms_for_disease(self, disease):
        """Get symptoms associated with a disease."""
        return self._cpp_graph.get_symptoms_for_disease(str(disease))
    
    def has_node(self, node):
        """Check if node exists."""
        return self._cpp_graph.has_node(str(node))
    
    def clear(self):
        """Clear all nodes and edges."""
        self._cpp_graph.clear()
    
    def size(self):
        """Get number of nodes."""
        return self._cpp_graph.size()


class Set:
    """Wrapper for C++ Set."""
    
    def __init__(self):
        if CPP_DSA_AVAILABLE:
            self._cpp_set = cpp_tree.Set()
        else:
            from utils.dsa_structures import Set as PySet
            self._cpp_set = PySet()
            self._is_python = True
    
    def add(self, item):
        """Add item to set."""
        self._cpp_set.add(str(item))
    
    def remove(self, item):
        """Remove item from set."""
        self._cpp_set.remove(str(item))
    
    def contains(self, item):
        """Check if item exists."""
        return self._cpp_set.contains(str(item))
    
    def clear(self):
        """Clear all items."""
        self._cpp_set.clear()
    
    def size(self):
        """Get number of items."""
        return self._cpp_set.size()
    
    def to_vector(self):
        """Get all items as list."""
        return self._cpp_set.to_vector()

