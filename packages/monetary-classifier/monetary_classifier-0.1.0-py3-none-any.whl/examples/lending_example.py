"""
Example script demonstrating the MonetaryClassifier on a lending scenario.
"""
from sklearn.datasets import make_classification
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from monetary_classifier import MonetaryClassifier, create_lending_monetary_values

# Generate example data (1 = loan repaid, 0 = loan defaulted)
X, y = make_classification(n_samples=1000, n_features=10, random_state=42)

# Generate random loan amounts between $5,000 and $50,000
loan_amounts = np.random.uniform(5000, 50000, size=len(y))

# Split the data
X_train, X_test, y_train, y_test, loan_train, loan_test = train_test_split(
    X, y, loan_amounts, test_size=0.2, random_state=42
)

# Create a base classifier (any scikit-learn classifier will work)
base_clf = RandomForestClassifier(random_state=42)

# Calculate average loan amount
avg_loan = np.mean(loan_train)
monetary_values = create_lending_monetary_values(
    loan_amount=avg_loan,
    interest_rate=0.10,  # 10% interest
    default_cost_factor=1.0  # Full loss of principal
)

print("Monetary values for lending scenario:")
print(f"True Positive (correctly approve good loan): ${monetary_values['tp']:.2f}")
print(f"True Negative (correctly deny bad loan): ${monetary_values['tn']:.2f}")
print(f"False Positive (wrongly approve bad loan): ${monetary_values['fp']:.2f}")
print(f"False Negative (wrongly deny good loan): ${monetary_values['fn']:.2f}")

# Create and fit monetary classifier
monetary_clf = MonetaryClassifier(base_clf, monetary_values)
monetary_clf.fit(X_train, y_train)

# Evaluate on test set
monetary_score = monetary_clf.monetary_score(X_test, y_test)
print(f"\nMonetary outcome: ${monetary_score:.2f}")

# Get detailed monetary summary
summary = monetary_clf.get_monetary_summary(X_test, y_test)
print("\nDetailed monetary summary:")
for key, value in summary.items():
    if isinstance(value, dict):
        print(f"{key}: {value['count']} instances, ${value['value']:.2f}")
    else:
        print(f"{key}: ${value:.2f}")

# Show the optimal threshold
print(f"\nOptimal threshold found: {monetary_clf.threshold_:.4f}")

# Compare with standard classifier (0.5 threshold)
standard_clf = RandomForestClassifier(random_state=42)
standard_clf.fit(X_train, y_train)
y_pred_standard = standard_clf.predict(X_test)

# Create a function to calculate monetary outcome with any classifier
def calculate_monetary_outcome(y_true, y_pred, monetary_values):
    y_true, y_pred = np.asarray(y_true), np.asarray(y_pred)
    tp = np.sum((y_true == 1) & (y_pred == 1))
    tn = np.sum((y_true == 0) & (y_pred == 0))
    fp = np.sum((y_true == 0) & (y_pred == 1))
    fn = np.sum((y_true == 1) & (y_pred == 0))
    
    return (
        tp * monetary_values['tp'] +
        tn * monetary_values['tn'] +
        fp * monetary_values['fp'] +
        fn * monetary_values['fn']
    )

standard_monetary_outcome = calculate_monetary_outcome(
    y_test, y_pred_standard, monetary_values
)

print(f"\nStandard classifier monetary outcome: ${standard_monetary_outcome:.2f}")
print(f"Monetary classifier improvement: ${monetary_score - standard_monetary_outcome:.2f}")

if __name__ == "__main__":
    plt.figure(figsize=(10, 6))
    
    # Get probabilities from the base classifier
    probas = monetary_clf.base_estimator.predict_proba(X_test)[:, 1]
    
    # Try different thresholds
    thresholds = np.linspace(0, 1, 100)
    monetary_outcomes = []
    for threshold in thresholds:
        y_pred = (probas >= threshold).astype(int)
        outcome = calculate_monetary_outcome(y_test, y_pred, monetary_values)
        monetary_outcomes.append(outcome)
    
    # Plot monetary outcome vs threshold
    plt.plot(thresholds, monetary_outcomes, 'b-')
    plt.axvline(x=0.5, color='r', linestyle='--', label='Standard threshold (0.5)')
    plt.axvline(x=monetary_clf.threshold_, color='g', linestyle='--', 
                label=f'Optimal threshold ({monetary_clf.threshold_:.2f})')
    plt.xlabel('Classification Threshold')
    plt.ylabel('Monetary Outcome ($)')
    plt.title('Monetary Outcome vs Classification Threshold')
    plt.grid(True, alpha=0.3)
    plt.legend()
    plt.tight_layout()
    plt.show()
