"""
Prediction Engine using pure DSA-based analysis.
No ML fallback - all predictions based on custom data structures and algorithms.
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
# Note: Python fallback DSA modules removed. Use C++ DSAs via `utils.cpp_dsa_wrapper`.

from database.models import DiseaseThresholdDAO, PatientReportDAO
from utils.mapping import get_disease_config
import csv

# Import C++ DSA module (required)
import cpp_tree
from cpp_tree import MedicalSorting, RiskScorer, RiskFactors, SymptomManager


class PredictionEngine:
    """Pure DSA-based prediction engine."""
    
    def __init__(self):
        """Initialize prediction engine."""
        # Initialize DSA structures (using C++ implementations)
        self.threshold_map = MedicalHashMap()  # Disease thresholds (C++ HashMap)
        self.symptom_graph = SymptomDiseaseGraph()  # Symptom-disease relationships (C++ Graph)
        self.priority_heap = MedicalPriorityQueue(max_heap=True)  # Disease ranking (C++ PriorityQueue)
        
        # Load thresholds from database
        self._load_thresholds()
        # Load percentile thresholds from datasets (75/90/95)
        self.percentile_map = {}
        self._load_percentile_thresholds()
        
        # Load symptom-disease relationships
        self._load_symptom_disease_network()
        
        # Load trained C++ decision tree models
        self.models = {}
        self._load_cpp_models()
    
    def _load_thresholds(self):
        """Load disease thresholds from database into HashMap."""
        thresholds = DiseaseThresholdDAO.get_all_thresholds()
        
        for threshold in thresholds:
            # Use disease_code if available so keys match the internal disease_type codes
            disease_code = threshold.get('disease_code') or threshold.get('disease_name')
            param_name = threshold['parameter_name']
            key = f"{disease_code}:{param_name}"
            
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
    
    def _auto_train_model(self, disease_type, datasets_dir, output_path):
        """Auto-train a C++ decision tree model if it doesn't exist."""
        dataset_path = os.path.join(datasets_dir, f"{disease_type}.csv")
        
        if not os.path.exists(dataset_path):
            raise FileNotFoundError(f"Dataset not found: {dataset_path}")
        
        print(f"Training {disease_type} model from {dataset_path}...")
        
        # Import training logic
        from utils.mapping import get_disease_config
        config = get_disease_config(disease_type)
        if not config:
            raise ValueError(f"Unknown disease type: {disease_type}")
        
        # Load dataset
        data_points = []
        with open(dataset_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                try:
                    features = []
                    for col in config['columns']:
                        value = row.get(col, '0').strip()
                        if value == '':
                            value = '0'
                        features.append(float(value))
                    
                    target_col = config['target_column']
                    label_value = row.get(target_col, '0').strip()
                    
                    if 'target_mapping' in config:
                        if label_value in config['target_mapping']:
                            label = config['target_mapping'][label_value]
                        else:
                            continue
                    else:
                        label = int(label_value)
                    
                    dp = cpp_tree.DataPoint(features, label)
                    data_points.append(dp)
                except (ValueError, KeyError) as e:
                    continue
        
        print(f"Loaded {len(data_points)} samples")
        
        # Train model with optimized parameters for better accuracy
        tree = cpp_tree.DecisionTree()
        # Increase max_depth for better feature learning
        # Adjust min_samples_split to avoid overfitting
        max_depth = 15 if disease_type == 'diabetes' else 12
        min_samples = 5 if disease_type == 'heart' else 4
        tree.train(data_points, max_depth=max_depth, min_samples_split=min_samples, criterion='entropy')
        
        # Save model
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        tree.save(output_path)
        print(f"Model trained and saved to {output_path}")
    
    def _load_cpp_models(self):
        """Load trained C++ decision tree models for each disease. Auto-train if missing."""
        models_dir = os.path.join(os.path.dirname(__file__), '..', 'models')
        datasets_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'datasets')
        disease_types = ['diabetes', 'heart', 'breast_cancer']
        
        for disease_type in disease_types:
            model_path = os.path.join(models_dir, f"{disease_type}_model.txt")
            
            # If model doesn't exist, train it automatically
            if not os.path.exists(model_path):
                print(f"Model not found for {disease_type}, training automatically...")
                self._auto_train_model(disease_type, datasets_dir, model_path)
            
            # Load the model
            model = cpp_tree.DecisionTree()
            if not model.load(model_path):
                raise RuntimeError(f"Failed to load C++ model for {disease_type} from {model_path}")
            
            self.models[disease_type] = model
            print(f"Loaded C++ DecisionTree model for {disease_type}")

    def _compute_percentiles(self, values, percents=(75, 90, 95)):
        """Compute percentiles without external dependencies. Returns dict of percent->value."""
        out = {}
        try:
            vals = [v for v in values if v is not None]
            if not vals:
                return {p: None for p in percents}
            vals_sorted = sorted(vals)
            n = len(vals_sorted)
            for p in percents:
                # position using linear interpolation between nearest ranks
                if n == 1:
                    out[p] = vals_sorted[0]
                    continue
                rank = (p/100.0) * (n - 1)
                lo = int(rank)
                hi = min(lo + 1, n - 1)
                frac = rank - lo
                out[p] = vals_sorted[lo] * (1 - frac) + vals_sorted[hi] * frac
            return out
        except Exception:
            return {p: None for p in percents}

    def _load_percentile_thresholds(self):
        """Load percentiles (75/90/95) per numeric field from CSV datasets for each disease."""
        try:
            base = os.path.normpath(os.path.join(os.path.dirname(__file__), '..', '..', 'datasets'))
            diseases = ['diabetes', 'heart', 'breast_cancer']
            for disease in diseases:
                path = os.path.join(base, f"{disease}.csv")
                if not os.path.exists(path):
                    continue

                # Prepare collectors for fields based on disease config
                config = get_disease_config(disease)
                field_names = []
                if config and 'fields' in config:
                    field_names = [f['name'] for f in config['fields']]

                collectors = {name: [] for name in field_names}

                with open(path, 'r', encoding='utf-8') as fh:
                    reader = csv.DictReader(fh)
                    for row in reader:
                        # build a normalized header map for this row (keys are original headers)
                        header_map = {}
                        for h in row.keys():
                            if h is None:
                                continue
                            norm = str(h).lower().replace(' ', '').replace('_', '').replace('"', '')
                            header_map[norm] = h

                        for name in field_names:
                            norm_name = name.lower().replace(' ', '').replace('_', '')
                            matched_key = None
                            if norm_name in header_map:
                                matched_key = header_map[norm_name]
                            else:
                                # try name variants
                                if name in row:
                                    matched_key = name
                                elif name.title() in row:
                                    matched_key = name.title()
                                else:
                                    # try replacing underscores with spaces
                                    alt = name.replace('_', ' ')
                                    if alt in row:
                                        matched_key = alt

                            if matched_key:
                                val = row.get(matched_key)
                            else:
                                val = None

                            try:
                                if val is not None and val != '':
                                    num = float(val)
                                    collectors[name].append(num)
                            except Exception:
                                pass

                # Compute percentiles per field
                pct_map = {}
                for name, vals in collectors.items():
                    p = self._compute_percentiles(vals, percents=(75, 90, 95))
                    pct_map[name] = {'p75': p.get(75), 'p90': p.get(90), 'p95': p.get(95)}

                self.percentile_map[disease] = pct_map
        except Exception as e:
            # non-fatal; percentile_map stays empty
            print(f"Warning loading percentiles: {e}")
    
    def analyze_with_dsa(self, test_data, symptoms, disease_type):
        """
        Analyze using DSA structures (primary method).
        Returns: (result, confidence, method_used)
        """
        # Convert test data to a list of param/value dicts
        test_array = [{'param': k, 'value': v} for k, v in test_data.items()]

        # Check thresholds using HashMap
        threshold_violations = []
        risk_score = 0

        for test in test_array:
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
                        'normal_range': f"{min_val}-{max_val} {threshold.get('unit', '')}".strip()
                    })
                    risk_score += 8  # balanced weight for threshold violations
        
        # Check symptom correlations using graph
        symptom_matches = 0
        symptom_set = MedicalSet()
        for symptom in symptoms:
            symptom_set.add(symptom.lower().replace(' ', '_'))
        
        for symptom in symptom_set.to_vector():
            diseases = self.symptom_graph.get_diseases_for_symptom(symptom)
            if disease_type in diseases:
                symptom_matches += 1
                risk_score += 3  # Reduced from 5 to 3
        
        # Apply decision tree rules - MODEL IS PRIMARY DECISION MAKER
        decision = self._apply_decision_tree(test_data, disease_type)
        model_prediction = 0
        model_confidence = 0.85
        
        if decision:
            # Decision tree is the main predictor
            boost = decision.get('risk_boost', 0)
            model_confidence = decision.get('confidence', 0.85)
            # Use adaptive threshold based on disease type
            thresholds = {'diabetes': 35, 'heart': 40, 'breast_cancer': 38}
            threshold = thresholds.get(disease_type, 35)
            model_prediction = 1 if boost >= threshold else 0
            risk_score += boost
        
        # Apply clinical rules for fine-tuning (complement the model, don't override)
        severity_label, severity_reason, adjusted_score = self._apply_clinical_rules(
            disease_type, test_data, threshold_violations, symptom_matches, risk_score, model_prediction
        )

        # Map to prediction + confidence (balanced approach)
        # Final decision: model prediction + clinical validation
        result = model_prediction
        
        # If clinical score strongly disagrees with model, adjust result
        if model_prediction == 1 and adjusted_score < 30:
            result = 0  # Clinical evidence too weak despite model
        elif model_prediction == 0 and adjusted_score >= 75:
            result = 1  # Clinical evidence very strong despite model
        
        # Calculate confidence based on agreement between model and clinical
        confidence = 0
        agreement = (adjusted_score >= 50) == (result == 1)
        
        if result == 1:  # High Risk prediction
            base_conf = int(model_confidence * 100)
            if agreement and adjusted_score >= 70:
                confidence = min(95, base_conf + 5)
            elif agreement:
                confidence = min(88, base_conf)
            else:
                confidence = max(65, base_conf - 10)
        else:  # Low Risk prediction  
            base_conf = int(model_confidence * 100)
            if agreement and adjusted_score <= 30:
                confidence = min(92, base_conf + 5)
            elif agreement:
                confidence = min(85, base_conf)
            else:
                confidence = max(65, base_conf - 10)

        return {
            'prediction': result,
            'confidence': confidence,
            # Expose adjusted score as the main risk_score so callers use the combined logic
            'risk_score': int(adjusted_score),
            'adjusted_score': int(adjusted_score),
            'severity_label': severity_label,
            'severity_reason': severity_reason,
            'threshold_violations': threshold_violations,
            'symptom_matches': symptom_matches,
            'method': 'Machine Learning',
            'decision_rules_applied': decision is not None
        }

    def _apply_clinical_rules(self, disease_type, test_data, threshold_violations, symptom_matches, risk_score, model_prediction):
        """
        Apply disease-specific clinical heuristics for fine-tuning.
        Model prediction is the primary decision maker.

        Returns: (severity_label, reason, adjusted_score)
        """
        # Start with base adjusted score = risk_score
        adjusted = float(risk_score)
        reasons = []
        strong_flags = 0

        if disease_type == 'diabetes':
            # Common clinical cutoffs (fasting glucose mg/dL):
            # Normal <100, Prediabetes 100-125, Diabetes >=126
            glucose = None
            if 'glucose' in test_data:
                try:
                    glucose = float(test_data.get('glucose') or 0)
                except Exception:
                    glucose = None

            bmi = None
            if 'bmi' in test_data:
                try:
                    bmi = float(test_data.get('bmi') or 0)
                except Exception:
                    bmi = None

            if glucose is not None:
                # Clinical cutoffs: Normal <100, Prediabetes 100-125, Diabetes >=126
                if glucose >= 126:
                    adjusted += 12  # Strong clinical indicator
                    strong_flags += 1
                    reasons.append(f'glucose >=126 mg/dL (diabetic range: {glucose:.1f})')
                elif glucose >= 100:
                    adjusted += 6  # Moderate indicator
                    reasons.append(f'glucose {glucose:.1f} mg/dL (prediabetic range)')
                elif glucose < 70:
                    adjusted += 3  # Hypoglycemia can indicate issues
                    reasons.append(f'low glucose {glucose:.1f} mg/dL')

            if bmi is not None:
                # Clinical BMI categories: Normal 18.5-24.9, Overweight 25-29.9, Obese >=30
                if bmi >= 35:
                    adjusted += 8  # Class 2+ obesity
                    strong_flags += 1
                    reasons.append(f'BMI {bmi:.1f} (severe obesity)')
                elif bmi >= 30:
                    adjusted += 5  # Class 1 obesity
                    reasons.append(f'BMI {bmi:.1f} (obese)')
                elif bmi >= 25:
                    adjusted += 2  # Overweight
                    reasons.append(f'BMI {bmi:.1f} (overweight)')

        elif disease_type == 'heart':
            # Clinical heart disease risk factors
            age = float(test_data.get('age') or 0)
            chol = float(test_data.get('chol') or 0)
            sbp = float(test_data.get('trestbps') or test_data.get('systolic_bp') or 0)
            thalach = float(test_data.get('thalach') or 0)  # Max heart rate
            oldpeak = float(test_data.get('oldpeak') or 0)  # ST depression

            # Age risk (Framingham criteria)
            if age >= 65:
                adjusted += 6
                reasons.append(f'age {age} (high risk)')
            elif age >= 55:
                adjusted += 3
                reasons.append(f'age {age} (moderate risk)')
            
            # Cholesterol (ACC/AHA guidelines: Desirable <200, Borderline 200-239, High >=240)
            if chol >= 240:
                adjusted += 8
                strong_flags += 1
                reasons.append(f'cholesterol {chol} mg/dL (high)')
            elif chol >= 200:
                adjusted += 4
                reasons.append(f'cholesterol {chol} mg/dL (borderline high)')
            
            # Blood pressure (Hypertension: Stage 1 >=130/80, Stage 2 >=140/90)
            if sbp >= 140:
                adjusted += 7
                strong_flags += 1
                reasons.append(f'blood pressure {sbp} mmHg (hypertensive)')
            elif sbp >= 130:
                adjusted += 4
                reasons.append(f'blood pressure {sbp} mmHg (elevated)')
            
            # Maximum heart rate (220-age is predicted max)
            if thalach > 0:
                predicted_max = 220 - age
                if thalach < predicted_max * 0.6:  # Poor exercise capacity
                    adjusted += 5
                    reasons.append(f'low max heart rate {thalach} bpm')
            
            # ST depression (oldpeak) - strong indicator
            if oldpeak >= 2.0:
                adjusted += 10
                strong_flags += 1
                reasons.append(f'ST depression {oldpeak} (significant ischemia)')
            elif oldpeak >= 1.0:
                adjusted += 5
                reasons.append(f'ST depression {oldpeak} (mild ischemia)')

        elif disease_type == 'breast_cancer':
            # Clinical features for breast cancer (WDBC dataset analysis)
            def getf(name):
                try:
                    return float(test_data.get(name) or 0)
                except Exception:
                    return 0.0

            radius = getf('radius_mean')
            texture = getf('texture_mean')
            perimeter = getf('perimeter_mean')
            area = getf('area_mean')
            concavity = getf('concavity_mean')
            concave_pts = getf('concave_points_mean')

            # Based on WDBC research: Malignant tumors typically have:
            # - Larger size (radius > 17, perimeter > 110)
            # - Higher concavity and concave points
            # - More irregular texture
            
            # Size indicators (strong predictors)
            if radius > 17 or perimeter > 115:
                adjusted += 12
                strong_flags += 1
                reasons.append(f'large tumor size (radius={radius:.1f}mm, perimeter={perimeter:.1f}mm)')
            elif radius > 14 or perimeter > 95:
                adjusted += 6
                reasons.append(f'moderate tumor size (radius={radius:.1f}mm)')
            
            # Concavity features (malignant tumors are more concave)
            if concavity > 0.15 or concave_pts > 0.08:
                adjusted += 10
                strong_flags += 1
                reasons.append(f'high concavity (concavity={concavity:.3f}, points={concave_pts:.3f})')
            elif concavity > 0.08 or concave_pts > 0.04:
                adjusted += 5
                reasons.append(f'moderate concavity features')
            
            # Texture irregularity
            if texture > 25:
                adjusted += 6
                reasons.append(f'irregular texture ({texture:.1f})')
            elif texture > 20:
                adjusted += 3
                reasons.append(f'moderately irregular texture ({texture:.1f})')
            
            # Area (correlated with radius but useful)
            if area > 900:
                adjusted += 4
                reasons.append(f'large tumor area ({area:.0f} mm²)')

        # Combination logic: multiple risk factors
        if len(threshold_violations) >= 3:
            adjusted += 8
            strong_flags += 1
            reasons.append(f'{len(threshold_violations)} parameter violations')
        elif len(threshold_violations) >= 2:
            adjusted += 4
            reasons.append(f'{len(threshold_violations)} parameter violations')

        if symptom_matches >= 3:
            adjusted += 6
            reasons.append(f'{symptom_matches} symptoms match disease profile')
        elif symptom_matches >= 2:
            adjusted += 3
            reasons.append(f'{symptom_matches} symptoms match disease profile')
        
        # Apply percentile-based flags for outlier detection
        # This helps identify extreme values beyond clinical thresholds
        pct_map = self.percentile_map.get(disease_type, {})
        percentile_count = 0
        
        for param, raw_val in test_data.items():
            try:
                val = float(raw_val)
            except Exception:
                continue

            field_pct = pct_map.get(param)
            if not field_pct:
                continue

            p95 = field_pct.get('p95')
            p90 = field_pct.get('p90')

            # Only use extreme percentiles (95th) for strong outliers
            if p95 is not None and val >= p95:
                percentile_count += 1
                if percentile_count <= 2:  # Don't double-count too much
                    adjusted += 5
                    reasons.append(f'{param}={val:.1f} (>95th percentile)')

        # If rules fail, keep adjusted as risk_score (no outer try/except)

        # Normalize adjusted score to 0-100
        adjusted_score = max(0.0, min(100.0, adjusted))
        
        # Additional cap: if no threshold violations and no symptoms, cap at 75%
        if len(threshold_violations) == 0 and symptom_matches == 0:
            adjusted_score = min(75.0, adjusted_score)

        # Map to label (conservative: require multiple strong flags for High)
        if adjusted_score >= 60:
            if strong_flags >= 2:
                label = 'High'
        # Normalize adjusted score to 0-100
        adjusted_score = max(0.0, min(100.0, adjusted))

        # Map to label based on MODEL PREDICTION (trust the model)
        if model_prediction == 1:
            # Model says High Risk - respect it
            if adjusted_score >= 70 or strong_flags >= 2:
                label = 'High'
            elif adjusted_score >= 50:
                label = 'Moderate'
            else:
                label = 'Moderate'  # Model says risk, so at least Moderate
        else:
            # Model says Low Risk
            if adjusted_score >= 60:
                label = 'Moderate'  # Clinical flags suggest caution
            else:
                label = 'Low'

        reason_text = '; '.join(reasons) if reasons else 'No specific clinical flags.'
        return label, reason_text, adjusted_score
    
    def _apply_decision_tree(self, test_data, disease_type):
        """Apply C++ trained decision tree model with calibrated risk scoring."""
        # Use the loaded C++ model if available
        if disease_type in self.models:
            try:
                # Get disease config to build features in correct order
                config = get_disease_config(disease_type)
                if config and 'fields' in config:
                    features = []
                    for field in config['fields']:
                        field_name = field['name']
                        value = test_data.get(field_name, field.get('default', 0))
                        try:
                            features.append(float(value))
                        except:
                            features.append(0.0)
                    
                    # Use C++ decision tree prediction
                    prediction = self.models[disease_type].predict(features)
                    
                    # Map prediction to risk boost - calibrated per disease
                    # prediction 0 = low risk, 1 = high risk
                    if prediction == 1:
                        # Calibrated risk boost based on dataset characteristics
                        # Diabetes: 35% positive rate -> moderate boost
                        # Heart: 55% positive rate -> higher boost  
                        # Breast Cancer: varies by features -> moderate boost
                        risk_boosts = {'diabetes': 40, 'heart': 45, 'breast_cancer': 42}
                        boost = risk_boosts.get(disease_type, 40)
                        return {'risk_boost': boost, 'rule': 'cpp_tree_high_risk', 'model': 'C++ DecisionTree', 'confidence': 0.85}
                    else:
                        return {'risk_boost': 5, 'rule': 'cpp_tree_low_risk', 'model': 'C++ DecisionTree', 'confidence': 0.85}
            except Exception as e:
                raise RuntimeError(f"Error applying C++ decision tree for {disease_type}: {e}")
        
        # Model must exist - no fallback
        raise RuntimeError(f"C++ model not loaded for {disease_type}")
    
    def predict(self, test_data, symptoms, disease_type):
        """
        Main prediction method using pure DSA analysis.
        No ML fallback - all predictions based on custom data structures.
        """
        # Use DSA analysis only
        dsa_result = self.analyze_with_dsa(test_data, symptoms, disease_type)
        
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
        except Exception as e:
            raise RuntimeError(f"Error building features list: {e}")

        # Attach a human-friendly remark based on disease-specific heuristics
        try:
            prediction_value = dsa_result.get('prediction', 0)
            # Ensure DSA metadata is present so templates can display severity info
            dsa_result['dsa_result'] = dsa_result

            # Try to generate a human-friendly remark. Prefer any existing remark,
            # otherwise fall back to DSA's severity_reason.
            if dsa_result.get('remark'):
                pass
            else:
                # If the only available text is a technical severity_reason (parameter names/values),
                # prefer a short human-friendly remark and keep the technical details in severity_reason.
                sr = dsa_result.get('severity_reason')
                if sr:
                    # detect technical pattern like operators or parameter names
                    if any(tok in sr for tok in ['>=', '<=', ' pct', 'pct', '=', 'parameter', 'radius', 'glucose', 'bmi', 'chol', 'bp']):
                        dsa_result['remark'] = 'Clinical flags detected. See details for specifics.'
                    else:
                        dsa_result['remark'] = sr
                else:
                    dsa_result['remark'] = 'Based on the analysis of provided health metrics.'
        except Exception:
            dsa_result['remark'] = 'Based on the analysis of provided health metrics.'

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
        
        # Rank by risk using C++ PriorityQueue (wrapper)
        ranked_results = []
        heap = MedicalPriorityQueue(max_heap=True)
        
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
        # Convert to format expected by C++ sorter
        score_pairs = [(disease, float(score)) for disease, score in disease_scores]
        
        # Use C++ QuickSort for performance
        sorted_scores = MedicalSorting.quick_sort_by_score(score_pairs, descending=True)
        
        return sorted_scores
    
    def calculate_composite_risk(self, disease_scores, symptom_weight=0.4, 
                                frequency_weight=0.3, comorbidity_weight=0.2, 
                                age_factor_weight=0.1):
        """
        Calculate composite risk score using C++ RiskScorer.
        Applies multiple factors to rank diseases more accurately.
        """
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
            raise RuntimeError(f"Error in composite risk calculation: {e}")
    
    def extract_symptoms_from_db(self):
        """
        Extract all symptoms from database and load into C++ SymptomManager.
        Used for fast symptom lookup and autocomplete.
        """
        
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
        sym_manager = self.extract_symptoms_from_db()
        if sym_manager:
            results = sym_manager.search_by_prefix(prefix)
            return results
        return []

