#ifndef DSA_STRUCTURES_H
#define DSA_STRUCTURES_H

#include <string>
#include <vector>
#include <unordered_map>
#include <queue>
#include <stack>
#include <list>
#include <algorithm>
#include <functional>
#include <stdexcept>

// ============================================================================
// HASH MAP - For O(1) threshold lookups and parameter normalization
// ============================================================================
class MedicalHashMap {
private:
    std::unordered_map<std::string, std::string> map;
    
public:
    MedicalHashMap();
    void put(const std::string& key, const std::string& value);
    std::string get(const std::string& key, const std::string& default_val = "");
    bool contains(const std::string& key);
    void clear();
    int size();
    std::vector<std::string> keys();
    std::vector<std::string> values();
};

// ============================================================================
// STACK - For reverse chronological access to past reports (LIFO)
// ============================================================================
template<typename T>
class MedicalStack {
private:
    std::stack<T> stack;
    int maxSize;
    
public:
    MedicalStack(int max_size = 5);
    void push(const T& item);
    T pop();
    T peek();
    bool isEmpty();
    int size();
    void clear();
    std::vector<T> getAll();
};

// ============================================================================
// QUEUE - For managing patient request order (FIFO)
// ============================================================================
template<typename T>
class MedicalQueue {
private:
    std::queue<T> queue;
    
public:
    MedicalQueue();
    void enqueue(const T& item);
    T dequeue();
    T peek();
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
    std::vector<PriorityItem> heap;
    bool maxHeap;
    
    void heapifyUp(int index);
    void heapifyDown(int index);
    int parent(int i) { return (i - 1) / 2; }
    int left(int i) { return 2 * i + 1; }
    int right(int i) { return 2 * i + 2; }
    
public:
    MedicalPriorityQueue(bool max_heap = true);
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
    std::unordered_map<std::string, std::vector<std::string>> adjacencyList;
    std::unordered_map<std::string, std::string> nodeTypes; // "symptom" or "disease"
    
public:
    SymptomDiseaseGraph();
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
    std::unordered_map<std::string, bool> set;
    
public:
    MedicalSet();
    void add(const std::string& item);
    void remove(const std::string& item);
    bool contains(const std::string& item);
    void clear();
    int size();
    std::vector<std::string> toVector();
};

#endif // DSA_STRUCTURES_H

