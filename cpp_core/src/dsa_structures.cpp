#include "../Include/dsa_structures.h"
#include <algorithm>

// ============================================================================
// HASH MAP Implementation
// ============================================================================
MedicalHashMap::MedicalHashMap() {}

void MedicalHashMap::put(const std::string& key, const std::string& value) {
    map[key] = value;
}

std::string MedicalHashMap::get(const std::string& key, const std::string& default_val) {
    auto it = map.find(key);
    return (it != map.end()) ? it->second : default_val;
}

bool MedicalHashMap::contains(const std::string& key) {
    return map.find(key) != map.end();
}

void MedicalHashMap::clear() {
    map.clear();
}

int MedicalHashMap::size() {
    return static_cast<int>(map.size());
}

std::vector<std::string> MedicalHashMap::keys() {
    std::vector<std::string> result;
    for (const auto& pair : map) {
        result.push_back(pair.first);
    }
    return result;
}

std::vector<std::string> MedicalHashMap::values() {
    std::vector<std::string> result;
    for (const auto& pair : map) {
        result.push_back(pair.second);
    }
    return result;
}

// ============================================================================
// STACK Implementation
// ============================================================================
template<typename T>
MedicalStack<T>::MedicalStack(int max_size) : maxSize(max_size) {}

template<typename T>
void MedicalStack<T>::push(const T& item) {
    stack.push(item);
    if (static_cast<int>(stack.size()) > maxSize) {
        // Remove oldest (bottom) by recreating stack
        std::stack<T> temp;
        while (stack.size() > 1) {
            temp.push(stack.top());
            stack.pop();
        }
        stack.pop(); // Remove oldest
        while (!temp.empty()) {
            stack.push(temp.top());
            temp.pop();
        }
    }
}

template<typename T>
T MedicalStack<T>::pop() {
    if (stack.empty()) {
        throw std::runtime_error("Stack is empty");
    }
    T item = stack.top();
    stack.pop();
    return item;
}

template<typename T>
T MedicalStack<T>::peek() {
    if (stack.empty()) {
        throw std::runtime_error("Stack is empty");
    }
    return stack.top();
}

template<typename T>
bool MedicalStack<T>::isEmpty() {
    return stack.empty();
}

template<typename T>
int MedicalStack<T>::size() {
    return static_cast<int>(stack.size());
}

template<typename T>
void MedicalStack<T>::clear() {
    while (!stack.empty()) {
        stack.pop();
    }
}

template<typename T>
std::vector<T> MedicalStack<T>::getAll() {
    std::vector<T> result;
    std::stack<T> temp = stack;
    while (!temp.empty()) {
        result.insert(result.begin(), temp.top());
        temp.pop();
    }
    return result;
}

// ============================================================================
// QUEUE Implementation
// ============================================================================
template<typename T>
MedicalQueue<T>::MedicalQueue() {}

template<typename T>
void MedicalQueue<T>::enqueue(const T& item) {
    queue.push(item);
}

template<typename T>
T MedicalQueue<T>::dequeue() {
    if (queue.empty()) {
        throw std::runtime_error("Queue is empty");
    }
    T item = queue.front();
    queue.pop();
    return item;
}

template<typename T>
T MedicalQueue<T>::peek() {
    if (queue.empty()) {
        throw std::runtime_error("Queue is empty");
    }
    return queue.front();
}

template<typename T>
bool MedicalQueue<T>::isEmpty() {
    return queue.empty();
}

template<typename T>
int MedicalQueue<T>::size() {
    return static_cast<int>(queue.size());
}

template<typename T>
void MedicalQueue<T>::clear() {
    while (!queue.empty()) {
        queue.pop();
    }
}

// ============================================================================
// PRIORITY QUEUE / HEAP Implementation
// ============================================================================
MedicalPriorityQueue::MedicalPriorityQueue(bool max_heap) : maxHeap(max_heap) {}

void MedicalPriorityQueue::heapifyUp(int index) {
    if (index == 0) return;
    
    int p = parent(index);
    bool shouldSwap = maxHeap ? 
        (heap[index].risk_score > heap[p].risk_score) :
        (heap[index].risk_score < heap[p].risk_score);
    
    if (shouldSwap) {
        std::swap(heap[index], heap[p]);
        heapifyUp(p);
    }
}

void MedicalPriorityQueue::heapifyDown(int index) {
    int largest = index;
    int l = left(index);
    int r = right(index);
    
    if (l < static_cast<int>(heap.size())) {
        bool shouldSwap = maxHeap ?
            (heap[l].risk_score > heap[largest].risk_score) :
            (heap[l].risk_score < heap[largest].risk_score);
        if (shouldSwap) largest = l;
    }
    
    if (r < static_cast<int>(heap.size())) {
        bool shouldSwap = maxHeap ?
            (heap[r].risk_score > heap[largest].risk_score) :
            (heap[r].risk_score < heap[largest].risk_score);
        if (shouldSwap) largest = r;
    }
    
    if (largest != index) {
        std::swap(heap[index], heap[largest]);
        heapifyDown(largest);
    }
}

void MedicalPriorityQueue::enqueue(const PriorityItem& item) {
    heap.push_back(item);
    heapifyUp(heap.size() - 1);
}

PriorityItem MedicalPriorityQueue::dequeue() {
    if (heap.empty()) {
        throw std::runtime_error("Priority queue is empty");
    }
    
    PriorityItem item = heap[0];
    heap[0] = heap.back();
    heap.pop_back();
    
    if (!heap.empty()) {
        heapifyDown(0);
    }
    
    return item;
}

PriorityItem MedicalPriorityQueue::peek() {
    if (heap.empty()) {
        throw std::runtime_error("Priority queue is empty");
    }
    return heap[0];
}

bool MedicalPriorityQueue::isEmpty() {
    return heap.empty();
}

int MedicalPriorityQueue::size() {
    return static_cast<int>(heap.size());
}

void MedicalPriorityQueue::clear() {
    heap.clear();
}

std::vector<PriorityItem> MedicalPriorityQueue::getAll() {
    std::vector<PriorityItem> result = heap;
    if (maxHeap) {
        std::sort(result.begin(), result.end(), 
            [](const PriorityItem& a, const PriorityItem& b) {
                return a.risk_score > b.risk_score;
            });
    } else {
        std::sort(result.begin(), result.end(), 
            [](const PriorityItem& a, const PriorityItem& b) {
                return a.risk_score < b.risk_score;
            });
    }
    return result;
}

// ============================================================================
// GRAPH Implementation
// ============================================================================
SymptomDiseaseGraph::SymptomDiseaseGraph() {}

void SymptomDiseaseGraph::addNode(const std::string& node, const std::string& type) {
    if (adjacencyList.find(node) == adjacencyList.end()) {
        adjacencyList[node] = std::vector<std::string>();
        nodeTypes[node] = type;
    }
}

void SymptomDiseaseGraph::addEdge(const std::string& from, const std::string& to, bool bidirectional) {
    addNode(from, "symptom");
    addNode(to, "disease");
    
    adjacencyList[from].push_back(to);
    if (bidirectional) {
        adjacencyList[to].push_back(from);
    }
}

std::vector<std::string> SymptomDiseaseGraph::getNeighbors(const std::string& node) {
    auto it = adjacencyList.find(node);
    return (it != adjacencyList.end()) ? it->second : std::vector<std::string>();
}

std::vector<std::string> SymptomDiseaseGraph::getDiseasesForSymptom(const std::string& symptom) {
    return getNeighbors(symptom);
}

std::vector<std::string> SymptomDiseaseGraph::getSymptomsForDisease(const std::string& disease) {
    std::vector<std::string> symptoms;
    for (const auto& pair : adjacencyList) {
        if (nodeTypes[pair.first] == "symptom") {
            for (const auto& neighbor : pair.second) {
                if (neighbor == disease) {
                    symptoms.push_back(pair.first);
                    break;
                }
            }
        }
    }
    return symptoms;
}

bool SymptomDiseaseGraph::hasNode(const std::string& node) {
    return adjacencyList.find(node) != adjacencyList.end();
}

std::string SymptomDiseaseGraph::getNodeType(const std::string& node) {
    auto it = nodeTypes.find(node);
    return (it != nodeTypes.end()) ? it->second : "";
}

void SymptomDiseaseGraph::clear() {
    adjacencyList.clear();
    nodeTypes.clear();
}

int SymptomDiseaseGraph::size() {
    return static_cast<int>(adjacencyList.size());
}

// ============================================================================
// LINKED LIST Implementation
// ============================================================================
template<typename T>
MedicalLinkedList<T>::MedicalLinkedList() : head(nullptr), tail(nullptr), listSize(0) {}

template<typename T>
MedicalLinkedList<T>::~MedicalLinkedList() {
    clear();
}

template<typename T>
void MedicalLinkedList<T>::append(const T& item) {
    ListNode<T>* newNode = new ListNode<T>(item);
    if (tail == nullptr) {
        head = tail = newNode;
    } else {
        tail->next = newNode;
        newNode->prev = tail;
        tail = newNode;
    }
    listSize++;
}

template<typename T>
void MedicalLinkedList<T>::prepend(const T& item) {
    ListNode<T>* newNode = new ListNode<T>(item);
    if (head == nullptr) {
        head = tail = newNode;
    } else {
        head->prev = newNode;
        newNode->next = head;
        head = newNode;
    }
    listSize++;
}

template<typename T>
void MedicalLinkedList<T>::remove(const T& item) {
    ListNode<T>* current = head;
    while (current != nullptr) {
        if (current->data == item) {
            if (current->prev) current->prev->next = current->next;
            else head = current->next;
            
            if (current->next) current->next->prev = current->prev;
            else tail = current->prev;
            
            delete current;
            listSize--;
            return;
        }
        current = current->next;
    }
}

template<typename T>
bool MedicalLinkedList<T>::contains(const T& item) {
    ListNode<T>* current = head;
    while (current != nullptr) {
        if (current->data == item) return true;
        current = current->next;
    }
    return false;
}

template<typename T>
int MedicalLinkedList<T>::size() {
    return listSize;
}

template<typename T>
void MedicalLinkedList<T>::clear() {
    while (head != nullptr) {
        ListNode<T>* temp = head;
        head = head->next;
        delete temp;
    }
    tail = nullptr;
    listSize = 0;
}

template<typename T>
std::vector<T> MedicalLinkedList<T>::toVector() {
    std::vector<T> result;
    ListNode<T>* current = head;
    while (current != nullptr) {
        result.push_back(current->data);
        current = current->next;
    }
    return result;
}

template<typename T>
T MedicalLinkedList<T>::get(int index) {
    if (index < 0 || index >= listSize) {
        throw std::runtime_error("Index out of bounds");
    }
    ListNode<T>* current = head;
    for (int i = 0; i < index; i++) {
        current = current->next;
    }
    return current->data;
}

// ============================================================================
// SET Implementation
// ============================================================================
MedicalSet::MedicalSet() {}

void MedicalSet::add(const std::string& item) {
    set[item] = true;
}

void MedicalSet::remove(const std::string& item) {
    set.erase(item);
}

bool MedicalSet::contains(const std::string& item) {
    return set.find(item) != set.end();
}

void MedicalSet::clear() {
    set.clear();
}

int MedicalSet::size() {
    return static_cast<int>(set.size());
}

std::vector<std::string> MedicalSet::toVector() {
    std::vector<std::string> result;
    for (const auto& pair : set) {
        result.push_back(pair.first);
    }
    return result;
}

// Explicit template instantiations for pybind
template class MedicalStack<std::string>;
template class MedicalQueue<std::string>;
template class MedicalLinkedList<std::string>;

