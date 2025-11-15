"""
Linked List implementation for patient report history.
Used for maintaining chronological order of medical reports.
"""


class ListNode:
    """Node for linked list."""
    
    def __init__(self, data):
        self.data = data
        self.next = None
        self.prev = None


class MedicalLinkedList:
    """Doubly linked list for patient report history."""
    
    def __init__(self):
        """Initialize empty linked list."""
        self.head = None
        self.tail = None
        self.size = 0
    
    def append(self, data):
        """Add data to the end of list."""
        new_node = ListNode(data)
        
        if self.head is None:
            self.head = new_node
            self.tail = new_node
        else:
            new_node.prev = self.tail
            self.tail.next = new_node
            self.tail = new_node
        
        self.size += 1
    
    def prepend(self, data):
        """Add data to the beginning of list."""
        new_node = ListNode(data)
        
        if self.head is None:
            self.head = new_node
            self.tail = new_node
        else:
            new_node.next = self.head
            self.head.prev = new_node
            self.head = new_node
        
        self.size += 1
    
    def insert_at(self, index, data):
        """Insert data at specific index."""
        if index < 0 or index > self.size:
            raise IndexError("Index out of range")
        
        if index == 0:
            self.prepend(data)
        elif index == self.size:
            self.append(data)
        else:
            new_node = ListNode(data)
            current = self._get_node_at(index)
            
            new_node.prev = current.prev
            new_node.next = current
            current.prev.next = new_node
            current.prev = new_node
            
            self.size += 1
    
    def remove(self, data):
        """Remove first occurrence of data."""
        current = self.head
        
        while current:
            if current.data == data:
                if current.prev:
                    current.prev.next = current.next
                else:
                    self.head = current.next
                
                if current.next:
                    current.next.prev = current.prev
                else:
                    self.tail = current.prev
                
                self.size -= 1
                return True
            
            current = current.next
        
        return False
    
    def remove_at(self, index):
        """Remove node at specific index."""
        if index < 0 or index >= self.size:
            raise IndexError("Index out of range")
        
        current = self._get_node_at(index)
        
        if current.prev:
            current.prev.next = current.next
        else:
            self.head = current.next
        
        if current.next:
            current.next.prev = current.prev
        else:
            self.tail = current.prev
        
        self.size -= 1
        return current.data
    
    def get(self, index):
        """Get data at index."""
        if index < 0 or index >= self.size:
            raise IndexError("Index out of range")
        
        current = self._get_node_at(index)
        return current.data
    
    def find(self, data):
        """Find index of data, return -1 if not found."""
        current = self.head
        index = 0
        
        while current:
            if current.data == data:
                return index
            current = current.next
            index += 1
        
        return -1
    
    def _get_node_at(self, index):
        """Get node at specific index."""
        if index < self.size // 2:
            # Start from head
            current = self.head
            for _ in range(index):
                current = current.next
        else:
            # Start from tail
            current = self.tail
            for _ in range(self.size - index - 1):
                current = current.prev
        
        return current
    
    def to_list(self):
        """Convert linked list to Python list."""
        result = []
        current = self.head
        while current:
            result.append(current.data)
            current = current.next
        return result
    
    def __len__(self):
        """Return size of list."""
        return self.size
    
    def __iter__(self):
        """Make list iterable."""
        current = self.head
        while current:
            yield current.data
            current = current.next
    
    def __str__(self):
        """String representation."""
        return str(self.to_list())

