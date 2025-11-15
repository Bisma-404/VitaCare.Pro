"""
Tree implementations for decision rules.
Includes binary tree and decision tree for medical analysis.
"""


class TreeNode:
    """Node for binary tree."""
    
    def __init__(self, data):
        self.data = data
        self.left = None
        self.right = None


class MedicalTree:
    """Binary Tree for organizing medical decision rules."""
    
    def __init__(self):
        """Initialize empty tree."""
        self.root = None
        self.size = 0
    
    def insert(self, data, compare_func=None):
        """Insert data into tree."""
        if compare_func is None:
            compare_func = lambda x, y: x < y
        
        self.root = self._insert_recursive(self.root, data, compare_func)
        self.size += 1
    
    def _insert_recursive(self, node, data, compare_func):
        """Recursive helper for insert."""
        if node is None:
            return TreeNode(data)
        
        if compare_func(data, node.data):
            node.left = self._insert_recursive(node.left, data, compare_func)
        else:
            node.right = self._insert_recursive(node.right, data, compare_func)
        
        return node
    
    def search(self, data, compare_func=None):
        """Search for data in tree."""
        if compare_func is None:
            compare_func = lambda x, y: x == y
        
        return self._search_recursive(self.root, data, compare_func)
    
    def _search_recursive(self, node, data, compare_func):
        """Recursive helper for search."""
        if node is None:
            return None
        
        if compare_func(node.data, data):
            return node.data
        
        left_result = self._search_recursive(node.left, data, compare_func)
        if left_result:
            return left_result
        
        return self._search_recursive(node.right, data, compare_func)
    
    def inorder_traversal(self):
        """Return inorder traversal of tree."""
        result = []
        self._inorder_recursive(self.root, result)
        return result
    
    def _inorder_recursive(self, node, result):
        """Recursive helper for inorder traversal."""
        if node:
            self._inorder_recursive(node.left, result)
            result.append(node.data)
            self._inorder_recursive(node.right, result)
    
    def preorder_traversal(self):
        """Return preorder traversal of tree."""
        result = []
        self._preorder_recursive(self.root, result)
        return result
    
    def _preorder_recursive(self, node, result):
        """Recursive helper for preorder traversal."""
        if node:
            result.append(node.data)
            self._preorder_recursive(node.left, result)
            self._preorder_recursive(node.right, result)
    
    def postorder_traversal(self):
        """Return postorder traversal of tree."""
        result = []
        self._postorder_recursive(self.root, result)
        return result
    
    def _postorder_recursive(self, node, result):
        """Recursive helper for postorder traversal."""
        if node:
            self._postorder_recursive(node.left, result)
            self._postorder_recursive(node.right, result)
            result.append(node.data)
    
    def height(self):
        """Return height of tree."""
        return self._height_recursive(self.root)
    
    def _height_recursive(self, node):
        """Recursive helper for height."""
        if node is None:
            return -1
        return 1 + max(
            self._height_recursive(node.left),
            self._height_recursive(node.right)
        )
    
    def __len__(self):
        """Return size of tree."""
        return self.size


class DecisionTreeNode:
    """Node for decision tree."""
    
    def __init__(self, feature_idx=None, threshold=None, decision=None):
        self.feature_idx = feature_idx  # Feature index for split
        self.threshold = threshold  # Threshold value for split
        self.decision = decision  # Final decision (class label) if leaf node
        self.left = None  # Left child (feature <= threshold)
        self.right = None  # Right child (feature > threshold)


class DecisionTree:
    """Decision Tree for medical decision rules."""
    
    def __init__(self):
        """Initialize empty decision tree."""
        self.root = None
    
    def add_rule(self, feature_idx, threshold, decision_left, decision_right=None):
        """Add a decision rule to the tree."""
        if self.root is None:
            self.root = DecisionTreeNode(feature_idx, threshold)
            self.root.left = DecisionTreeNode(decision=decision_left)
            if decision_right is not None:
                self.root.right = DecisionTreeNode(decision=decision_right)
        else:
            # Add to existing tree (simple insertion)
            self._add_rule_recursive(self.root, feature_idx, threshold, decision_left, decision_right)
    
    def _add_rule_recursive(self, node, feature_idx, threshold, decision_left, decision_right):
        """Recursive helper for adding rules."""
        if node.decision is not None:  # Leaf node
            # Convert leaf to decision node
            old_decision = node.decision
            node.feature_idx = feature_idx
            node.threshold = threshold
            node.decision = None
            node.left = DecisionTreeNode(decision=decision_left or old_decision)
            node.right = DecisionTreeNode(decision=decision_right or old_decision)
        else:
            # Add to appropriate child
            if node.left is None:
                node.left = DecisionTreeNode(decision=decision_left)
            else:
                self._add_rule_recursive(node.left, feature_idx, threshold, decision_left, decision_right)
            
            if decision_right is not None:
                if node.right is None:
                    node.right = DecisionTreeNode(decision=decision_right)
                else:
                    self._add_rule_recursive(node.right, feature_idx, threshold, decision_left, decision_right)
    
    def predict(self, features):
        """Predict decision based on features."""
        if self.root is None:
            return None
        
        node = self.root
        while node.decision is None:
            if features[node.feature_idx] <= node.threshold:
                node = node.left
            else:
                node = node.right
        
        return node.decision
    
    def get_rules(self):
        """Get all decision rules as list."""
        rules = []
        if self.root:
            self._get_rules_recursive(self.root, rules, path=[])
        return rules
    
    def _get_rules_recursive(self, node, rules, path):
        """Recursive helper for getting rules."""
        if node.decision is not None:
            rules.append({
                'path': path.copy(),
                'decision': node.decision
            })
        else:
            left_path = path + [f"feature_{node.feature_idx} <= {node.threshold}"]
            right_path = path + [f"feature_{node.feature_idx} > {node.threshold}"]
            
            if node.left:
                self._get_rules_recursive(node.left, rules, left_path)
            if node.right:
                self._get_rules_recursive(node.right, rules, right_path)

