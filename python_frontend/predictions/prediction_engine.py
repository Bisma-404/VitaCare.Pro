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

# Import C++ DSA module only (no ML)
try:
    import cpp_tree
    from cpp_tree import MedicalSorting, RiskScorer, RiskFactors, SymptomManager
    CPP_AVAILABLE = True
except ImportError:
    print("Warning: cpp_tree module not fully available.")
    cpp_tree = None
    CPP_AVAILABLE = False


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
                    risk_score += 15  # reduced weight to make thresholds less sensitive
        
        # Check symptom correlations using graph
        symptom_matches = 0
        symptom_set = MedicalSet()
        for symptom in symptoms:
            symptom_set.add(symptom.lower().replace(' ', '_'))
        
        for symptom in symptom_set.to_vector():
            diseases = self.symptom_graph.get_diseases_for_symptom(symptom)
            if disease_type in diseases:
                symptom_matches += 1
                risk_score += 10  # reduced weight for symptom matches
        
        # Apply decision tree rules
        decision = self._apply_decision_tree(test_data, disease_type)
        if decision:
            # apply a slightly reduced decision boost to lower sensitivity
            risk_score += max(0, decision.get('risk_boost', 0) - 5)
        
        # Apply clinical / heuristic rules to adjust severity
        severity_label, severity_reason, adjusted_score = self._apply_clinical_rules(
            disease_type, test_data, threshold_violations, symptom_matches, risk_score
        )

        # Map adjusted score to prediction + confidence
        result = 0  # Low risk by default
        confidence = 0

        if adjusted_score >= 60 or severity_label == 'High':
            result = 1
            confidence = min(95, int(adjusted_score) + 5)
        elif adjusted_score >= 40 or severity_label == 'Moderate':
            result = 1
            confidence = max(50, int(adjusted_score) + 5)
        else:
            result = 0
            confidence = max(10, 100 - int(adjusted_score))

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
            'method': 'DSA',
            'decision_rules_applied': decision is not None
        }

    def _apply_clinical_rules(self, disease_type, test_data, threshold_violations, symptom_matches, risk_score):
        """
        Apply disease-specific clinical heuristics (based on widely used cutoffs)
        and a small percentile/combination logic to determine a severity label.

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
                if glucose >= 126:
                    adjusted += 25
                    strong_flags += 1
                    reasons.append(f'glucose >=126 ({glucose})')
                elif 100 <= glucose < 126:
                    adjusted += 12
                    reasons.append(f'prediabetes-range glucose {glucose}')

            if bmi is not None:
                if bmi >= 35:
                    adjusted += 10
                    strong_flags += 1
                    reasons.append(f'bmi >=35 ({bmi})')
                elif bmi >= 30:
                    adjusted += 6
                    reasons.append(f'bmi >=30 ({bmi})')

        elif disease_type == 'heart':
            # Simple heart risk heuristics
            age = float(test_data.get('age') or 0)
            chol = float(test_data.get('chol') or 0)
            sbp = float(test_data.get('trestbps') or test_data.get('systolic_bp') or 0)

            if age >= 65 and chol > 240 and sbp > 140:
                # more conservative: smaller bump for heart triple-risk
                adjusted += 15
                strong_flags += 1
                reasons.append(f'age+chol+bp high (age {age}, chol {chol}, bp {sbp})')
            elif chol > 240 or sbp > 140:
                adjusted += 8
                reasons.append(f'high chol or high BP (chol {chol}, bp {sbp})')
            elif age >= 60:
                adjusted += 6
                reasons.append(f'age >=60 ({age})')

        elif disease_type == 'breast_cancer':
            # Heuristics for breast cancer features (WDBC dataset fields)
            # Use radius_mean, texture_mean, perimeter_mean as indicators
            def getf(name):
                try:
                    return float(test_data.get(name) or 0)
                except Exception:
                    return 0.0

            radius = getf('radius_mean')
            texture = getf('texture_mean')
            perimeter = getf('perimeter_mean')

            # Common heuristic: radius_mean > 15 associated with malignant larger masses
            if radius > 15 or perimeter > 100:
                adjusted += 30
                strong_flags += 1
                reasons.append(f'large radius/perimeter (r={radius}, p={perimeter})')
            elif texture > 25:
                adjusted += 12
                reasons.append(f'high texture ({texture})')

        # Simple combination logic: increase severity if multiple violations/symptoms
        if len(threshold_violations) >= 2:
            adjusted += 12
            reasons.append(f'{len(threshold_violations)} threshold violations')

        if symptom_matches >= 2:
            adjusted += 6
            reasons.append(f'{symptom_matches} symptom matches')
        # Apply percentile-based flags (dataset-driven) if available
        pct_map = self.percentile_map.get(disease_type, {})
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
            p75 = field_pct.get('p75')

            # apply slightly smaller percentile bumps for heart to reduce sensitivity
            if disease_type == 'heart':
                if p95 is not None and val >= p95:
                    adjusted += 12
                    strong_flags += 1
                    reasons.append(f'{param} >= 95th pct ({val} >= {round(p95,2)})')
                elif p90 is not None and val >= p90:
                    adjusted += 8
                    reasons.append(f'{param} >= 90th pct ({val} >= {round(p90,2)})')
                elif p75 is not None and val >= p75:
                    adjusted += 3
                    reasons.append(f'{param} >= 75th pct ({val} >= {round(p75,2)})')
            else:
                if p95 is not None and val >= p95:
                    adjusted += 20
                    strong_flags += 1
                    reasons.append(f'{param} >= 95th pct ({val} >= {round(p95,2)})')
                elif p90 is not None and val >= p90:
                    adjusted += 12
                    reasons.append(f'{param} >= 90th pct ({val} >= {round(p90,2)})')
                elif p75 is not None and val >= p75:
                    adjusted += 4
                    reasons.append(f'{param} >= 75th pct ({val} >= {round(p75,2)})')

        # If rules fail, keep adjusted as risk_score (no outer try/except)

        # Normalize adjusted score to 0-100
        adjusted_score = max(0.0, min(100.0, adjusted))

        # Map to label (conservative: require multiple strong flags for High)
        if adjusted_score >= 60:
            if strong_flags >= 2:
                label = 'High'
            else:
                label = 'Moderate'
        elif adjusted_score >= 40:
            label = 'Moderate'
        else:
            label = 'Low'

        reason_text = '; '.join(reasons) if reasons else 'No specific clinical flags.'
        return label, reason_text, adjusted_score
    
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
            else:
                # Fallback: use values from test_data
                features = list(test_data.values())
        except Exception:
            features = list(test_data.values())

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

