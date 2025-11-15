"""
Heap implementations for ranking diseases by risk.
Includes max heap for priority-based ranking.
"""


class MedicalHeap:
    """Base heap class for medical data."""
    
    def __init__(self, is_max_heap=True):
        """Initialize heap. is_max_heap=True for max heap, False for min heap."""
        self.heap = []
        self.is_max_heap = is_max_heap
    
    def _parent(self, index):
        """Get parent index."""
        return (index - 1) // 2
    
    def _left_child(self, index):
        """Get left child index."""
        return 2 * index + 1
    
    def _right_child(self, index):
        """Get right child index."""
        return 2 * index + 2
    
    def _swap(self, i, j):
        """Swap elements at indices i and j."""
        self.heap[i], self.heap[j] = self.heap[j], self.heap[i]
    
    def _compare(self, a, b):
        """Compare two elements based on heap type."""
        if self.is_max_heap:
            return a > b
        return a < b
    
    def insert(self, item):
        """Insert item into heap."""
        self.heap.append(item)
        self._heapify_up(len(self.heap) - 1)
    
    def _heapify_up(self, index):
        """Heapify up from given index."""
        parent = self._parent(index)
        
        if index > 0 and self._compare(self.heap[index], self.heap[parent]):
            self._swap(index, parent)
            self._heapify_up(parent)
    
    def extract(self):
        """Extract root element from heap."""
        if len(self.heap) == 0:
            return None
        
        if len(self.heap) == 1:
            return self.heap.pop()
        
        root = self.heap[0]
        self.heap[0] = self.heap.pop()
        self._heapify_down(0)
        
        return root
    
    def _heapify_down(self, index):
        """Heapify down from given index."""
        left = self._left_child(index)
        right = self._right_child(index)
        extreme = index
        
        if left < len(self.heap) and self._compare(self.heap[left], self.heap[extreme]):
            extreme = left
        
        if right < len(self.heap) and self._compare(self.heap[right], self.heap[extreme]):
            extreme = right
        
        if extreme != index:
            self._swap(index, extreme)
            self._heapify_down(extreme)
    
    def peek(self):
        """Peek at root element without removing it."""
        if len(self.heap) == 0:
            return None
        return self.heap[0]
    
    def size(self):
        """Return size of heap."""
        return len(self.heap)
    
    def is_empty(self):
        """Check if heap is empty."""
        return len(self.heap) == 0
    
    def clear(self):
        """Clear all elements from heap."""
        self.heap = []
    
    def to_list(self):
        """Convert heap to sorted list."""
        result = []
        temp_heap = MedicalHeap(self.is_max_heap)
        temp_heap.heap = self.heap.copy()
        
        while not temp_heap.is_empty():
            result.append(temp_heap.extract())
        
        return result
    
    def __len__(self):
        """Return size of heap."""
        return len(self.heap)
    
    def __str__(self):
        """String representation."""
        return str(self.heap)


class MaxHeap(MedicalHeap):
    """Max heap for ranking diseases by highest risk first."""
    
    def __init__(self):
        """Initialize max heap."""
        super().__init__(is_max_heap=True)


class MinHeap(MedicalHeap):
    """Min heap for ranking diseases by lowest risk first."""
    
    def __init__(self):
        """Initialize min heap."""
        super().__init__(is_max_heap=False)


class PriorityItem:
    """Item with priority for heap."""
    
    def __init__(self, priority, item):
        self.priority = priority
        self.item = item
    
    def __lt__(self, other):
        """Less than comparison for max heap (reverse logic)."""
        return self.priority > other.priority
    
    def __gt__(self, other):
        """Greater than comparison for max heap (reverse logic)."""
        return self.priority < other.priority
    
    def __eq__(self, other):
        """Equality comparison."""
        return self.priority == other.priority
    
    def __str__(self):
        """String representation."""
        return f"PriorityItem(priority={self.priority}, item={self.item})"


class PriorityHeap:
    """Priority heap for ranking items by priority."""
    
    def __init__(self, max_heap=True):
        """Initialize priority heap."""
        self.heap = []
        self.max_heap = max_heap
    
    def push(self, item, priority):
        """Push item with priority."""
        priority_item = PriorityItem(priority, item)
        self.heap.append(priority_item)
        self._heapify_up(len(self.heap) - 1)
    
    def pop(self):
        """Pop highest priority item."""
        if len(self.heap) == 0:
            return None
        
        if len(self.heap) == 1:
            return self.heap.pop().item
        
        root = self.heap[0].item
        self.heap[0] = self.heap.pop()
        self._heapify_down(0)
        
        return root
    
    def _parent(self, index):
        """Get parent index."""
        return (index - 1) // 2
    
    def _left_child(self, index):
        """Get left child index."""
        return 2 * index + 1
    
    def _right_child(self, index):
        """Get right child index."""
        return 2 * index + 2
    
    def _heapify_up(self, index):
        """Heapify up."""
        parent = self._parent(index)
        
        if index > 0 and self.heap[index] > self.heap[parent]:
            self.heap[index], self.heap[parent] = self.heap[parent], self.heap[index]
            self._heapify_up(parent)
    
    def _heapify_down(self, index):
        """Heapify down."""
        left = self._left_child(index)
        right = self._right_child(index)
        largest = index
        
        if left < len(self.heap) and self.heap[left] > self.heap[largest]:
            largest = left
        
        if right < len(self.heap) and self.heap[right] > self.heap[largest]:
            largest = right
        
        if largest != index:
            self.heap[index], self.heap[largest] = self.heap[largest], self.heap[index]
            self._heapify_down(largest)
    
    def peek(self):
        """Peek at highest priority item."""
        if len(self.heap) == 0:
            return None
        return self.heap[0].item
    
    def size(self):
        """Return size of heap."""
        return len(self.heap)
    
    def is_empty(self):
        """Check if heap is empty."""
        return len(self.heap) == 0

