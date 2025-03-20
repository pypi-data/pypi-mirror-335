"""
Example script demonstrating the MonetaryClassifier with monetary-weighted updates.
"""
from sklearn.datasets import make_classification
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.model_selection import train_test_split
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from monetary_classifier import (
    MonetaryClassifier,
    create_lending_monetary_values,
    optimize_monetary_classifier
)

# Try to import XGBoost for advanced example
try:
    import xgboost as xgb
    from monetary_classifier import MonetaryGradientBoostingClassifier
    HAS_XGB = True
except ImportError:
    HAS_XGB = False

# Generate example data (1 = loan repaid, 0 = loan defaulted)
X, y = make_classification(
    n_samples=1000,
    n_features=10,
    weights=[0.8, 0.2],  # Make it imbalanced: 80% repaid, 20% default
    random_state=42
)

# Generate loan amounts between $5,000 and $50,000, with higher amounts for better credit
credit_score = X[:, 0]  # Use first feature as proxy for credit score
normalized_score = (credit_score - credit_score.min()) / (credit_score.max() - credit_score.min())
loan_amounts = 5000 + 45000 * normalized_score

# Split the data
X_train, X_test, y_train, y_test, loan_train, loan_test = train_test_split(
    X, y, loan_amounts, test_size=0.2, random_state=42
)

# Calculate monetary values for lending
avg_loan = np.mean(loan_train)
monetary_values = create_lending_monetary_values(
    loan_amount=avg_loan,
    interest_rate=0.15,  # 15% interest
    default_cost_factor=1.0  # Full loss of principal on default
)

print("Monetary values for lending scenario:")
print(f"True Positive (correctly approve good loan): ${monetary_values['tp']:.2f}")
print(f"True Negative (correctly deny bad loan): ${monetary_values['tn']:.2f}")
print(f"False Positive (wrongly approve bad loan): ${monetary_values['fp']:.2f}")
print(f"False Negative (wrongly deny good loan): ${monetary_values['fn']:.2f}")

# Create different types of classifiers to compare performance

# 1. Standard classifier (no monetary optimization)
std_clf = RandomForestClassifier(n_estimators=100, random_state=42)
std_clf.fit(X_train, y_train)

# 2. Monetary classifier with optimized threshold only
threshold_clf = MonetaryClassifier(
    RandomForestClassifier(n_estimators=100, random_state=42),
    monetary_values=monetary_values,
    use_monetary_weights=False
)
threshold_clf.fit(X_train, y_train)

# 3. Monetary classifier with sample weights during training
weighted_clf = MonetaryClassifier(
    RandomForestClassifier(n_estimators=100, random_state=42),
    monetary_values=monetary_values,
    use_monetary_weights=True
)
weighted_clf.fit(X_train, y_train)

# 4. Gradient Boosting with monetary optimization
gb_clf = MonetaryClassifier(
    GradientBoostingClassifier(n_estimators=100, random_state=42),
    monetary_values=monetary_values,
    use_monetary_weights=True
)
gb_clf.fit(X_train, y_train)

# 5. XGBoost with monetary optimization (if available)
if HAS_XGB:
    xgb_clf = MonetaryGradientBoostingClassifier(
        xgb.XGBClassifier(n_estimators=100, random_state=42),
        monetary_values=monetary_values,
        use_monetary_weights=True,
        use_custom_objective=True
    )
    xgb_clf.fit(X_train, y_train)

# Compare model performance on test set
def evaluate_model(name, model, X, y):
    # Standard accuracy
    y_pred = model.predict(X)
    accuracy = np.mean(y_pred == y)
    
    # Calculate monetary outcome
    if hasattr(model, 'monetary_score'):
        monetary_outcome = model.monetary_score(X, y)
        monetary_summary = model.get_monetary_summary(X, y)
        
        # Extract values
        tp_count = monetary_summary['true_positives']['count']
        tn_count = monetary_summary['true_negatives']['count']
        fp_count = monetary_summary['false_positives']['count']
        fn_count = monetary_summary['false_negatives']['count']
        
        # Calculate values
        tp_value = monetary_summary['true_positives']['value']
        tn_value = monetary_summary['true_negatives']['value']
        fp_value = monetary_summary['false_positives']['value']
        fn_value = monetary_summary['false_negatives']['value']
        
        # Calculate threshold if available
        threshold = getattr(model, 'threshold_', 0.5)
    else:
        # For standard model, calculate monetary values manually
        tp = np.sum((y == 1) & (y_pred == 1))
        tn = np.sum((y == 0) & (y_pred == 0))
        fp = np.sum((y == 0) & (y_pred == 1))
        fn = np.sum((y == 1) & (y_pred == 0))
        
        tp_count, tn_count, fp_count, fn_count = tp, tn, fp, fn
        
        # Calculate monetary outcome
        tp_value = tp * monetary_values['tp']
        tn_value = tn * monetary_values['tn']
        fp_value = fp * monetary_values['fp']
        fn_value = fn * monetary_values['fn']
        monetary_outcome = tp_value + tn_value + fp_value + fn_value
        
        threshold = 0.5
    
    results = {
        'name': name,
        'accuracy': accuracy,
        'monetary_outcome': monetary_outcome,
        'tp_count': tp_count,
        'tn_count': tn_count,
        'fp_count': fp_count,
        'fn_count': fn_count,
        'tp_value': tp_value,
        'tn_value': tn_value,
        'fp_value': fp_value,
        'fn_value': fn_value,
        'threshold': threshold
    }
    
    return results

# Evaluate all models
results = []
results.append(evaluate_model("Standard RandomForest", std_clf, X_test, y_test))
results.append(evaluate_model("Monetary Threshold Only", threshold_clf, X_test, y_test))
results.append(evaluate_model("Monetary Weighted", weighted_clf, X_test, y_test))
results.append(evaluate_model("Gradient Boosting Monetary", gb_clf, X_test, y_test))
if HAS_XGB:
    results.append(evaluate_model("XGBoost Custom Objective", xgb_clf, X_test, y_test))

# Convert to DataFrame for better visualization
results_df = pd.DataFrame(results)

# Print results
print("\nModel Performance Comparison:")
print(results_df[['name', 'accuracy', 'monetary_outcome', 'threshold']].to_string(index=False))

print("\nConfusion Matrix Values:")
print(results_df[['name', 'tp_count', 'tn_count', 'fp_count', 'fn_count']].to_string(index=False))

print("\nMonetary Breakdown:")
print(results_df[['name', 'tp_value', 'tn_value', 'fp_value', 'fn_value']].to_string(index=False))

if __name__ == "__main__":
    # Plot monetary outcomes
    plt.figure(figsize=(12, 6))
    plt.bar(results_df['name'], results_df['monetary_outcome'])
    plt.title('Total Monetary Outcome by Model')
    plt.ylabel('Monetary Outcome ($)')
    plt.xticks(rotation=45, ha='right')
    plt.grid(axis='y', alpha=0.3)
    plt.tight_layout()
    
    # Plot breakdown of monetary components
    plt.figure(figsize=(14, 7))
    bar_width = 0.2
    index = np.arange(len(results_df))
    
    plt.bar(index - bar_width*1.5, results_df['tp_value'], bar_width, label='TP Value')
    plt.bar(index - bar_width*0.5, results_df['tn_value'], bar_width, label='TN Value')
    plt.bar(index + bar_width*0.5, results_df['fp_value'], bar_width, label='FP Value') 
    plt.bar(index + bar_width*1.5, results_df['fn_value'], bar_width, label='FN Value')
    
    plt.title('Breakdown of Monetary Components by Model')
    plt.ylabel('Monetary Value ($)')
    plt.xticks(index, results_df['name'], rotation=45, ha='right')
    plt.legend()
    plt.grid(axis='y', alpha=0.3)
    plt.tight_layout()
    plt.show()
