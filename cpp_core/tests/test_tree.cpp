#include <iostream>
#include "../Include/decision_tree.h"
using namespace std;
using namespace ml;

int main() {
    // Simple toy data: Predicts class 0 if first feature ≤ 1, else 1.
    vector<DataPoint> data = {
        DataPoint({0.5, 2.0}, 0),
        DataPoint({1.1, 1.0}, 1),
        DataPoint({0.2, 4.2}, 0),
        DataPoint({2.0, 0.1}, 1),
        DataPoint({0.9, 2.2}, 0),
        DataPoint({2.4, 3.3}, 1)
    };

    DecisionTree tree;
    tree.train(data, 3, 2, "entropy");

    cout << "\n=== Decision Tree Test Sample ===\n\n";
    int correct = 0;
    for (size_t i = 0; i < data.size(); ++i) {
        int pred = tree.predict(data[i].features);
        cout << "Sample " << i << ": true=" << data[i].label << ", predicted=" << pred << endl;
        if (pred == data[i].label) correct++;
    }
    cout << "\nAccuracy on train set: " << (100.0 * correct / data.size()) << "%\n";

    // Save and reload
    string modelfile = "test_model.txt";
    if (tree.save(modelfile)) cout << "Model saved to " << modelfile << endl;
    DecisionTree loaded_tree;
    if (loaded_tree.load(modelfile)) {
        cout << "Model loaded from " << modelfile << ". Prediction for {1.0, 1.0}: " << loaded_tree.predict({1.0, 1.0}) << endl;
    } else {
        cout << "Failed to load model from file." << endl;
    }
    cout << "\n=== End of test ===\n";
    return 0;
}
