"""
Set implementation for managing symptoms.
Used for efficient symptom membership testing.
"""


class MedicalSet:
    """Set data structure for managing unique symptoms."""
    
    def __init__(self, initial_capacity=16):
        """Initialize set with initial capacity."""
        self.capacity = initial_capacity
        self.buckets = [[] for _ in range(self.capacity)]
        self.size = 0
    
    def _hash(self, item):
        """Generate hash value for item."""
        if isinstance(item, str):
            hash_value = 0
            for char in item.lower():
                hash_value = (hash_value * 31 + ord(char)) % self.capacity
            return hash_value
        return hash(item) % self.capacity
    
    def add(self, item):
        """Add item to set if not already present."""
        index = self._hash(item)
        bucket = self.buckets[index]
        
        # Check if item already exists
        for existing_item in bucket:
            if existing_item == item:
                return  # Item already in set
        
        # Add new item
        bucket.append(item)
        self.size += 1
        
        # Resize if needed
        if self.size > self.capacity * 0.75:
            self._resize()
    
    def remove(self, item):
        """Remove item from set."""
        index = self._hash(item)
        bucket = self.buckets[index]
        
        for i, existing_item in enumerate(bucket):
            if existing_item == item:
                bucket.pop(i)
                self.size -= 1
                return True
        
        return False
    
    def contains(self, item):
        """Check if item is in set."""
        index = self._hash(item)
        bucket = self.buckets[index]
        
        for existing_item in bucket:
            if existing_item == item:
                return True
        
        return False
    
    def union(self, other_set):
        """Return union of this set and other_set."""
        result = MedicalSet()
        
        for item in self:
            result.add(item)
        
        for item in other_set:
            result.add(item)
        
        return result
    
    def intersection(self, other_set):
        """Return intersection of this set and other_set."""
        result = MedicalSet()
        
        for item in self:
            if other_set.contains(item):
                result.add(item)
        
        return result
    
    def difference(self, other_set):
        """Return difference of this set and other_set."""
        result = MedicalSet()
        
        for item in self:
            if not other_set.contains(item):
                result.add(item)
        
        return result
    
    def _resize(self):
        """Double capacity and rehash all items."""
        old_buckets = self.buckets
        self.capacity *= 2
        self.buckets = [[] for _ in range(self.capacity)]
        self.size = 0
        
        for bucket in old_buckets:
            for item in bucket:
                self.add(item)
    
    def to_list(self):
        """Convert set to Python list."""
        result = []
        for bucket in self.buckets:
            result.extend(bucket)
        return result
    
    def clear(self):
        """Clear all items from set."""
        self.buckets = [[] for _ in range(self.capacity)]
        self.size = 0
    
    def __len__(self):
        """Return size of set."""
        return self.size
    
    def __contains__(self, item):
        """Support 'in' operator."""
        return self.contains(item)
    
    def __iter__(self):
        """Make set iterable."""
        for bucket in self.buckets:
            for item in bucket:
                yield item
    
    def __str__(self):
        """String representation."""
        items = self.to_list()
        return "{" + ", ".join(str(item) for item in items) + "}"

