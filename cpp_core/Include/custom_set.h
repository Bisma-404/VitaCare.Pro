#ifndef CUSTOM_SET_H
#define CUSTOM_SET_H

#include <vector>

// Custom Set implementation using Red-Black Tree (balanced BST)
// Provides O(log n) insert, search, and delete operations
template<typename T>
class CustomSet {
private:
    enum Color { RED, BLACK };
    
    struct Node {
        T value;
        Color color;
        Node* left;
        Node* right;
        Node* parent;
        
        Node(T val) : value(val), color(RED), left(nullptr), right(nullptr), parent(nullptr) {}
    };
    
    Node* root;
    int setSize;
    
    // Helper functions for Red-Black Tree operations
    void rotateLeft(Node* node);
    void rotateRight(Node* node);
    void fixInsert(Node* node);
    Node* findNode(const T& value) const;
    void deleteTree(Node* node);
    void collectValues(Node* node, std::vector<T>& values) const;
    
public:
    CustomSet();
    ~CustomSet();
    
    // Core operations
    bool insert(const T& value);
    bool contains(const T& value) const;
    bool remove(const T& value);
    int size() const;
    bool empty() const;
    void clear();
    std::vector<T> toVector() const;
    
    // Iterator support for range-based for loops
    class Iterator {
    private:
        Node* current;
        std::vector<Node*> stack;
        
        void pushLeft(Node* node);
        
    public:
        Iterator(Node* root);
        Iterator();
        
        T operator*() const;
        Iterator& operator++();
        bool operator!=(const Iterator& other) const;
    };
    
    Iterator begin() const;
    Iterator end() const;
};

// Implementation
template<typename T>
CustomSet<T>::CustomSet() : root(nullptr), setSize(0) {}

template<typename T>
CustomSet<T>::~CustomSet() {
    deleteTree(root);
}

template<typename T>
void CustomSet<T>::deleteTree(Node* node) {
    if (node == nullptr) return;
    deleteTree(node->left);
    deleteTree(node->right);
    delete node;
}

template<typename T>
void CustomSet<T>::rotateLeft(Node* x) {
    Node* y = x->right;
    x->right = y->left;
    if (y->left != nullptr) y->left->parent = x;
    y->parent = x->parent;
    if (x->parent == nullptr) root = y;
    else if (x == x->parent->left) x->parent->left = y;
    else x->parent->right = y;
    y->left = x;
    x->parent = y;
}

template<typename T>
void CustomSet<T>::rotateRight(Node* y) {
    Node* x = y->left;
    y->left = x->right;
    if (x->right != nullptr) x->right->parent = y;
    x->parent = y->parent;
    if (y->parent == nullptr) root = x;
    else if (y == y->parent->right) y->parent->right = x;
    else y->parent->left = x;
    x->right = y;
    y->parent = x;
}

template<typename T>
void CustomSet<T>::fixInsert(Node* z) {
    while (z != root && z->parent != nullptr && z->parent->color == RED) {
        if (z->parent->parent == nullptr) break;
        
        if (z->parent == z->parent->parent->left) {
            Node* y = z->parent->parent->right;
            if (y != nullptr && y->color == RED) {
                z->parent->color = BLACK;
                y->color = BLACK;
                z->parent->parent->color = RED;
                z = z->parent->parent;
            } else {
                if (z == z->parent->right) {
                    z = z->parent;
                    rotateLeft(z);
                }
                if (z->parent != nullptr) {
                    z->parent->color = BLACK;
                    if (z->parent->parent != nullptr) {
                        z->parent->parent->color = RED;
                        rotateRight(z->parent->parent);
                    }
                }
            }
        } else {
            Node* y = z->parent->parent->left;
            if (y != nullptr && y->color == RED) {
                z->parent->color = BLACK;
                y->color = BLACK;
                z->parent->parent->color = RED;
                z = z->parent->parent;
            } else {
                if (z == z->parent->left) {
                    z = z->parent;
                    rotateRight(z);
                }
                if (z->parent != nullptr) {
                    z->parent->color = BLACK;
                    if (z->parent->parent != nullptr) {
                        z->parent->parent->color = RED;
                        rotateLeft(z->parent->parent);
                    }
                }
            }
        }
    }
    root->color = BLACK;
}

template<typename T>
bool CustomSet<T>::insert(const T& value) {
    if (findNode(value) != nullptr) return false;
    
    Node* z = new Node(value);
    Node* y = nullptr;
    Node* x = root;
    
    while (x != nullptr) {
        y = x;
        if (z->value < x->value) x = x->left;
        else x = x->right;
    }
    
    z->parent = y;
    if (y == nullptr) root = z;
    else if (z->value < y->value) y->left = z;
    else y->right = z;
    
    setSize++;
    
    if (z->parent == nullptr) {
        z->color = BLACK;
        return true;
    }
    
    if (z->parent->parent == nullptr) return true;
    
    fixInsert(z);
    return true;
}

template<typename T>
typename CustomSet<T>::Node* CustomSet<T>::findNode(const T& value) const {
    Node* current = root;
    while (current != nullptr) {
        if (value == current->value) return current;
        else if (value < current->value) current = current->left;
        else current = current->right;
    }
    return nullptr;
}

template<typename T>
bool CustomSet<T>::contains(const T& value) const {
    return findNode(value) != nullptr;
}

template<typename T>
int CustomSet<T>::size() const {
    return setSize;
}

template<typename T>
bool CustomSet<T>::empty() const {
    return setSize == 0;
}

template<typename T>
void CustomSet<T>::clear() {
    deleteTree(root);
    root = nullptr;
    setSize = 0;
}

template<typename T>
void CustomSet<T>::collectValues(Node* node, std::vector<T>& values) const {
    if (node == nullptr) return;
    collectValues(node->left, values);
    values.push_back(node->value);
    collectValues(node->right, values);
}

template<typename T>
std::vector<T> CustomSet<T>::toVector() const {
    std::vector<T> result;
    collectValues(root, result);
    return result;
}

// Iterator implementation
template<typename T>
void CustomSet<T>::Iterator::pushLeft(Node* node) {
    while (node != nullptr) {
        stack.push_back(node);
        node = node->left;
    }
}

template<typename T>
CustomSet<T>::Iterator::Iterator(Node* root) : current(nullptr) {
    pushLeft(root);
    if (!stack.empty()) {
        current = stack.back();
        stack.pop_back();
    }
}

template<typename T>
CustomSet<T>::Iterator::Iterator() : current(nullptr) {}

template<typename T>
T CustomSet<T>::Iterator::operator*() const {
    return current->value;
}

template<typename T>
typename CustomSet<T>::Iterator& CustomSet<T>::Iterator::operator++() {
    if (current != nullptr) {
        pushLeft(current->right);
        if (!stack.empty()) {
            current = stack.back();
            stack.pop_back();
        } else {
            current = nullptr;
        }
    }
    return *this;
}

template<typename T>
bool CustomSet<T>::Iterator::operator!=(const Iterator& other) const {
    return current != other.current;
}

template<typename T>
typename CustomSet<T>::Iterator CustomSet<T>::begin() const {
    return Iterator(root);
}

template<typename T>
typename CustomSet<T>::Iterator CustomSet<T>::end() const {
    return Iterator();
}

#endif // CUSTOM_SET_H
