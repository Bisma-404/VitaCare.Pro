#include "../Include/decision_tree_simple.h"
#include "../Include/custom_map.h"
#include "../Include/custom_set.h"
#include <sstream>
using namespace std;

SimpleDecisionTree::SimpleDecisionTree() {
    root = nullptr;
    maxDepth = 3;
    minSamples = 2;
    criterion = "entropy";
}
SimpleDecisionTree::~SimpleDecisionTree() {
    deleteNodes(root);
}
void SimpleDecisionTree::deleteNodes(NodeS* node) {
    if (node == nullptr) return;
    deleteNodes(node->left);
    deleteNodes(node->right);
    delete node;
}

double SimpleDecisionTree::calcEntropy(const vector<int>& labels) {
    CustomMap<int, int> counts;
    for(auto label : labels) counts[label]++;
    double entropy = 0.0;
    int total = labels.size();
    for(auto it = counts.begin(); it != counts.end(); ++it) {
        auto x = *it;
        double p = double(x.value) / total;
        if (p > 0) entropy -= p * log2(p);
    }
    return entropy;
}
double SimpleDecisionTree::calcGini(const vector<int>& labels) {
    CustomMap<int, int> counts;
    for(auto label : labels) counts[label]++;
    double gini = 1.0;
    int total = labels.size();
    for(auto it = counts.begin(); it != counts.end(); ++it) {
        auto x = *it;
        double p = double(x.value) / total;
        gini -= p * p;
    }
    return gini;
}
double SimpleDecisionTree::calcImpurity(const vector<int>& labels) {
    if (criterion == "gini") return calcGini(labels);
    return calcEntropy(labels);
}
double SimpleDecisionTree::infoGain(const vector<int>& parent, const vector<int>& left, const vector<int>& right) {
    double pi = calcImpurity(parent);
    int n = parent.size(), nl = left.size(), nr = right.size();
    if (nl == 0 || nr == 0) return 0.0;
    double lw = double(nl) / n, rw = double(nr) / n;
    double c = lw * calcImpurity(left) + rw * calcImpurity(right);
    return pi - c;
}
bool SimpleDecisionTree::allSameLabel(const vector<DataPointS>& data) {
    if (data.empty()) return true;
    int first = data[0].label;
    for(auto& d : data) if (d.label != first) return false;
    return true;
}
int SimpleDecisionTree::majorityLabel(const vector<DataPointS>& data) {
    CustomMap<int, int> c;
    for(auto& d : data) c[d.label]++;
    int maj = -1, mc = 0;
    for(auto it = c.begin(); it != c.end(); ++it) {
        auto x = *it;
        if(x.value > mc) { mc = x.value; maj = x.key; }
    }
    return maj;
}
void SimpleDecisionTree::splitData(const vector<DataPointS>& data, int featureIndex, double threshold, vector<DataPointS>& left, vector<DataPointS>& right) {
    for(auto& d : data) {
        if(d.features[featureIndex] <= threshold) left.push_back(d);
        else right.push_back(d);
    }
}
NodeS* SimpleDecisionTree::buildTree(const vector<DataPointS>& data, int depth) {
    NodeS* node = new NodeS();
    if (data.empty() || allSameLabel(data) || depth >= maxDepth || int(data.size()) < minSamples) {
        node->isLeaf = true;
        node->prediction = majorityLabel(data);
        return node;
    }
    int nfeat = data[0].features.size();
    double bestGain = -1e9; int bestFeat = -1; double bestThresh = 0;
    vector<DataPointS> bestL, bestR;
    vector<int> parentLabels;
    for(auto& d : data) parentLabels.push_back(d.label);
    for(int feat = 0; feat < nfeat; ++feat) {
        CustomSet<double> vals;
        for(auto& d : data) vals.insert(d.features[feat]);
        vector<double> sorted = vals.toVector();
        for(size_t i = 0; i + 1 < sorted.size(); ++i) {
            double threshold = (sorted[i] + sorted[i+1])/2.0;
            vector<DataPointS> l, r;
            vector<int> ll, rr;
            for(auto& d : data) {
                if(d.features[feat] <= threshold) { l.push_back(d); ll.push_back(d.label); }
                else { r.push_back(d); rr.push_back(d.label); }
            }
            if(l.empty() || r.empty()) continue;
            double gain = infoGain(parentLabels, ll, rr);
            if (gain > bestGain) {
                bestGain = gain; bestFeat = feat; bestThresh = threshold; bestL = l; bestR = r;
            }
        }
    }
    if(bestGain <= 0 || bestL.empty() || bestR.empty()) {
        node->isLeaf = true;
        node->prediction = majorityLabel(data);
        return node;
    }
    node->featureIndex = bestFeat;
    node->threshold = bestThresh;
    node->left = buildTree(bestL, depth+1);
    node->right = buildTree(bestR, depth+1);
    return node;
}
void SimpleDecisionTree::train(const vector<DataPointS>& data, int maxD, int minS, string crit) {
    if(root) deleteNodes(root);
    root = nullptr;
    maxDepth = maxD;
    minSamples = minS;
    criterion = crit;
    root = buildTree(data, 0);
}
int SimpleDecisionTree::predictOne(const vector<double>& features, NodeS* node) {
    if (!node) return -1;
    if (node->isLeaf) return node->prediction;
    if (features[node->featureIndex] <= node->threshold) return predictOne(features, node->left);
    else return predictOne(features, node->right);
}
int SimpleDecisionTree::predict(const vector<double>& features) {
    return predictOne(features, root);
}
vector<int> SimpleDecisionTree::predictBatch(const vector<vector<double>>& featureBatch) {
    vector<int> preds;
    for(auto& x : featureBatch) preds.push_back(predict(x));
    return preds;
}
// --- Save / Load, same simple pre-order as previous ---
bool SimpleDecisionTree::save(string path) {
    ofstream out(path);
    if(!out.is_open() || !root) return false;
    out << maxDepth << ' ' << minSamples << ' ' << criterion << '\n';
    saveNode(out, root);
    return true;
}
void SimpleDecisionTree::saveNode(ofstream& out, NodeS* node) {
    if(!node) { out << "#\n"; return; }
    out << node->isLeaf << ' ' << node->prediction << ' ' << node->featureIndex << ' ' << node->threshold << '\n';
    saveNode(out, node->left);
    saveNode(out, node->right);
}
bool SimpleDecisionTree::load(string path) {
    if(root) deleteNodes(root); root=nullptr;
    ifstream in(path);
    if(!in.is_open()) return false;
    in >> maxDepth >> minSamples >> criterion;
    string dummy; getline(in, dummy);
    root = loadNode(in);
    return bool(root);
}
NodeS* SimpleDecisionTree::loadNode(ifstream& in) {
    string line;
    if(!std::getline(in,line)) return nullptr;
    if(line.empty() || line[0]=='#') return nullptr;
    std::istringstream iss(line);
    NodeS* node = new NodeS();
    int il;
    iss >> il >> node->prediction >> node->featureIndex >> node->threshold;
    node->isLeaf = il;
    node->left = loadNode(in);
    node->right = loadNode(in);
    return node;
}
