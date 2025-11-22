
#ifndef ADVANCED_DSA_H
#define ADVANCED_DSA_H

#include <string>
#include <vector>
#include <algorithm>
#include <functional>

// ============================================================================
// RISK FACTORS - Multi-factor risk scoring data structure
// ============================================================================
struct RiskFactors {
    double symptomWeight = 0.0;      // 0-1
    double frequencyWeight = 0.0;    // 0-1
    double comorbidityWeight = 0.0;  // 0-1
    double ageFactorWeight = 0.0;    // 0-1
};

// ============================================================================
// SORTING - QuickSort, MergeSort for efficient symptom/disease ranking
// ============================================================================
class MedicalSorting {
public:
    // Sort key-value pairs by value (for risk scores, frequencies)
    static std::vector<std::pair<std::string, double>> quickSortByScore(
        std::vector<std::pair<std::string, double>>& items, bool descending = true);
    
    static std::vector<std::pair<std::string, double>> mergeSortByScore(
        std::vector<std::pair<std::string, double>> items, bool descending = true);
    
    // Helper comparators
    static bool compareDescending(const std::pair<std::string, double>& a, 
                                   const std::pair<std::string, double>& b);
    static bool compareAscending(const std::pair<std::string, double>& a,
                                  const std::pair<std::string, double>& b);
};

// ============================================================================
// BINARY SEARCH - Fast lookup in sorted symptom/disease lists
// ============================================================================
class MedicalBinarySearch {
public:
    // Search for a value in sorted array, return index or -1
    static int search(const std::vector<std::string>& sortedList, const std::string& target);
    
    // Range search: find all items in range [minVal, maxVal]
    static std::vector<std::string> rangeSearch(
        const std::vector<std::string>& sortedList, 
        const std::string& minVal, 
        const std::string& maxVal);
};

// ============================================================================
// SYMPTOM MANAGER - Extract, cache, and manage symptoms from DB
// ============================================================================
class SymptomManager {
private:
    std::vector<std::string> allSymptoms;
    std::vector<std::pair<std::string, int>> symptomFrequency; // For analytics
    
public:
    SymptomManager();
    
    // Load symptoms from external data (called from Python)
    void loadSymptoms(const std::vector<std::string>& symptoms);
    
    // Get all symptoms
    std::vector<std::string> getSymptoms() const;
    
    // Search symptoms by prefix (auto-complete)
    std::vector<std::string> searchByPrefix(const std::string& prefix) const;
    
    // Get most common symptoms
    std::vector<std::string> getMostCommonSymptoms(int count) const;
    
    // Add symptom frequency (used during predictions)
    void recordSymptomUsage(const std::string& symptom);
    
    // Get frequency analytics
    std::vector<std::pair<std::string, int>> getFrequencyAnalytics() const;
    
    int getSymptomCount() const;
};

// ============================================================================
// RISK SCORER - Advanced scoring using multiple factors
// ============================================================================
class RiskScorer {
public:
    // Calculate composite risk score
    static double calculateRiskScore(const RiskFactors& factors);
    
    // Rank diseases by composite score
    static std::vector<std::pair<std::string, double>> rankDiseasesByRisk(
        const std::vector<std::pair<std::string, double>>& diseaseScores,
        const RiskFactors& factors);
};

#endif // ADVANCED_DSA_H
