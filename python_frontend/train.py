"""
Training script for disease prediction models.
"""
import sys
import os
import csv
import pickle
import argparse

# Import the C++ module
try:
    import cpp_tree
except ImportError:
    print("Error: cpp_tree module not found. Please build the C++ module first.")
    print("Run: mkdir build && cd build && cmake .. && make")
    sys.exit(1)

from utils.mapping import get_disease_config


def load_dataset(filepath, disease_type):
    """Load and preprocess dataset."""
    config = get_disease_config(disease_type)
    if not config:
        raise ValueError(f"Unknown disease type: {disease_type}")
    
    data_points = []
    
    with open(filepath, 'r') as f:
        reader = csv.DictReader(f)
        
        for row in reader:
            try:
                # Extract features
                features = []
                for col in config['columns']:
                    value = row.get(col, '0').strip()
                    if value == '':
                        value = '0'
                    features.append(float(value))
                
                # Extract label
                target_col = config['target_column']
                label_value = row.get(target_col, '0').strip()
                
                # Handle special mappings (e.g., M/B for breast cancer)
                if 'target_mapping' in config:
                    if label_value in config['target_mapping']:
                        label = config['target_mapping'][label_value]
                    else:
                        raise ValueError(f"Unknown label '{label_value}' in column '{target_col}' for '{disease_type}'")
                else:
                    label = int(label_value)
                
                # Create DataPoint
                dp = cpp_tree.DataPoint(features, label)
                data_points.append(dp)
                
            except (ValueError, KeyError) as e:
                print(f"Warning: Skipping row due to error: {e}")
                continue
    
    print(f"Loaded {len(data_points)} samples")
    return data_points


def train_model(data_points, max_depth=10, min_samples_split=2, criterion='entropy'):
    """Train the decision tree model."""
    print(f"\nTraining model with:")
    print(f"  - Max depth: {max_depth}")
    print(f"  - Min samples split: {min_samples_split}")
    print(f"  - Criterion: {criterion}")
    
    tree = cpp_tree.DecisionTree()
    tree.train(data_points, max_depth, min_samples_split, criterion)
    
    print("Training complete!")
    return tree


def evaluate_model(tree, data_points):
    """Evaluate model accuracy on training data."""
    correct = 0
    total = len(data_points)
    
    for dp in data_points:
        prediction = tree.predict(dp.features)
        if prediction == dp.label:
            correct += 1
    
    accuracy = (correct / total) * 100
    print(f"\nTraining Accuracy: {accuracy:.2f}% ({correct}/{total})")
    return accuracy


def save_model(tree, output_path):
    """Save the trained model using C++ save() method."""
    tree.save(output_path)
    print(f"Model saved to: {output_path}")


def main():
    parser = argparse.ArgumentParser(description='Train disease prediction model')
    parser.add_argument('--disease', type=str, required=True,
                       choices=['diabetes', 'heart', 'breast_cancer'],
                       help='Disease type to train for')
    parser.add_argument('--dataset', type=str, required=True,
                       help='Path to dataset CSV file')
    parser.add_argument('--max-depth', type=int, default=10,
                       help='Maximum depth of decision tree')
    parser.add_argument('--min-samples', type=int, default=2,
                       help='Minimum samples required to split')
    parser.add_argument('--criterion', type=str, default='entropy',
                       choices=['entropy', 'gini'],
                       help='Impurity criterion')
    parser.add_argument('--output', type=str, default=None,
                       help='Output path for trained model')
    
    args = parser.parse_args()
    
    # Set default output path
    if args.output is None:
        args.output = f'models/{args.disease}_model.txt'
    
    # Create models directory if it doesn't exist
    os.makedirs('models', exist_ok=True)
    
    print(f"{'='*60}")
    print(f"Training {args.disease.upper()} Prediction Model")
    print(f"{'='*60}")
    
    # Load dataset
    print(f"\nLoading dataset from: {args.dataset}")
    data_points = load_dataset(args.dataset, args.disease)
    
    if not data_points:
        print("Error: No data points loaded!")
        return
    
    # Train model
    tree = train_model(data_points, args.max_depth, args.min_samples, args.criterion)
    
    # Evaluate model
    evaluate_model(tree, data_points)
    
    # Save model
    save_model(tree, args.output)
    
    print(f"\n{'='*60}")
    print("Training complete!")
    print(f"{'='*60}")


if __name__ == '__main__':
    main()