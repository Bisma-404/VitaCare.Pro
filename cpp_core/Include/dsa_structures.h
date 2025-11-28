#ifndef DSA_STRUCTURES_H
#define DSA_STRUCTURES_H

#include <string>
#include <vector>
#include <queue>
#include <stack>
#include <list>
#include <algorithm>
#include <functional>
#include <stdexcept>

// Note: internal DSA implementations aim to avoid using STL containers
// for core storage when possible. `MedicalHashMap` uses a custom
// open-addressing double-hash table implemented with raw arrays.

// ============================================================================
// HASH MAP - For O(1) threshold lookups and parameter normalization
// ============================================================================
class MedicalHashMap {
private:
    // Open-addressing table (double hashing). We keep raw arrays for keys
    // and values to avoid using std::unordered_map. Empty slots are marked
    // with occupied = false, deleted = false.
    struct Entry {
        std::string key;
        std::string value;
        bool occupied;
        bool deleted;
        Entry() : key(), value(), occupied(false), deleted(false) {}
    };

    Entry* table;
    int capacity; // m
    int count;    // n
    double max_load_factor;

    // Helpers
    unsigned long hash1(const std::string& s) const;
    unsigned long hash2(const std::string& s) const;
    void ensure_capacity_for_insert();
    void rehash(int new_capacity);
    int find_index(const std::string& key) const; // returns -1 if not found

public:
    MedicalHashMap(int initial_capacity = 17, double load_factor = 0.6);
    ~MedicalHashMap();

    void put(const std::string& key, const std::string& value);
    std::string get(const std::string& key, const std::string& default_val = "");
    bool contains(const std::string& key);
    bool remove(const std::string& key);
    void clear();
    int size();
    std::vector<std::string> keys();
    std::vector<std::string> values();
};

// ============================================================================
// STACK - For reverse chronological access to past reports (LIFO)
// ============================================================================
// ---------------------------------------------------------------------------
// STRING STACK - array-backed stack for strings (avoids std::stack)
// ---------------------------------------------------------------------------
class StringStack {
private:
    std::string* arr;
    int capacity;
    int topIndex; // points to next free slot
    int maxSizeLimit;

    void grow_if_needed();

public:
    StringStack(int max_size = 5);
    ~StringStack();
    void push(const std::string& item);
    std::string pop();
    std::string peek();
    bool isEmpty();
    int size();
    void clear();
    std::vector<std::string> getAll();
};

// ============================================================================
// QUEUE - For managing patient request order (FIFO)
// ============================================================================
// ---------------------------------------------------------------------------
// STRING QUEUE - circular buffer for strings (avoids std::queue)
// ---------------------------------------------------------------------------
class StringQueue {
private:
    std::string* buffer;
    int capacity;
    int head; // index of first element
    int tail; // index of one past last
    int count;

    void grow_if_needed();

public:
    StringQueue();
    ~StringQueue();
    void enqueue(const std::string& item);
    std::string dequeue();
    std::string peek();
    bool isEmpty();
    int size();
    void clear();
};

// ============================================================================
// PRIORITY QUEUE / HEAP - For ranking diseases by risk scores
// ============================================================================
struct PriorityItem {
    std::string disease_type;
    std::string disease_name;
    int prediction;
    double risk_score;
    std::string risk_level;
    
    PriorityItem() : prediction(0), risk_score(0.0) {}
    PriorityItem(const std::string& type, const std::string& name, int pred, double score, const std::string& level)
        : disease_type(type), disease_name(name), prediction(pred), risk_score(score), risk_level(level) {}
};

class MedicalPriorityQueue {
private:
    PriorityItem* heapArr;
    int capacity;
    int heapSize;
    bool maxHeap;

    void grow_heap();
    void heapifyUp(int index);
    void heapifyDown(int index);
    int parent(int i) { return (i - 1) / 2; }
    int left(int i) { return 2 * i + 1; }
    int right(int i) { return 2 * i + 2; }

public:
    MedicalPriorityQueue(bool max_heap = true);
    ~MedicalPriorityQueue();
    void enqueue(const PriorityItem& item);
    PriorityItem dequeue();
    PriorityItem peek();
    bool isEmpty();
    int size();
    void clear();
    std::vector<PriorityItem> getAll();
};

// ============================================================================
// GRAPH - For symptom-disease relationships
// ============================================================================
class SymptomDiseaseGraph {
private:
    // Use MedicalHashMap to avoid STL containers in core internals.
    // adjacencyMap maps node -> serialized neighbor list (DELIM separated)
    MedicalHashMap* adjacencyMap;
    // nodeTypeMap maps node -> node type string ("symptom" or "disease")
    MedicalHashMap* nodeTypeMap;
    const char DELIM = '\x1E'; // record separator unlikely in names

public:
    SymptomDiseaseGraph();
    ~SymptomDiseaseGraph();
    void addNode(const std::string& node, const std::string& type);
    void addEdge(const std::string& from, const std::string& to, bool bidirectional = false);
    std::vector<std::string> getNeighbors(const std::string& node);
    std::vector<std::string> getDiseasesForSymptom(const std::string& symptom);
    std::vector<std::string> getSymptomsForDisease(const std::string& disease);
    bool hasNode(const std::string& node);
    std::string getNodeType(const std::string& node);
    void clear();
    int size();
};

// ============================================================================
// LINKED LIST - For maintaining chronological patient reports
// ============================================================================
template<typename T>
struct ListNode {
    T data;
    ListNode* next;
    ListNode* prev;
    
    ListNode(const T& item) : data(item), next(nullptr), prev(nullptr) {}
};

template<typename T>
class MedicalLinkedList {
private:
    ListNode<T>* head;
    ListNode<T>* tail;
    int listSize;
    
public:
    MedicalLinkedList();
    ~MedicalLinkedList();
    void append(const T& item);
    void prepend(const T& item);
    void remove(const T& item);
    bool contains(const T& item);
    int size();
    void clear();
    std::vector<T> toVector();
    T get(int index);
};

// ============================================================================
// SET - For storing unique symptoms
// ============================================================================
class MedicalSet {
private:
    // Backed by MedicalHashMap (key -> "1") to avoid STL usage
    MedicalHashMap* map;

public:
    MedicalSet();
    ~MedicalSet();
    void add(const std::string& item);
    void remove(const std::string& item);
    bool contains(const std::string& item);
    void clear();
    int size();
    std::vector<std::string> toVector();
};

#endif // DSA_STRUCTURES_H

