#ifndef CUSTOM_MAP_H
#define CUSTOM_MAP_H

#include <vector>
#include <stdexcept>

// Custom Map implementation using Red-Black Tree (balanced BST)
// Provides O(log n) insert, search, and delete operations
template<typename K, typename V>
class CustomMap {
private:
    enum Color { RED, BLACK };
    
    struct Node {
        K key;
        V value;
        Color color;
        Node* left;
        Node* right;
        Node* parent;
        
        Node(K k, V v) : key(k), value(v), color(RED), left(nullptr), right(nullptr), parent(nullptr) {}
    };
    
    Node* root;
    int mapSize;
    
    // Helper functions for Red-Black Tree operations
    void rotateLeft(Node* node);
    void rotateRight(Node* node);
    void fixInsert(Node* node);
    void fixDelete(Node* node);
    Node* findNode(const K& key) const;
    Node* minimum(Node* node) const;
    void transplant(Node* u, Node* v);
    void deleteTree(Node* node);
    void collectKeys(Node* node, std::vector<K>& keys) const;
    
public:
    CustomMap();
    ~CustomMap();
    
    // Core operations
    void insert(const K& key, const V& value);
    bool contains(const K& key) const;
    V& operator[](const K& key);
    V get(const K& key, const V& defaultValue) const;
    bool remove(const K& key);
    int size() const;
    bool empty() const;
    void clear();
    std::vector<K> keys() const;
    
    // Iterator support for range-based for loops
    class Iterator {
    private:
        Node* current;
        std::vector<Node*> stack;
        
        void pushLeft(Node* node);
        
    public:
        Iterator(Node* root);
        Iterator();
        
        struct KeyValuePair {
            K key;
            V value;
            KeyValuePair(K k, V v) : key(k), value(v) {}
        };
        
        KeyValuePair operator*() const;
        Iterator& operator++();
        bool operator!=(const Iterator& other) const;
    };
    
    Iterator begin() const;
    Iterator end() const;
};

// Implementation
template<typename K, typename V>
CustomMap<K, V>::CustomMap() : root(nullptr), mapSize(0) {}

template<typename K, typename V>
CustomMap<K, V>::~CustomMap() {
    deleteTree(root);
}

template<typename K, typename V>
void CustomMap<K, V>::deleteTree(Node* node) {
    if (node == nullptr) return;
    deleteTree(node->left);
    deleteTree(node->right);
    delete node;
}

template<typename K, typename V>
void CustomMap<K, V>::rotateLeft(Node* x) {
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

template<typename K, typename V>
void CustomMap<K, V>::rotateRight(Node* y) {
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

template<typename K, typename V>
void CustomMap<K, V>::fixInsert(Node* z) {
    while (z != root && z->parent->color == RED) {
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
                z->parent->color = BLACK;
                z->parent->parent->color = RED;
                rotateRight(z->parent->parent);
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
                z->parent->color = BLACK;
                z->parent->parent->color = RED;
                rotateLeft(z->parent->parent);
            }
        }
    }
    root->color = BLACK;
}

template<typename K, typename V>
void CustomMap<K, V>::insert(const K& key, const V& value) {
    Node* existing = findNode(key);
    if (existing != nullptr) {
        existing->value = value;
        return;
    }
    
    Node* z = new Node(key, value);
    Node* y = nullptr;
    Node* x = root;
    
    while (x != nullptr) {
        y = x;
        if (z->key < x->key) x = x->left;
        else x = x->right;
    }
    
    z->parent = y;
    if (y == nullptr) root = z;
    else if (z->key < y->key) y->left = z;
    else y->right = z;
    
    mapSize++;
    
    if (z->parent == nullptr) {
        z->color = BLACK;
        return;
    }
    
    if (z->parent->parent == nullptr) return;
    
    fixInsert(z);
}

template<typename K, typename V>
typename CustomMap<K, V>::Node* CustomMap<K, V>::findNode(const K& key) const {
    Node* current = root;
    while (current != nullptr) {
        if (key == current->key) return current;
        else if (key < current->key) current = current->left;
        else current = current->right;
    }
    return nullptr;
}

template<typename K, typename V>
bool CustomMap<K, V>::contains(const K& key) const {
    return findNode(key) != nullptr;
}

template<typename K, typename V>
V& CustomMap<K, V>::operator[](const K& key) {
    Node* existing = findNode(key);
    if (existing != nullptr) return existing->value;
    
    V defaultValue = V();
    insert(key, defaultValue);
    return findNode(key)->value;
}

template<typename K, typename V>
V CustomMap<K, V>::get(const K& key, const V& defaultValue) const {
    Node* node = findNode(key);
    if (node != nullptr) return node->value;
    return defaultValue;
}

template<typename K, typename V>
int CustomMap<K, V>::size() const {
    return mapSize;
}

template<typename K, typename V>
bool CustomMap<K, V>::empty() const {
    return mapSize == 0;
}

template<typename K, typename V>
void CustomMap<K, V>::clear() {
    deleteTree(root);
    root = nullptr;
    mapSize = 0;
}

template<typename K, typename V>
void CustomMap<K, V>::collectKeys(Node* node, std::vector<K>& keys) const {
    if (node == nullptr) return;
    collectKeys(node->left, keys);
    keys.push_back(node->key);
    collectKeys(node->right, keys);
}

template<typename K, typename V>
std::vector<K> CustomMap<K, V>::keys() const {
    std::vector<K> result;
    collectKeys(root, result);
    return result;
}

// Iterator implementation
template<typename K, typename V>
void CustomMap<K, V>::Iterator::pushLeft(Node* node) {
    while (node != nullptr) {
        stack.push_back(node);
        node = node->left;
    }
}

template<typename K, typename V>
CustomMap<K, V>::Iterator::Iterator(Node* root) : current(nullptr) {
    pushLeft(root);
    if (!stack.empty()) {
        current = stack.back();
        stack.pop_back();
    }
}

template<typename K, typename V>
CustomMap<K, V>::Iterator::Iterator() : current(nullptr) {}

template<typename K, typename V>
typename CustomMap<K, V>::Iterator::KeyValuePair CustomMap<K, V>::Iterator::operator*() const {
    return KeyValuePair(current->key, current->value);
}

template<typename K, typename V>
typename CustomMap<K, V>::Iterator& CustomMap<K, V>::Iterator::operator++() {
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

template<typename K, typename V>
bool CustomMap<K, V>::Iterator::operator!=(const Iterator& other) const {
    return current != other.current;
}

template<typename K, typename V>
typename CustomMap<K, V>::Iterator CustomMap<K, V>::begin() const {
    return Iterator(root);
}

template<typename K, typename V>
typename CustomMap<K, V>::Iterator CustomMap<K, V>::end() const {
    return Iterator();
}

#endif // CUSTOM_MAP_H
