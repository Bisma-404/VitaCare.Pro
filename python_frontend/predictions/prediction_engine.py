"""
Prediction Engine integrating DSA rules and ML fallback.
Uses DSA structures first, falls back to ML if inconclusive.
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# Use C++ DSA implementations via wrapper
from utils.cpp_dsa_wrapper import HashMap as MedicalHashMap, Stack as MedicalStack, Queue, PriorityQueue, SymptomDiseaseGraph, Set as MedicalSet
from dsa_engine.arrays import MedicalArray
from dsa_engine.linked_list import MedicalLinkedList
from dsa_engine.trees import DecisionTree

from database.models import DiseaseThresholdDAO, PatientReportDAO
from utils.mapping import get_disease_config, extract_features_from_form

# Import C++ tree module for ML fallback
try:
    import cpp_tree
except ImportError:
    print("Warning: cpp_tree module not found.")
    cpp_tree = None


class PredictionEngine:
    """Main prediction engine combining DSA and ML."""
    
    def __init__(self):
        """Initialize prediction engine."""
        # Initialize DSA structures (using C++ implementations)
        self.threshold_map = MedicalHashMap()  # Disease thresholds (C++ HashMap)
        self.symptom_graph = SymptomDiseaseGraph()  # Symptom-disease relationships (C++ Graph)
        self.decision_tree = DecisionTree()  # Decision rules
        self.priority_heap = PriorityQueue(max_heap=True)  # Disease ranking (C++ PriorityQueue)
        
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
            from webapp.ocr_utils import get_default_values
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
        
        return dsa_result
    
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

