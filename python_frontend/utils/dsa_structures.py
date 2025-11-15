"""
Data Structures and Algorithms implementations for medical analysis.
Includes Stack, PriorityQueue, and MedicalHashMap for disease prediction system.
"""


class Stack:
    """
    Stack implementation to store patient's last N reports for trend analysis.
    Uses LIFO (Last In First Out) principle.
    """
    
    def __init__(self, max_size=5):
        """Initialize stack with maximum size."""
        self.items = []
        self.max_size = max_size
    
    def push(self, item):
        """Push item onto stack. Removes oldest if stack is full."""
        self.items.append(item)
        if len(self.items) > self.max_size:
            self.items.pop(0)  # Remove oldest item
    
    def pop(self):
        """Pop and return top item from stack."""
        if self.is_empty():
            return None
        return self.items.pop()
    
    def peek(self):
        """Return top item without removing it."""
        if self.is_empty():
            return None
        return self.items[-1]
    
    def is_empty(self):
        """Check if stack is empty."""
        return len(self.items) == 0
    
    def size(self):
        """Return number of items in stack."""
        return len(self.items)
    
    def get_all(self):
        """Get all items in stack (oldest to newest)."""
        return self.items.copy()
    
    def clear(self):
        """Clear all items from stack."""
        self.items = []


class PriorityQueue:
    """
    Priority Queue implementation to rank diseases by risk score.
    Higher priority (risk score) items are dequeued first.
    """
    
    def __init__(self):
        """Initialize priority queue."""
        self.items = []
    
    def enqueue(self, item, priority):
        """
        Add item to queue with priority.
        Priority: higher number = higher risk = dequeued first.
        """
        self.items.append((priority, item))
        # Sort by priority (descending - highest risk first)
        self.items.sort(key=lambda x: x[0], reverse=True)
    
    def dequeue(self):
        """Remove and return highest priority item."""
        if self.is_empty():
            return None
        return self.items.pop(0)[1]  # Return item (not priority)
    
    def peek(self):
        """Return highest priority item without removing it."""
        if self.is_empty():
            return None
        return self.items[0][1]
    
    def is_empty(self):
        """Check if queue is empty."""
        return len(self.items) == 0
    
    def size(self):
        """Return number of items in queue."""
        return len(self.items)
    
    def get_all(self):
        """Get all items sorted by priority (highest first)."""
        return [(priority, item) for priority, item in self.items]
    
    def clear(self):
        """Clear all items from queue."""
        self.items = []


class MedicalHashMap:
    """
    Hash Map implementation for medical term and symptom-disease mappings.
    Provides O(1) average case lookup time.
    """
    
    def __init__(self, initial_capacity=16):
        """Initialize hash map with initial capacity."""
        self.capacity = initial_capacity
        self.buckets = [[] for _ in range(self.capacity)]
        self.size = 0
    
    def _hash(self, key):
        """Generate hash value for key."""
        if isinstance(key, str):
            # Simple hash function for strings
            hash_value = 0
            for char in key.lower():
                hash_value = (hash_value * 31 + ord(char)) % self.capacity
            return hash_value
        return hash(key) % self.capacity
    
    def put(self, key, value):
        """Insert or update key-value pair."""
        index = self._hash(key)
        bucket = self.buckets[index]
        
        # Check if key already exists
        for i, (k, v) in enumerate(bucket):
            if k == key:
                bucket[i] = (key, value)
                return
        
        # Add new key-value pair
        bucket.append((key, value))
        self.size += 1
        
        # Resize if load factor > 0.75
        if self.size > self.capacity * 0.75:
            self._resize()
    
    def get(self, key, default=None):
        """Get value for key, return default if not found."""
        index = self._hash(key)
        bucket = self.buckets[index]
        
        for k, v in bucket:
            if k == key:
                return v
        
        return default
    
    def contains(self, key):
        """Check if key exists in map."""
        return self.get(key) is not None
    
    def _resize(self):
        """Double capacity and rehash all items."""
        old_buckets = self.buckets
        self.capacity *= 2
        self.buckets = [[] for _ in range(self.capacity)]
        self.size = 0
        
        for bucket in old_buckets:
            for key, value in bucket:
                self.put(key, value)
    
    def keys(self):
        """Get all keys in the map."""
        keys_list = []
        for bucket in self.buckets:
            for key, value in bucket:
                keys_list.append(key)
        return keys_list
    
    def values(self):
        """Get all values in the map."""
        values_list = []
        for bucket in self.buckets:
            for key, value in bucket:
                values_list.append(value)
        return values_list
    
    def items(self):
        """Get all key-value pairs in the map."""
        items_list = []
        for bucket in self.buckets:
            for key, value in bucket:
                items_list.append((key, value))
        return items_list
    
    def clear(self):
        """Clear all items from map."""
        self.buckets = [[] for _ in range(self.capacity)]
        self.size = 0

