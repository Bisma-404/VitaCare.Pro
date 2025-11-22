class DecisionTree:
    """Tiny DecisionTree stub used as a safe fallback when C++ tree
    implementation is not available. The stub provides `load` and
    `predict` methods with simple behavior.
    """
    def __init__(self):
        self._loaded = False

    def load(self, path):
        # Fake load: mark as loaded if file exists
        try:
            with open(path, 'r') as f:
                self._loaded = True
                return True
        except Exception:
            self._loaded = False
            return False

    def predict(self, features):
        # Very simple heuristic: if any numeric feature is high, return 1
        try:
            for v in features:
                try:
                    if float(v) > 200:
                        return 1
                except Exception:
                    continue
        except Exception:
            pass
        return 0
