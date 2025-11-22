class MedicalArray:
    """Lightweight array shim used by the prediction engine.
    Provides append, get, __len__ and iteration so code relying on
    the C++ MedicalArray can run when C++ DSA is not available.
    """
    def __init__(self):
        self._data = []

    def append(self, item):
        self._data.append(item)

    def get(self, idx):
        return self._data[idx]

    def __len__(self):
        return len(self._data)

    def __iter__(self):
        return iter(self._data)

    def to_list(self):
        return list(self._data)
