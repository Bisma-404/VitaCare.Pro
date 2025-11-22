"""
Prediction Engine integrating DSA rules and ML fallback.
Uses DSA structures first, falls back to ML if inconclusive.
Enhanced with advanced sorting and risk scoring algorithms.
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# Use C++ DSA implementations via wrapper
from utils.cpp_dsa_wrapper import (
    MedicalHashMap,
    Stack as MedicalStack, 
    Queue, 
    MedicalPriorityQueue,
    SymptomDiseaseGraphWrapper as SymptomDiseaseGraph,
    MedicalSet
)
from dsa_engine.arrays import MedicalArray
from dsa_engine.linked_list import MedicalLinkedList
from dsa_engine.trees import DecisionTree

from database.models import DiseaseThresholdDAO, PatientReportDAO
from utils.mapping import get_disease_config

# Import C++ tree module for ML fallback and advanced DSA
try:
    import cpp_tree
    from cpp_tree import MedicalSorting, RiskScorer, RiskFactors, SymptomManager
    CPP_AVAILABLE = True
except ImportError:
    print("Warning: cpp_tree module not fully available.")
    cpp_tree = None
    CPP_AVAILABLE = False


class PredictionEngine:
    """Main prediction engine combining DSA and ML."""
    
    def __init__(self):
        """Initialize prediction engine."""
        # Initialize DSA structures (using C++ implementations)
        self.threshold_map = MedicalHashMap()  # Disease thresholds (C++ HashMap)
        self.symptom_graph = SymptomDiseaseGraph()  # Symptom-disease relationships (C++ Graph)
        self.decision_tree = DecisionTree()  # Decision rules
        self.priority_heap = MedicalPriorityQueue(max_heap=True)  # Disease ranking (C++ PriorityQueue)
        
        # Load thresholds from database
        self._load_thresholds()
        
        # Load symptom-disease relationships
        self._load_symptom_disease_network()
    
    def _load_thresholds(self):
        """Load disease thresholds from database into HashMap."""
        thresholds = DiseaseThresholdDAO.get_all_thresholds()
        
        for threshold in thresholds:
            disease_name = threshold['disease_name']
            param_name = threshold['parameter_name']
            key = f"{disease_name}:{param_name}"
            
            self.threshold_map.put(key, {
                'min': threshold['min_value'],
                'max': threshold['max_value'],
                'unit': threshold['unit']
            })
    
    def _load_symptom_disease_network(self):
        """Load symptom-disease relationships into graph."""
        # Sample symptom-disease mappings (can be loaded from database)
        mappings = {
            'chest_pain': ['heart_disease'],
            'shortness_of_breath': ['heart_disease', 'diabetes'],
            'fatigue': ['heart_disease', 'diabetes', 'breast_cancer'],
            'blurred_vision': ['diabetes'],
            'frequent_urination': ['diabetes'],
            'dizziness': ['heart_disease', 'diabetes'],
            'nausea': ['heart_disease', 'diabetes', 'breast_cancer'],
            'weight_changes': ['diabetes', 'breast_cancer'],
        }
        
        for symptom, diseases in mappings.items():
            self.symptom_graph.add_node(symptom, 'symptom')
            for disease in diseases:
                self.symptom_graph.add_node(disease, 'disease')
                self.symptom_graph.add_edge(symptom, disease, bidirectional=False)
    
    def analyze_with_dsa(self, test_data, symptoms, disease_type):
        """
        Analyze using DSA structures (primary method).
        Returns: (result, confidence, method_used)
        """
        # Convert test data to array
        test_array = MedicalArray()
        for key, value in test_data.items():
            test_array.append({'param': key, 'value': value})
        
        # Check thresholds using HashMap
        threshold_violations = []
        risk_score = 0
        
        for i in range(len(test_array)):
            test = test_array.get(i)
            param = test['param']
            value = test['value']
            
            # Check threshold
            threshold_key = f"{disease_type}:{param}"
            threshold = self.threshold_map.get(threshold_key)
            
            if threshold:
                min_val = threshold['min']
                max_val = threshold['max']
                
                if value < min_val or value > max_val:
                    threshold_violations.append({
                        'parameter': param,
                        'value': value,
                        'normal_range': f"{min_val}-{max_val}"
                    })
                    risk_score += 20
        
        # Check symptom correlations using graph
        symptom_matches = 0
        symptom_set = MedicalSet()
        for symptom in symptoms:
            symptom_set.add(symptom.lower().replace(' ', '_'))
        
        for symptom in symptom_set:
            diseases = self.symptom_graph.get_diseases_for_symptom(symptom)
            if disease_type in diseases:
                symptom_matches += 1
                risk_score += 15
        
        # Apply decision tree rules
        decision = self._apply_decision_tree(test_data, disease_type)
        if decision:
            risk_score += decision.get('risk_boost', 0)
        
        # Determine result
        result = 0  # Low risk
        confidence = 0
        
        if risk_score >= 70:
            result = 1  # High risk
            confidence = min(95, risk_score)
        elif risk_score >= 40:
            result = 1  # Medium-high risk
            confidence = risk_score
        else:
            result = 0  # Low risk
            confidence = 100 - risk_score
        
        return {
            'prediction': result,
            'confidence': confidence,
            'risk_score': risk_score,
            'threshold_violations': threshold_violations,
            'symptom_matches': symptom_matches,
            'method': 'DSA',
            'decision_rules_applied': decision is not None
        }
    
    def _apply_decision_tree(self, test_data, disease_type):
        """Apply decision tree rules."""
        # Sample decision rules based on disease type
        if disease_type == 'diabetes':
            glucose = test_data.get('glucose', 0)
            bmi = test_data.get('bmi', 0)
            
            if glucose > 200 or bmi > 35:
                return {'risk_boost': 25, 'rule': 'high_glucose_or_bmi'}
            elif glucose > 140 or bmi > 30:
                return {'risk_boost': 15, 'rule': 'moderate_glucose_or_bmi'}
        
        elif disease_type == 'heart':
            age = test_data.get('age', 0)
            cholesterol = test_data.get('chol', 0)
            
            if age > 60 and cholesterol > 240:
                return {'risk_boost': 30, 'rule': 'high_age_and_chol'}
            elif cholesterol > 240:
                return {'risk_boost': 20, 'rule': 'high_cholesterol'}
        
        return None
    
    def analyze_with_ml(self, test_data, disease_type):
        """
        Analyze using ML model (fallback method).
        Returns: (result, confidence, method_used)
        """
        if cpp_tree is None:
            return None

        def get_remarks(self, disease_type, prediction, features):
            """Generate human-friendly remark text for a prediction.
            Logic adapted from the Version 3 implementation to provide clearer
            messages for diabetes, heart disease and breast cancer.
            """
            try:
                # Build a name->value map using the fields order when possible
                config = get_disease_config(disease_type)
                name_map = {}
                if config and 'fields' in config:
                    for idx, field in enumerate(config['fields']):
                        fname = field['name']
                        if idx < len(features):
                            name_map[fname] = features[idx]
                # DIABETES
                if disease_type == 'diabetes':
                    glucose = float(name_map.get('glucose', 0)) if 'glucose' in name_map else (features[1] if len(features) > 1 else 0)
                    bmi = float(name_map.get('bmi', 0)) if 'bmi' in name_map else (features[5] if len(features) > 5 else 0)
                    if prediction == 1:
                        if glucose > 170:
                            return 'High diabetes risk and very elevated glucose! Please consult a doctor immediately.'
                        elif bmi > 32:
                            return 'High risk and high BMI detected. Talk with your doctor about weight management.'
                        else:
                            return 'High risk detected. Please consult a doctor soon for further assessment.'
                    else:
                        if glucose < 100:
                            return 'No diabetes risk and healthy glucose. Keep it up!'
                        else:
                            return 'No diabetes risk detected. Maintain a healthy lifestyle!'

                # HEART
                if disease_type == 'heart':
                    age = float(name_map.get('age', 0)) if 'age' in name_map else (features[0] if len(features) > 0 else 0)
                    chol = float(name_map.get('chol', 0)) if 'chol' in name_map else (features[4] if len(features) > 4 else 0)
                    if prediction == 1:
                        if age > 60:
                            return 'No heart disease, but your age suggests regular cardiac checkups.'
                        else:
                            return 'No heart disease detected. Keep a healthy routine.'
                    else:
                        if age > 60:
                            return 'AT RISK: Cardiac danger in advanced age. Schedule a cardiology checkup!'
                        elif chol > 240:
                            return 'Warning: High cholesterol and cardiac risk detected. Seek medical attention promptly.'
                        else:
                            return 'Urgent: cardiac risk detected! Schedule a medical appointment now.'

                # BREAST CANCER
                if disease_type == 'breast_cancer':
                    radius_mean = float(name_map.get('radius_mean', 0)) if 'radius_mean' in name_map else (features[0] if len(features) > 0 else 0)
                    if prediction == 1:
                        if radius_mean > 15:
                            return 'Warning: Malignant, large suspicious mass detected. Urgent oncologist referral needed.'
                        else:
                            return 'Warning: suspicious malignant features detected. Please see your oncologist as soon as possible.'
                    else:
                        return 'Benign result. Routine screenings and vigilance are still recommended.'

            except Exception:
                pass

            return 'Result interpretation is unavailable.'
        
        # Load model
        script_dir = os.path.dirname(os.path.abspath(__file__))
        models_dir = os.path.join(script_dir, '..', 'models')
        model_path = os.path.join(models_dir, f'{disease_type}_model.txt')
        model_path = os.path.normpath(model_path)
        
        if not os.path.exists(model_path):
            return None
        
        try:
            model = cpp_tree.DecisionTree()
            loaded = model.load(model_path)
            
            if not loaded:
                return None
            
            # Extract features
            config = get_disease_config(disease_type)
            if not config:
                return None
            
            features = []
            defaults = {}
            from ocr_utils import get_default_values
            defaults = get_default_values(disease_type)
            
            for field in config['fields']:
                field_name = field['name']
                value = test_data.get(field_name)
                if value is None:
                    value = defaults.get(field_name, field.get('default', 0))
                features.append(float(value))
            
            # Make prediction
            prediction = model.predict(features)
            
            # Calculate confidence (simplified - actual ML would provide probability)
            confidence = 75.0  # Default confidence for ML
            
            return {
                'prediction': prediction,
                'confidence': confidence,
                'method': 'ML',
                'features_used': len(features)
            }
            
        except Exception as e:
            print(f"Error in ML prediction: {e}")
            return None
    
    def predict(self, test_data, symptoms, disease_type):
        """
        Main prediction method.
        Uses DSA first, falls back to ML if DSA confidence is low.
        """
        # Try DSA first
        dsa_result = self.analyze_with_dsa(test_data, symptoms, disease_type)
        
        # If DSA confidence is low (< 60), use ML fallback
        if dsa_result['confidence'] < 60:
            ml_result = self.analyze_with_ml(test_data, disease_type)
            
            if ml_result:
                # Combine DSA and ML results
                combined_confidence = (dsa_result['confidence'] * 0.4) + (ml_result['confidence'] * 0.6)
                
                # Use ML prediction if confidence is significantly higher
                if ml_result['confidence'] > dsa_result['confidence'] + 15:
                    return {
                        **ml_result,
                        'confidence': combined_confidence,
                        'method': 'ML (DSA confidence too low)',
                        'dsa_result': dsa_result
                    }
        
        # Determine which result we will return (could be DSA or ML combined)
        final_result = dsa_result

        # If DSA confidence is low (< 60), use ML fallback
        if dsa_result['confidence'] < 60:
            ml_result = self.analyze_with_ml(test_data, disease_type)

            if ml_result:
                # Combine DSA and ML results
                combined_confidence = (dsa_result['confidence'] * 0.4) + (ml_result['confidence'] * 0.6)

                # Use ML prediction if confidence is significantly higher
                if ml_result['confidence'] > dsa_result['confidence'] + 15:
                    final_result = {
                        **ml_result,
                        'confidence': combined_confidence,
                        'method': 'ML (DSA confidence too low)',
                        'dsa_result': dsa_result
                    }

        # Build an ordered features list (matching disease config) to enable human-friendly remarks
        try:
            config = get_disease_config(disease_type)
            from ocr_utils import get_default_values
            defaults = get_default_values(disease_type)
            features = []
            if config and 'fields' in config:
                for field in config['fields']:
                    fname = field['name']
                    val = test_data.get(fname)
                    if val is None:
                        val = defaults.get(fname, field.get('default', 0))
                    try:
                        features.append(float(val))
                    except Exception:
                        features.append(val)
            else:
                # Fallback: use values from test_data
                features = list(test_data.values())
        except Exception:
            features = list(test_data.values())

        # Attach a human-friendly remark based on disease-specific heuristics
        try:
            prediction_value = final_result.get('prediction', 0)
            final_result['remark'] = self.get_remarks(disease_type, prediction_value, features)
        except Exception:
            final_result['remark'] = 'Based on the analysis of provided health metrics.'

        return final_result
    
    def predict_all_diseases(self, test_data, symptoms):
        """
        Predict for all diseases and rank by risk.
        Returns ranked list using C++ PriorityQueue.
        """
        diseases = ['diabetes', 'heart', 'breast_cancer']
        results = []
        
        for disease_type in diseases:
            result = self.predict(test_data, symptoms, disease_type)
            if result:
                # Add to priority heap
                risk_score = result.get('risk_score', result.get('confidence', 0))
                results.append({
                    'disease_type': disease_type,
                    **result
                })
        
        # Rank by risk using C++ PriorityQueue
        ranked_results = []
        heap = PriorityQueue(max_heap=True)
        
        for result in results:
            risk_score = result.get('risk_score', result.get('confidence', 0))
            heap.enqueue(result, risk_score)
        
        # Extract all ranked results
        while not heap.is_empty():
            ranked_results.append(heap.dequeue())
        
        return ranked_results
    
    def analyze_trends(self, current_data, historical_data):
        """
        Analyze trends using Stack.
        Compares current data with historical data.
        """
        # Create stack from historical data (last 5 reports) - using C++ Stack
        history_stack = MedicalStack(max_size=5)
        import json
        for report in historical_data:
            report_str = json.dumps(report)
            history_stack.push(report_str)
        
        trends = {}
        
        if history_stack.is_empty():
            return trends
        
        # Get most recent report from stack
        try:
            last_report_str = history_stack.peek()
            last_report = json.loads(last_report_str)
        except:
            # Fallback: use last item from historical_data
            if historical_data:
                last_report = historical_data[-1]
            else:
                return trends
        
        for param, current_value in current_data.items():
            if isinstance(current_value, (int, float)):
                last_value = last_report.get('test_data', {}).get(param)
                
                if last_value is not None:
                    change = current_value - last_value
                    change_percent = (change / last_value * 100) if last_value != 0 else 0
                    
                    if abs(change_percent) < 5:
                        trend = "stable"
                        symbol = "→"
                    elif change_percent > 0:
                        trend = "increasing"
                        symbol = "↑"
                    else:
                        trend = "decreasing"
                        symbol = "↓"
                    
                    trends[param] = {
                        'current': current_value,
                        'previous': last_value,
                        'change': change,
                        'change_percent': round(change_percent, 1),
                        'trend': trend,
                        'symbol': symbol
                    }
        return trends
    
    def rank_diseases_advanced(self, disease_scores):
        """
        Rank diseases using C++ MedicalSorting (QuickSort/MergeSort).
        disease_scores: List of tuples [(disease_name, score), ...]
        Returns: Sorted list by score (descending)
        """
        if not CPP_AVAILABLE or MedicalSorting is None:
            # Fallback to Python sorting
            return sorted(disease_scores, key=lambda x: x[1], reverse=True)
        
        try:
            # Convert to format expected by C++ sorter
            score_pairs = [(disease, float(score)) for disease, score in disease_scores]
            
            # Use C++ QuickSort for performance
            sorted_scores = MedicalSorting.quick_sort_by_score(score_pairs, descending=True)
            
            return sorted_scores
        except Exception as e:
            print(f"Error in DSA sorting: {e}")
            return sorted(disease_scores, key=lambda x: x[1], reverse=True)
    
    def calculate_composite_risk(self, disease_scores, symptom_weight=0.4, 
                                frequency_weight=0.3, comorbidity_weight=0.2, 
                                age_factor_weight=0.1):
        """
        Calculate composite risk score using C++ RiskScorer.
        Applies multiple factors to rank diseases more accurately.
        """
        if not CPP_AVAILABLE or RiskScorer is None or RiskFactors is None:
            # Fallback: simple weighted average
            return sorted(disease_scores, key=lambda x: x[1], reverse=True)
        
        try:
            # Create risk factors
            factors = RiskFactors()
            factors.symptom_weight = symptom_weight
            factors.frequency_weight = frequency_weight
            factors.comorbidity_weight = comorbidity_weight
            factors.age_factor_weight = age_factor_weight
            
            # Convert to format expected by RiskScorer
            score_pairs = [(disease, float(score)) for disease, score in disease_scores]
            
            # Get ranked results using composite scoring
            ranked = RiskScorer.rank_diseases_by_risk(score_pairs, factors)
            
            return ranked
        except Exception as e:
            print(f"Error in composite risk calculation: {e}")
            return sorted(disease_scores, key=lambda x: x[1], reverse=True)
    
    def extract_symptoms_from_db(self):
        """
        Extract all symptoms from database and load into C++ SymptomManager.
        Used for fast symptom lookup and autocomplete.
        """
        if not CPP_AVAILABLE or SymptomManager is None:
            return None
        
        try:
            from database.db_connection import get_db_connection
            
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)
            
            # Get all unique symptoms
            cursor.execute("""
                SELECT DISTINCT symptom_name 
                FROM symptoms 
                ORDER BY symptom_name ASC
            """)
            
            symptoms = [row['symptom_name'] for row in cursor.fetchall()]
            cursor.close()
            conn.close()
            
            # Initialize and load symptom manager
            sym_manager = SymptomManager()
            sym_manager.load_symptoms(symptoms)
            
            return sym_manager
        except Exception as e:
            print(f"Error loading symptoms: {e}")
            return None
    
    def search_symptoms_fast(self, prefix):
        """
        Fast symptom search using DSA binary search.
        """
        if not CPP_AVAILABLE:
            return []
        
        try:
            sym_manager = self.extract_symptoms_from_db()
            if sym_manager:
                results = sym_manager.search_by_prefix(prefix)
                return results
        except Exception as e:
            print(f"Error in symptom search: {e}")
        
        return []

