"""
Stack implementation for trend reversal analysis.
Used for analyzing medical parameter trends over time.
"""


class MedicalStack:
    """LIFO Stack for storing patient reports for trend analysis."""
    
    def __init__(self, max_size=None):
        """Initialize stack with optional maximum size."""
        self.items = []
        self.max_size = max_size
    
    def push(self, item):
        """Push item onto stack."""
        self.items.append(item)
        if self.max_size and len(self.items) > self.max_size:
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
    
    def get_reverse(self):
        """Get all items in reverse order (newest to oldest)."""
        return self.items[::-1]
    
    def clear(self):
        """Clear all items from stack."""
        self.items = []
    
    def __len__(self):
        """Return size of stack."""
        return len(self.items)
    
    def __iter__(self):
        """Make stack iterable (from oldest to newest)."""
        return iter(self.items)
    
    def __str__(self):
        """String representation."""
        return str(self.items)

