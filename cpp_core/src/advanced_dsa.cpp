#include "../Include/advanced_dsa.h"
#include <algorithm>
#include <cmath>

// ============================================================================
// SORTING IMPLEMENTATIONS
// ============================================================================
std::vector<std::pair<std::string, double>> MedicalSorting::quickSortByScore(
    std::vector<std::pair<std::string, double>>& items, bool descending) {
    if (items.size() <= 1) return items;
    
    auto comparator = descending ? compareDescending : compareAscending;
    std::sort(items.begin(), items.end(), comparator);
    return items;
}

std::vector<std::pair<std::string, double>> MedicalSorting::mergeSortByScore(
    std::vector<std::pair<std::string, double>> items, bool descending) {
    if (items.size() <= 1) return items;
    
    auto comparator = descending ? compareDescending : compareAscending;
    std::stable_sort(items.begin(), items.end(), comparator);
    return items;
}

bool MedicalSorting::compareDescending(const std::pair<std::string, double>& a,
                                        const std::pair<std::string, double>& b) {
    return a.second > b.second;
}

bool MedicalSorting::compareAscending(const std::pair<std::string, double>& a,
                                       const std::pair<std::string, double>& b) {
    return a.second < b.second;
}

// ============================================================================
// BINARY SEARCH IMPLEMENTATIONS
// ============================================================================
int MedicalBinarySearch::search(const std::vector<std::string>& sortedList,
                                 const std::string& target) {
    int left = 0, right = static_cast<int>(sortedList.size()) - 1;
    
    while (left <= right) {
        int mid = left + (right - left) / 2;
        if (sortedList[mid] == target) return mid;
        if (sortedList[mid] < target) left = mid + 1;
        else right = mid - 1;
    }
    return -1;
}

std::vector<std::string> MedicalBinarySearch::rangeSearch(
    const std::vector<std::string>& sortedList,
    const std::string& minVal,
    const std::string& maxVal) {
    std::vector<std::string> result;
    
    auto lower = std::lower_bound(sortedList.begin(), sortedList.end(), minVal);
    auto upper = std::upper_bound(sortedList.begin(), sortedList.end(), maxVal);
    
    result.insert(result.end(), lower, upper);
    return result;
}

// ============================================================================
// SYMPTOM MANAGER IMPLEMENTATIONS
// ============================================================================
SymptomManager::SymptomManager() {}

void SymptomManager::loadSymptoms(const std::vector<std::string>& symptoms) {
    allSymptoms = symptoms;
    std::sort(allSymptoms.begin(), allSymptoms.end());
}

std::vector<std::string> SymptomManager::getSymptoms() const {
    return allSymptoms;
}

std::vector<std::string> SymptomManager::searchByPrefix(const std::string& prefix) const {
    std::vector<std::string> results;
    
    for (const auto& symptom : allSymptoms) {
        if (symptom.find(prefix) == 0) {
            results.push_back(symptom);
        }
    }
    
    return results;
}

std::vector<std::string> SymptomManager::getMostCommonSymptoms(int count) const {
    std::vector<std::pair<std::string, int>> sorted = symptomFrequency;
    std::sort(sorted.begin(), sorted.end(),
              [](const auto& a, const auto& b) { return a.second > b.second; });
    
    std::vector<std::string> result;
    for (int i = 0; i < std::min(count, static_cast<int>(sorted.size())); ++i) {
        result.push_back(sorted[i].first);
    }
    
    return result;
}

void SymptomManager::recordSymptomUsage(const std::string& symptom) {
    auto it = std::find_if(symptomFrequency.begin(), symptomFrequency.end(),
                           [&](const auto& p) { return p.first == symptom; });
    
    if (it != symptomFrequency.end()) {
        it->second++;
    } else {
        symptomFrequency.emplace_back(symptom, 1);
    }
}

std::vector<std::pair<std::string, int>> SymptomManager::getFrequencyAnalytics() const {
    return symptomFrequency;
}

int SymptomManager::getSymptomCount() const {
    return static_cast<int>(allSymptoms.size());
}

// ============================================================================
// RISK SCORER IMPLEMENTATIONS
// ============================================================================
double RiskScorer::calculateRiskScore(const RiskFactors& factors) {
    // Weighted composite score: normalize all weights sum to 1.0
    double total = factors.symptomWeight + factors.frequencyWeight +
                   factors.comorbidityWeight + factors.ageFactorWeight;
    
    if (total == 0.0) return 0.0;
    
    // Simple weighted average; could use more sophisticated methods
    double score = (factors.symptomWeight * 0.4 +
                    factors.frequencyWeight * 0.3 +
                    factors.comorbidityWeight * 0.2 +
                    factors.ageFactorWeight * 0.1);
    
    return std::min(score, 1.0); // Cap at 100%
}

std::vector<std::pair<std::string, double>> RiskScorer::rankDiseasesByRisk(
    const std::vector<std::pair<std::string, double>>& diseaseScores,
    const RiskFactors& factors) {
    auto ranked = diseaseScores;
    
    // Apply composite score multiplier to each disease
    double compositeMultiplier = calculateRiskScore(factors);
    for (auto& pair : ranked) {
        pair.second *= (1.0 + compositeMultiplier);
    }
    
    // Sort by adjusted score (descending)
    std::sort(ranked.begin(), ranked.end(),
              [](const auto& a, const auto& b) { return a.second > b.second; });
    
    return ranked;
}
