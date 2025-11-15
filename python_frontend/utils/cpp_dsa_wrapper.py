"""
Python wrapper for C++ DSA structures.
This module provides a Python interface to the C++ DSA implementations.
Uses C++ classes directly via using-directive style.
"""

import json
from decimal import Decimal


class DecimalEncoder(json.JSONEncoder):
    """Custom JSON encoder to handle Decimal types."""
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        return super().default(obj)


# Using-directive style imports - direct access to C++ classes
from cpp_tree import (
    HashMap,
    StringStack,
    StringQueue,
    PriorityQueue,
    PriorityItem,
    SymptomDiseaseGraph,
    Set,
    StringLinkedList
)


class Stack:
    """Wrapper for C++ Stack."""
    
    def __init__(self, max_size=5):
        self._stack = StringStack(max_size)
    
    def push(self, item):
        """Push item onto stack."""
        self._stack.push(str(item))
    
    def pop(self):
        """Pop and return top item."""
        return self._stack.pop()
    
    def peek(self):
        """Get top item without removing."""
        return self._stack.peek()
    
    def is_empty(self):
        """Check if empty."""
        return self._stack.is_empty()
    
    def size(self):
        """Get number of items."""
        return self._stack.size()
    
    def clear(self):
        """Clear all items."""
        self._stack.clear()
    
    def get_all(self):
        """Get all items."""
        return self._stack.get_all()


class Queue:
    """Wrapper for C++ Queue."""
    
    def __init__(self):
        self._queue = StringQueue()
    
    def enqueue(self, item):
        """Add item to queue."""
        self._queue.enqueue(str(item))
    
    def dequeue(self):
        """Remove and return front item."""
        return self._queue.dequeue()
    
    def peek(self):
        """Get front item without removing."""
        return self._queue.peek()
    
    def is_empty(self):
        """Check if empty."""
        return self._queue.is_empty()
    
    def size(self):
        """Get number of items."""
        return self._queue.size()
    
    def clear(self):
        """Clear all items."""
        self._queue.clear()


class MedicalPriorityQueue:
    """Wrapper for C++ PriorityQueue."""
    
    def __init__(self, max_heap=True):
        self._pq = PriorityQueue(max_heap)
    
    def enqueue(self, item, priority):
        """Add item with priority."""
        # Create PriorityItem from the item dictionary
        priority_item = PriorityItem(
            item.get('disease_type', ''),
            item.get('disease_name', ''),
            item.get('prediction', 0),
            float(priority),
            item.get('risk_level', '')
        )
        self._pq.enqueue(priority_item)
    
    def dequeue(self):
        """Remove and return highest priority item."""
        item = self._pq.dequeue()
        return {
            'disease_type': item.disease_type,
            'disease_name': item.disease_name,
            'prediction': item.prediction,
            'risk_score': item.risk_score,
            'risk_level': item.risk_level
        }
    
    def peek(self):
        """Get highest priority item without removing."""
        item = self._pq.peek()
        return {
            'disease_type': item.disease_type,
            'disease_name': item.disease_name,
            'prediction': item.prediction,
            'risk_score': item.risk_score,
            'risk_level': item.risk_level
        }
    
    def is_empty(self):
        """Check if empty."""
        return self._pq.is_empty()
    
    def size(self):
        """Get number of items."""
        return self._pq.size()
    
    def clear(self):
        """Clear all items."""
        self._pq.clear()


class MedicalHashMap:
    """Wrapper for C++ HashMap with JSON serialization support."""
    
    def __init__(self, initial_capacity=16):
        self._map = HashMap()
    
    def put(self, key, value):
        """Insert or update key-value pair.
        Automatically serializes complex types (dict, list) to JSON strings.
        """
        str_key = str(key)
        # Convert value to string - if it's a dict or list, use JSON
        if isinstance(value, (dict, list)):
            str_value = json.dumps(value, cls=DecimalEncoder)
        else:
            str_value = str(value)
        self._map.put(str_key, str_value)
    
    def get(self, key, default=None):
        """Get value for key.
        Automatically deserializes JSON strings back to Python objects when possible.
        """
        result = self._map.get(str(key), "")
        if not result:
            return default
        
        # Try to deserialize if it looks like JSON
        if result.startswith(('{', '[')):
            try:
                return json.loads(result)
            except (json.JSONDecodeError, ValueError):
                pass
        
        return result
    
    def contains(self, key):
        """Check if key exists."""
        return self._map.contains(str(key))
    
    def clear(self):
        """Clear all items."""
        self._map.clear()
    
    def size(self):
        """Get number of items."""
        return self._map.size()


class SymptomDiseaseGraphWrapper:
    """Wrapper for C++ SymptomDiseaseGraph."""
    
    def __init__(self):
        self._graph = SymptomDiseaseGraph()
    
    def add_node(self, node, node_type):
        """Add a node to the graph."""
        self._graph.add_node(str(node), str(node_type))
    
    def add_edge(self, from_node, to_node, bidirectional=False):
        """Add an edge between nodes."""
        self._graph.add_edge(str(from_node), str(to_node), bidirectional)
    
    def get_diseases_for_symptom(self, symptom):
        """Get diseases associated with a symptom."""
        return self._graph.get_diseases_for_symptom(str(symptom))
    
    def get_symptoms_for_disease(self, disease):
        """Get symptoms associated with a disease."""
        return self._graph.get_symptoms_for_disease(str(disease))
    
    def has_node(self, node):
        """Check if node exists."""
        return self._graph.has_node(str(node))
    
    def clear(self):
        """Clear all nodes and edges."""
        self._graph.clear()
    
    def size(self):
        """Get number of nodes."""
        return self._graph.size()


class MedicalSet:
    """Wrapper for C++ Set."""
    
    def __init__(self):
        self._set = Set()
    
    def add(self, item):
        """Add item to set."""
        self._set.add(str(item))
    
    def remove(self, item):
        """Remove item from set."""
        self._set.remove(str(item))
    
    def contains(self, item):
        """Check if item exists."""
        return self._set.contains(str(item))
    
    def clear(self):
        """Clear all items."""
        self._set.clear()
    
    def size(self):
        """Get number of items."""
        return self._set.size()
    
    def to_vector(self):
        """Get all items as list."""
        return self._set.to_vector()


class MedicalLinkedList:
    """Wrapper for C++ LinkedList."""
    
    def __init__(self):
        self._list = StringLinkedList()
    
    def append(self, item):
        """Add item to end."""
        self._list.append(str(item))
    
    def prepend(self, item):
        """Add item to beginning."""
        self._list.prepend(str(item))
    
    def remove(self, item):
        """Remove item."""
        self._list.remove(str(item))
    
    def contains(self, item):
        """Check if item exists."""
        return self._list.contains(str(item))
    
    def size(self):
        """Get number of items."""
        return self._list.size()
    
    def clear(self):
        """Clear all items."""
        self._list.clear()
    
    def to_vector(self):
        """Get all items as list."""
        return self._list.to_vector()
    
    def get(self, index):
        """Get item at index."""
        return self._list.get(index)


