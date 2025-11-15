"""
Queue implementations for patient analysis.
Includes standard queue and priority queue.
"""


class MedicalQueue:
    """FIFO Queue for patient analysis processing."""
    
    def __init__(self):
        """Initialize empty queue."""
        self.items = []
    
    def enqueue(self, item):
        """Add item to the end of queue."""
        self.items.append(item)
    
    def dequeue(self):
        """Remove and return item from front of queue."""
        if self.is_empty():
            return None
        return self.items.pop(0)
    
    def peek(self):
        """Return front item without removing it."""
        if self.is_empty():
            return None
        return self.items[0]
    
    def is_empty(self):
        """Check if queue is empty."""
        return len(self.items) == 0
    
    def size(self):
        """Return size of queue."""
        return len(self.items)
    
    def clear(self):
        """Clear all items from queue."""
        self.items = []
    
    def __len__(self):
        """Return size of queue."""
        return len(self.items)
    
    def __iter__(self):
        """Make queue iterable."""
        return iter(self.items)
    
    def __str__(self):
        """String representation."""
        return str(self.items)


class PriorityQueue:
    """Priority Queue for ranking diseases by risk score."""
    
    def __init__(self):
        """Initialize empty priority queue."""
        self.items = []
    
    def enqueue(self, item, priority):
        """
        Add item to queue with priority.
        Priority: higher number = higher priority (dequeued first).
        """
        self.items.append((priority, item))
        # Sort by priority (descending - highest priority first)
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
    
    def peek_priority(self):
        """Return highest priority value."""
        if self.is_empty():
            return None
        return self.items[0][0]
    
    def is_empty(self):
        """Check if queue is empty."""
        return len(self.items) == 0
    
    def size(self):
        """Return size of queue."""
        return len(self.items)
    
    def get_all(self):
        """Get all items sorted by priority (highest first)."""
        return [(priority, item) for priority, item in self.items]
    
    def clear(self):
        """Clear all items from queue."""
        self.items = []
    
    def __len__(self):
        """Return size of queue."""
        return len(self.items)
    
    def __str__(self):
        """String representation."""
        return str([(p, str(item)) for p, item in self.items])

