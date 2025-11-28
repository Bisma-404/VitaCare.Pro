#include "../Include/dsa_structures.h"
#include <cmath>
#include <cstring>

// ============================================================================
// HASH MAP Implementation (custom open-addressing double hashing)
// ============================================================================

static bool is_prime(int x) {
    if (x <= 1) return false;
    if (x <= 3) return true;
    if (x % 2 == 0) return false;
    int r = static_cast<int>(std::sqrt(x));
    for (int i = 3; i <= r; i += 2) {
        if (x % i == 0) return false;
    }
    return true;
}

static int next_capacity(int current) {
    // find next prime roughly double the size
    int target = current * 2 + 1;
    while (!is_prime(target)) target += 2;
    return target;
}

// djb2 primary hash
unsigned long MedicalHashMap::hash1(const std::string& s) const {
    unsigned long hash = 5381UL;
    for (unsigned char c : s) {
        hash = ((hash << 5) + hash) + c; /* hash * 33 + c */
    }
    return hash;
}

// sdbm-like secondary hash (must be non-zero)
unsigned long MedicalHashMap::hash2(const std::string& s) const {
    unsigned long hash = 0UL;
    for (unsigned char c : s) {
        hash = c + (hash << 6) + (hash << 16) - hash;
    }
    // Make sure step is odd and non-zero
    hash = (hash % 0x7fffffff) | 1UL;
    return hash;
}

void MedicalHashMap::ensure_capacity_for_insert() {
    double lf = static_cast<double>(count + 1) / static_cast<double>(capacity);
    if (lf > max_load_factor) {
        int new_cap = next_capacity(capacity);
        rehash(new_cap);
    }
}

void MedicalHashMap::rehash(int new_capacity) {
    Entry* old_table = table;
    int old_capacity = capacity;

    table = new Entry[new_capacity];
    capacity = new_capacity;
    count = 0;

    for (int i = 0; i < old_capacity; ++i) {
        if (old_table[i].occupied && !old_table[i].deleted) {
            put(old_table[i].key, old_table[i].value);
        }
    }

    delete[] old_table;
}

int MedicalHashMap::find_index(const std::string& key) const {
    if (capacity == 0) return -1;
    unsigned long h1 = hash1(key) % static_cast<unsigned long>(capacity);
    unsigned long h2v = hash2(key) % static_cast<unsigned long>(capacity);
    if (h2v == 0) h2v = 1;

    for (int i = 0; i < capacity; ++i) {
        int idx = static_cast<int>((h1 + (unsigned long)i * h2v) % static_cast<unsigned long>(capacity));
        if (!table[idx].occupied) {
            // empty slot -> not present
            return -1;
        }
        if (!table[idx].deleted && table[idx].occupied && table[idx].key == key) {
            return idx;
        }
    }
    return -1;
}

MedicalHashMap::MedicalHashMap(int initial_capacity, double load_factor)
    : table(nullptr), capacity(0), count(0), max_load_factor(load_factor) {
    if (initial_capacity < 3) initial_capacity = 3;
    // find prime capacity
    int cap = initial_capacity;
    while (!is_prime(cap)) ++cap;
    capacity = cap;
    table = new Entry[capacity];
}

MedicalHashMap::~MedicalHashMap() {
    if (table) delete[] table;
}

void MedicalHashMap::put(const std::string& key, const std::string& value) {
    ensure_capacity_for_insert();
    unsigned long h1v = hash1(key) % static_cast<unsigned long>(capacity);
    unsigned long h2v = hash2(key) % static_cast<unsigned long>(capacity);
    if (h2v == 0) h2v = 1;

    int first_deleted = -1;
    for (int i = 0; i < capacity; ++i) {
        int idx = static_cast<int>((h1v + (unsigned long)i * h2v) % static_cast<unsigned long>(capacity));
        if (!table[idx].occupied) {
            if (first_deleted != -1) idx = first_deleted;
            table[idx].key = key;
            table[idx].value = value;
            table[idx].occupied = true;
            table[idx].deleted = false;
            ++count;
            return;
        }
        if (table[idx].occupied && !table[idx].deleted && table[idx].key == key) {
            table[idx].value = value; // update
            return;
        }
        if (table[idx].deleted && first_deleted == -1) {
            first_deleted = idx;
        }
    }

    // If we reach here, table is full (shouldn't if rehash worked), but handle
    if (first_deleted != -1) {
        table[first_deleted].key = key;
        table[first_deleted].value = value;
        table[first_deleted].occupied = true;
        table[first_deleted].deleted = false;
        ++count;
    } else {
        // force grow and insert
        int newcap = next_capacity(capacity);
        rehash(newcap);
        put(key, value);
    }
}

std::string MedicalHashMap::get(const std::string& key, const std::string& default_val) {
    int idx = find_index(key);
    if (idx == -1) return default_val;
    return table[idx].value;
}

bool MedicalHashMap::contains(const std::string& key) {
    return find_index(key) != -1;
}

bool MedicalHashMap::remove(const std::string& key) {
    int idx = find_index(key);
    if (idx == -1) return false;
    // Mark as deleted but keep occupied=true to preserve probe chain
    table[idx].value.clear();
    table[idx].key.clear();
    table[idx].deleted = true;
    // do not set occupied=false because that would break probing
    --count;
    return true;
}

void MedicalHashMap::clear() {
    for (int i = 0; i < capacity; ++i) {
        table[i].key.clear();
        table[i].value.clear();
        table[i].occupied = false;
        table[i].deleted = false;
    }
    count = 0;
}

int MedicalHashMap::size() { return count; }

std::vector<std::string> MedicalHashMap::keys() {
    std::vector<std::string> out;
    out.reserve(count);
    for (int i = 0; i < capacity; ++i) {
        if (table[i].occupied && !table[i].deleted) out.push_back(table[i].key);
    }
    return out;
}

std::vector<std::string> MedicalHashMap::values() {
    std::vector<std::string> out;
    out.reserve(count);
    for (int i = 0; i < capacity; ++i) {
        if (table[i].occupied && !table[i].deleted) out.push_back(table[i].value);
    }
    return out;
}

// ============================================================================
// STRING STACK Implementation (array-backed)
// ============================================================================
#include <algorithm>

void StringStack::grow_if_needed() {
    if (topIndex < capacity) return;
    int newcap = capacity * 2;
    std::string* newarr = new std::string[newcap];
    for (int i = 0; i < topIndex; ++i) newarr[i] = arr[i];
    delete[] arr;
    arr = newarr;
    capacity = newcap;
}

StringStack::StringStack(int max_size)
    : arr(nullptr), capacity(std::max(16, max_size)), topIndex(0), maxSizeLimit(max_size) {
    if (capacity < 4) capacity = 4;
    arr = new std::string[capacity];
}

StringStack::~StringStack() {
    delete[] arr;
}

void StringStack::push(const std::string& item) {
    // If we have a maxSizeLimit and we're at limit, shift left to drop oldest
    if (maxSizeLimit > 0 && topIndex >= maxSizeLimit) {
        // shift left by one
        for (int i = 1; i < topIndex; ++i) arr[i - 1] = arr[i];
        topIndex = topIndex - 1;
    }
    grow_if_needed();
    arr[topIndex++] = item;
}

std::string StringStack::pop() {
    if (topIndex == 0) throw std::runtime_error("Stack is empty");
    return arr[--topIndex];
}

std::string StringStack::peek() {
    if (topIndex == 0) throw std::runtime_error("Stack is empty");
    return arr[topIndex - 1];
}

bool StringStack::isEmpty() { return topIndex == 0; }

int StringStack::size() { return topIndex; }

void StringStack::clear() { topIndex = 0; }

std::vector<std::string> StringStack::getAll() {
    std::vector<std::string> out;
    out.reserve(topIndex);
    for (int i = 0; i < topIndex; ++i) out.push_back(arr[i]);
    return out;
}

// ============================================================================
// STRING QUEUE Implementation (circular buffer)
// ============================================================================

void StringQueue::grow_if_needed() {
    if (count < capacity) return;
    int newcap = capacity * 2;
    std::string* newbuf = new std::string[newcap];
    // copy existing elements in order
    for (int i = 0; i < count; ++i) {
        newbuf[i] = buffer[(head + i) % capacity];
    }
    delete[] buffer;
    buffer = newbuf;
    capacity = newcap;
    head = 0;
    tail = count % capacity;
}

StringQueue::StringQueue() : buffer(nullptr), capacity(16), head(0), tail(0), count(0) {
    buffer = new std::string[capacity];
}

StringQueue::~StringQueue() { delete[] buffer; }

void StringQueue::enqueue(const std::string& item) {
    grow_if_needed();
    buffer[tail] = item;
    tail = (tail + 1) % capacity;
    ++count;
}

std::string StringQueue::dequeue() {
    if (count == 0) throw std::runtime_error("Queue is empty");
    std::string val = buffer[head];
    head = (head + 1) % capacity;
    --count;
    return val;
}

std::string StringQueue::peek() {
    if (count == 0) throw std::runtime_error("Queue is empty");
    return buffer[head];
}

bool StringQueue::isEmpty() { return count == 0; }

int StringQueue::size() { return count; }

void StringQueue::clear() { head = tail = count = 0; }

// ============================================================================
// PRIORITY QUEUE / HEAP Implementation
// ============================================================================
MedicalPriorityQueue::MedicalPriorityQueue(bool max_heap)
    : heapArr(nullptr), capacity(16), heapSize(0), maxHeap(max_heap) {
    heapArr = new PriorityItem[capacity];
}

MedicalPriorityQueue::~MedicalPriorityQueue() {
    if (heapArr) delete[] heapArr;
}

void MedicalPriorityQueue::grow_heap() {
    int newcap = capacity * 2;
    PriorityItem* newarr = new PriorityItem[newcap];
    for (int i = 0; i < heapSize; ++i) newarr[i] = heapArr[i];
    delete[] heapArr;
    heapArr = newarr;
    capacity = newcap;
}

void MedicalPriorityQueue::heapifyUp(int index) {
    while (index > 0) {
        int p = parent(index);
        bool shouldSwap = maxHeap ?
            (heapArr[index].risk_score > heapArr[p].risk_score) :
            (heapArr[index].risk_score < heapArr[p].risk_score);
        if (!shouldSwap) break;
        PriorityItem tmp = heapArr[index];
        heapArr[index] = heapArr[p];
        heapArr[p] = tmp;
        index = p;
    }
}

void MedicalPriorityQueue::heapifyDown(int index) {
    while (true) {
        int largest = index;
        int l = left(index);
        int r = right(index);
        if (l < heapSize) {
            bool shouldSwap = maxHeap ?
                (heapArr[l].risk_score > heapArr[largest].risk_score) :
                (heapArr[l].risk_score < heapArr[largest].risk_score);
            if (shouldSwap) largest = l;
        }
        if (r < heapSize) {
            bool shouldSwap = maxHeap ?
                (heapArr[r].risk_score > heapArr[largest].risk_score) :
                (heapArr[r].risk_score < heapArr[largest].risk_score);
            if (shouldSwap) largest = r;
        }
        if (largest == index) break;
        PriorityItem tmp = heapArr[index];
        heapArr[index] = heapArr[largest];
        heapArr[largest] = tmp;
        index = largest;
    }
}

void MedicalPriorityQueue::enqueue(const PriorityItem& item) {
    if (heapSize >= capacity) grow_heap();
    heapArr[heapSize] = item;
    heapifyUp(heapSize);
    ++heapSize;
}

PriorityItem MedicalPriorityQueue::dequeue() {
    if (heapSize == 0) throw std::runtime_error("Priority queue is empty");
    PriorityItem item = heapArr[0];
    heapArr[0] = heapArr[heapSize - 1];
    --heapSize;
    if (heapSize > 0) heapifyDown(0);
    return item;
}

PriorityItem MedicalPriorityQueue::peek() {
    if (heapSize == 0) throw std::runtime_error("Priority queue is empty");
    return heapArr[0];
}

bool MedicalPriorityQueue::isEmpty() { return heapSize == 0; }

int MedicalPriorityQueue::size() { return heapSize; }

void MedicalPriorityQueue::clear() { heapSize = 0; }

std::vector<PriorityItem> MedicalPriorityQueue::getAll() {
    std::vector<PriorityItem> result;
    result.reserve(heapSize);
    for (int i = 0; i < heapSize; ++i) result.push_back(heapArr[i]);
    if (maxHeap) {
        std::sort(result.begin(), result.end(),
            [](const PriorityItem& a, const PriorityItem& b) { return a.risk_score > b.risk_score; });
    } else {
        std::sort(result.begin(), result.end(),
            [](const PriorityItem& a, const PriorityItem& b) { return a.risk_score < b.risk_score; });
    }
    return result;
}

// ============================================================================
// GRAPH Implementation
// ============================================================================
SymptomDiseaseGraph::SymptomDiseaseGraph() {
    adjacencyMap = new MedicalHashMap();
    nodeTypeMap = new MedicalHashMap();
}

SymptomDiseaseGraph::~SymptomDiseaseGraph() {
    if (adjacencyMap) delete adjacencyMap;
    if (nodeTypeMap) delete nodeTypeMap;
}

static void split_serialized(const std::string& s, char delim, std::vector<std::string>& out) {
    out.clear();
    if (s.empty()) return;
    std::string cur;
    for (char c : s) {
        if (c == delim) {
            out.push_back(cur);
            cur.clear();
        } else cur.push_back(c);
    }
    if (!cur.empty()) out.push_back(cur);
}

static std::string join_serialized(const std::vector<std::string>& v, char delim) {
    std::string s;
    bool first = true;
    for (const auto& it : v) {
        if (!first) s.push_back(delim);
        s += it;
        first = false;
    }
    return s;
}

void SymptomDiseaseGraph::addNode(const std::string& node, const std::string& type) {
    if (!nodeTypeMap->contains(node)) {
        nodeTypeMap->put(node, type);
        adjacencyMap->put(node, "");
    }
}

void SymptomDiseaseGraph::addEdge(const std::string& from, const std::string& to, bool bidirectional) {
    addNode(from, "symptom");
    addNode(to, "disease");

    // get existing neighbors
    std::string ser = adjacencyMap->get(from, "");
    std::vector<std::string> neigh;
    split_serialized(ser, DELIM, neigh);
    // avoid duplicates
    bool found = false;
    for (const auto& n : neigh) if (n == to) { found = true; break; }
    if (!found) {
        neigh.push_back(to);
        adjacencyMap->put(from, join_serialized(neigh, DELIM));
    }

    if (bidirectional) {
        std::string ser2 = adjacencyMap->get(to, "");
        std::vector<std::string> neigh2;
        split_serialized(ser2, DELIM, neigh2);
        bool found2 = false;
        for (const auto& n : neigh2) if (n == from) { found2 = true; break; }
        if (!found2) {
            neigh2.push_back(from);
            adjacencyMap->put(to, join_serialized(neigh2, DELIM));
        }
    }
}

std::vector<std::string> SymptomDiseaseGraph::getNeighbors(const std::string& node) {
    std::string ser = adjacencyMap->get(node, "");
    std::vector<std::string> neigh;
    split_serialized(ser, DELIM, neigh);
    return neigh;
}

std::vector<std::string> SymptomDiseaseGraph::getDiseasesForSymptom(const std::string& symptom) {
    return getNeighbors(symptom);
}

std::vector<std::string> SymptomDiseaseGraph::getSymptomsForDisease(const std::string& disease) {
    std::vector<std::string> symptoms;
    std::vector<std::string> keys = adjacencyMap->keys();
    for (const auto& key : keys) {
        if (nodeTypeMap->get(key, "") == "symptom") {
            std::vector<std::string> neigh;
            split_serialized(adjacencyMap->get(key, ""), DELIM, neigh);
            for (const auto& n : neigh) if (n == disease) { symptoms.push_back(key); break; }
        }
    }
    return symptoms;
}

bool SymptomDiseaseGraph::hasNode(const std::string& node) {
    return nodeTypeMap->contains(node);
}

std::string SymptomDiseaseGraph::getNodeType(const std::string& node) {
    return nodeTypeMap->get(node, "");
}

void SymptomDiseaseGraph::clear() {
    adjacencyMap->clear();
    nodeTypeMap->clear();
}

int SymptomDiseaseGraph::size() {
    return nodeTypeMap->size();
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
MedicalSet::MedicalSet() {
    map = new MedicalHashMap();
}

MedicalSet::~MedicalSet() {
    if (map) delete map;
}

void MedicalSet::add(const std::string& item) {
    map->put(item, "1");
}

void MedicalSet::remove(const std::string& item) {
    map->remove(item);
}

bool MedicalSet::contains(const std::string& item) {
    return map->contains(item);
}

void MedicalSet::clear() {
    map->clear();
}

int MedicalSet::size() {
    return map->size();
}

std::vector<std::string> MedicalSet::toVector() {
    return map->keys();
}

// Explicit template instantiations for pybind
template class MedicalLinkedList<std::string>;

