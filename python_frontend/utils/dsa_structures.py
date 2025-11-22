"""
Data Structures and Algorithms implementations for medical analysis.
Wrapper for C++ implementations via cpp_tree module.
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
try:
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
    CPP_AVAILABLE = True
except ImportError:
    print("Warning: cpp_tree module not found. Using Python fallback.")
    CPP_AVAILABLE = False


class Stack:
    """Wrapper for C++ Stack."""
    
    def __init__(self, max_size=5):
        if CPP_AVAILABLE:
            self._stack = StringStack(max_size)
        else:
            self._items = []
            self._max_size = max_size
    
    def push(self, item):
        """Push item onto stack."""
        if CPP_AVAILABLE:
            self._stack.push(str(item))
        else:
            self._items.append(item)
            if len(self._items) > self._max_size:
                self._items.pop(0)
    
    def pop(self):
        """Pop and return top item."""
        if CPP_AVAILABLE:
            return self._stack.pop()
        else:
            return self._items.pop() if self._items else None
    
    def peek(self):
        """Get top item without removing."""
        if CPP_AVAILABLE:
            return self._stack.peek()
        else:
            return self._items[-1] if self._items else None
    
    def is_empty(self):
        """Check if empty."""
        if CPP_AVAILABLE:
            return self._stack.is_empty()
        else:
            return len(self._items) == 0
    
    def size(self):
        """Get number of items."""
        if CPP_AVAILABLE:
            return self._stack.size()
        else:
            return len(self._items)
    
    def clear(self):
        """Clear all items."""
        if CPP_AVAILABLE:
            self._stack.clear()
        else:
            self._items = []
    
    def get_all(self):
        """Get all items."""
        if CPP_AVAILABLE:
            return self._stack.get_all()
        else:
            return self._items.copy()


class Queue:
    """Wrapper for C++ Queue."""
    
    def __init__(self):
        if CPP_AVAILABLE:
            self._queue = StringQueue()
        else:
            self._items = []
    
    def enqueue(self, item):
        """Add item to queue."""
        if CPP_AVAILABLE:
            self._queue.enqueue(str(item))
        else:
            self._items.append(item)
    
    def dequeue(self):
        """Remove and return front item."""
        if CPP_AVAILABLE:
            return self._queue.dequeue()
        else:
            return self._items.pop(0) if self._items else None
    
    def peek(self):
        """Get front item without removing."""
        if CPP_AVAILABLE:
            return self._queue.peek()
        else:
            return self._items[0] if self._items else None
    
    def is_empty(self):
        """Check if empty."""
        if CPP_AVAILABLE:
            return self._queue.is_empty()
        else:
            return len(self._items) == 0
    
    def size(self):
        """Get number of items."""
        if CPP_AVAILABLE:
            return self._queue.size()
        else:
            return len(self._items)
    
    def clear(self):
        """Clear all items."""
        if CPP_AVAILABLE:
            self._queue.clear()
        else:
            self._items = []


class PriorityQueue:
    """Wrapper for C++ PriorityQueue."""
    
    def __init__(self, max_heap=True):
        if CPP_AVAILABLE:
            self._pq = PriorityQueue(max_heap)
        else:
            self._items = []
            self._max_heap = max_heap
    
    def enqueue(self, item, priority):
        """Add item with priority."""
        if CPP_AVAILABLE:
            # Create PriorityItem from the item dictionary
            priority_item = PriorityItem(
                item.get('disease_type', ''),
                item.get('disease_name', ''),
                item.get('prediction', 0),
                float(priority),
                item.get('risk_level', '')
            )
            self._pq.enqueue(priority_item)
        else:
            self._items.append((priority, item))
            self._items.sort(key=lambda x: x[0], reverse=self._max_heap)
    
    def dequeue(self):
        """Remove and return highest priority item."""
        if CPP_AVAILABLE:
            item = self._pq.dequeue()
            return {
                'disease_type': item.disease_type,
                'disease_name': item.disease_name,
                'prediction': item.prediction,
                'risk_score': item.risk_score,
                'risk_level': item.risk_level
            }
        else:
            return self._items.pop(0)[1] if self._items else None
    
    def peek(self):
        """Get highest priority item without removing."""
        if CPP_AVAILABLE:
            item = self._pq.peek()
            return {
                'disease_type': item.disease_type,
                'disease_name': item.disease_name,
                'prediction': item.prediction,
                'risk_score': item.risk_score,
                'risk_level': item.risk_level
            }
        else:
            return self._items[0][1] if self._items else None
    
    def is_empty(self):
        """Check if empty."""
        if CPP_AVAILABLE:
            return self._pq.is_empty()
        else:
            return len(self._items) == 0
    
    def size(self):
        """Get number of items."""
        if CPP_AVAILABLE:
            return self._pq.size()
        else:
            return len(self._items)
    
    def clear(self):
        """Clear all items."""
        if CPP_AVAILABLE:
            self._pq.clear()
        else:
            self._items = []
            
    def get_all(self):
        """Get all items."""
        if CPP_AVAILABLE:
            # C++ returns vector of PriorityItem
            items = self._pq.get_all()
            result = []
            for item in items:
                result.append((item.risk_score, {
                    'disease_type': item.disease_type,
                    'disease_name': item.disease_name,
                    'prediction': item.prediction,
                    'risk_score': item.risk_score,
                    'risk_level': item.risk_level
                }))
            return result
        else:
            return self._items.copy()


class MedicalHashMap:
    """Wrapper for C++ HashMap with JSON serialization support."""
    
    def __init__(self, initial_capacity=16):
        if CPP_AVAILABLE:
            self._map = HashMap()
        else:
            self._map = {}
    
    def put(self, key, value):
        """Insert or update key-value pair."""
        if CPP_AVAILABLE:
            str_key = str(key)
            # Convert value to string - if it's a dict or list, use JSON
            if isinstance(value, (dict, list)):
                str_value = json.dumps(value, cls=DecimalEncoder)
            else:
                str_value = str(value)
            self._map.put(str_key, str_value)
        else:
            self._map[key] = value
    
    def get(self, key, default=None):
        """Get value for key."""
        if CPP_AVAILABLE:
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
        else:
            return self._map.get(key, default)
    
    def contains(self, key):
        """Check if key exists."""
        if CPP_AVAILABLE:
            return self._map.contains(str(key))
        else:
            return key in self._map
    
    def clear(self):
        """Clear all items."""
        if CPP_AVAILABLE:
            self._map.clear()
        else:
            self._map = {}
    
    def size(self):
        """Get number of items."""
        if CPP_AVAILABLE:
            return self._map.size()
        else:
            return len(self._map)
    
    def keys(self):
        """Get all keys."""
        if CPP_AVAILABLE:
            return self._map.keys()
        else:
            return list(self._map.keys())
            
    def values(self):
        """Get all values."""
        if CPP_AVAILABLE:
            return self._map.values()
        else:
            return list(self._map.values())
