#ifndef DECISION_TREE_SIMPLE_H
#define DECISION_TREE_SIMPLE_H

#include <iostream>
#include <vector>
#include <cmath>
#include <fstream>
using namespace std;

struct DataPointS {
    vector<double> features;
    int label;
};

struct NodeS {
    bool isLeaf;
    int prediction;
    int featureIndex;
    double threshold;
    NodeS* left;
    NodeS* right;
    NodeS() {
        isLeaf = false;
        prediction = -1;
        featureIndex = -1;
        threshold = 0.0;
        left = right = nullptr;
    }
};

class SimpleDecisionTree {
private:
    NodeS* root;
    int maxDepth;
    int minSamples;
    string criterion;

    double calcEntropy(const vector<int>& labels);
    double calcGini(const vector<int>& labels);
    double calcImpurity(const vector<int>& labels);
    double infoGain(const vector<int>& parent, const vector<int>& left, const vector<int>& right);
    bool allSameLabel(const vector<DataPointS>& data);
    int majorityLabel(const vector<DataPointS>& data);
    void splitData(const vector<DataPointS>& data, int featureIndex, double threshold, vector<DataPointS>& left, vector<DataPointS>& right);
    NodeS* buildTree(const vector<DataPointS>& data, int depth);
    int predictOne(const vector<double>& features, NodeS* node);
    void deleteNodes(NodeS* node);
    // Saving / Loading
    void saveNode(ofstream& out, NodeS* node);
    NodeS* loadNode(ifstream& in);
public:
    SimpleDecisionTree();
    ~SimpleDecisionTree();
    void train(const vector<DataPointS>& data, int maxD = 3, int minS = 2, string crit = "entropy");
    int predict(const vector<double>& features);
    vector<int> predictBatch(const vector<vector<double>>& featureBatch);
    bool save(string path);
    bool load(string path);
};

#endif
