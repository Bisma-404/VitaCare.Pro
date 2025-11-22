class MedicalLinkedList:
    """Very small linked-list shim used as a placeholder.
    Implements append and basic iteration so higher-level code can run.
    """
    class _Node:
        def __init__(self, value):
            self.value = value
            self.next = None

    def __init__(self):
        self.head = None
        self._size = 0

    def append(self, value):
        node = MedicalLinkedList._Node(value)
        if not self.head:
            self.head = node
        else:
            cur = self.head
            while cur.next:
                cur = cur.next
            cur.next = node
        self._size += 1

    def __len__(self):
        return self._size

    def to_list(self):
        out = []
        cur = self.head
        while cur:
            out.append(cur.value)
            cur = cur.next
        return out
