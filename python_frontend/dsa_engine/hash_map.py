"""
HashMap implementation for disease thresholds.
Provides O(1) average case lookup for medical thresholds.
"""


class MedicalHashMap:
    """Hash Map implementation for medical term and threshold mappings."""
    
    def __init__(self, initial_capacity=16, load_factor=0.75):
        """Initialize hash map with initial capacity and load factor."""
        self.capacity = initial_capacity
        self.load_factor = load_factor
        self.buckets = [[] for _ in range(self.capacity)]
        self.size = 0
    
    def _hash(self, key):
        """Generate hash value for key."""
        if isinstance(key, str):
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
        
        # Resize if load factor exceeded
        if self.size > self.capacity * self.load_factor:
            self._resize()
    
    def get(self, key, default=None):
        """Get value for key, return default if not found."""
        index = self._hash(key)
        bucket = self.buckets[index]
        
        for k, v in bucket:
            if k == key:
                return v
        
        return default
    
    def remove(self, key):
        """Remove key-value pair."""
        index = self._hash(key)
        bucket = self.buckets[index]
        
        for i, (k, v) in enumerate(bucket):
            if k == key:
                bucket.pop(i)
                self.size -= 1
                return True
        
        return False
    
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
    
    def __len__(self):
        """Return size of map."""
        return self.size
    
    def __contains__(self, key):
        """Support 'in' operator."""
        return self.contains(key)
    
    def __getitem__(self, key):
        """Support indexing."""
        value = self.get(key)
        if value is None:
            raise KeyError(key)
        return value
    
    def __setitem__(self, key, value):
        """Support assignment."""
        self.put(key, value)
    
    def __str__(self):
        """String representation."""
        items = self.items()
        return "{" + ", ".join(f"{k}: {v}" for k, v in items) + "}"

