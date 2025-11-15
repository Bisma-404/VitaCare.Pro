"""
Array implementation for storing test results.
Used for managing medical test data efficiently.
"""


class MedicalArray:
    """Array data structure for storing medical test results."""
    
    def __init__(self, initial_capacity=10):
        """Initialize array with initial capacity."""
        self.capacity = initial_capacity
        self.data = [None] * self.capacity
        self.size = 0
    
    def append(self, item):
        """Add item to the end of array."""
        if self.size >= self.capacity:
            self._resize()
        self.data[self.size] = item
        self.size += 1
    
    def insert(self, index, item):
        """Insert item at specific index."""
        if index < 0 or index > self.size:
            raise IndexError("Index out of range")
        
        if self.size >= self.capacity:
            self._resize()
        
        # Shift elements to the right
        for i in range(self.size, index, -1):
            self.data[i] = self.data[i - 1]
        
        self.data[index] = item
        self.size += 1
    
    def get(self, index):
        """Get item at index."""
        if index < 0 or index >= self.size:
            raise IndexError("Index out of range")
        return self.data[index]
    
    def set(self, index, item):
        """Set item at index."""
        if index < 0 or index >= self.size:
            raise IndexError("Index out of range")
        self.data[index] = item
    
    def remove(self, index):
        """Remove item at index."""
        if index < 0 or index >= self.size:
            raise IndexError("Index out of range")
        
        item = self.data[index]
        
        # Shift elements to the left
        for i in range(index, self.size - 1):
            self.data[i] = self.data[i + 1]
        
        self.size -= 1
        self.data[self.size] = None
        return item
    
    def find(self, item):
        """Find index of item, return -1 if not found."""
        for i in range(self.size):
            if self.data[i] == item:
                return i
        return -1
    
    def _resize(self):
        """Double the capacity of array."""
        self.capacity *= 2
        new_data = [None] * self.capacity
        for i in range(self.size):
            new_data[i] = self.data[i]
        self.data = new_data
    
    def to_list(self):
        """Convert array to Python list."""
        return [self.data[i] for i in range(self.size)]
    
    def __len__(self):
        """Return size of array."""
        return self.size
    
    def __getitem__(self, index):
        """Support indexing."""
        return self.get(index)
    
    def __setitem__(self, index, value):
        """Support assignment."""
        self.set(index, value)
    
    def __str__(self):
        """String representation."""
        return str(self.to_list())

