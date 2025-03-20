"""
Tests for the MonetaryClassifier package.
"""
import numpy as np
from sklearn.datasets import make_classification
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from monetary_classifier import (
    MonetaryClassificationScorer,
    MonetaryClassifier,
    create_lending_monetary_values
)

def test_monetary_scorer():
    """Test the monetary scorer."""
    y_true = np.array([1, 1, 1, 0, 0, 0])
    y_pred = np.array([1, 1, 0, 0, 0, 1])
    
    # TP: 2, TN: 2, FP: 1, FN: 1
    monetary_values = {'tp': 10, 'tn': 5, 'fp': -20, 'fn': -5}
    scorer = MonetaryClassificationScorer(monetary_values)
    
    expected_score = 2*10 + 2*5 + 1*(-20) + 1*(-5)
    actual_score = scorer(y_true, y_pred)
    
    assert actual_score == expected_score, f"Expected {expected_score}, got {actual_score}"

def test_monetary_classifier():
    """Test the monetary classifier."""
    # Generate simple dataset
    X, y = make_classification(n_samples=100, n_features=5, random_state=42)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # Create monetary values
    monetary_values = {'tp': 10, 'tn': 5, 'fp': -20, 'fn': -5}
    
    # Create classifier
    base_clf = RandomForestClassifier(n_estimators=10, random_state=42)
    monetary_clf = MonetaryClassifier(base_clf, monetary_values=monetary_values)
    
    # Fit and predict
    monetary_clf.fit(X_train, y_train)
    y_pred = monetary_clf.predict(X_test)
    
    # Check that threshold was set
    assert hasattr(monetary_clf, 'threshold_'), "Threshold not set"
    
    # Check monetary score
    score = monetary_clf.monetary_score(X_test, y_test)
    assert isinstance(score, (int, float)), "Score should be a number"

def test_lending_values():
    """Test the lending monetary values function."""
    loan_amount = 10000
    interest_rate = 0.1
    default_cost_factor = 0.8
    
    values = create_lending_monetary_values(
        loan_amount=loan_amount,
        interest_rate=interest_rate,
        default_cost_factor=default_cost_factor
    )
    
    assert values['tp'] == loan_amount * interest_rate
    assert values['tn'] == 0
    assert values['fp'] == -loan_amount * default_cost_factor
    assert values['fn'] == -loan_amount * interest_rate

if __name__ == "__main__":
    test_monetary_scorer()
    test_monetary_classifier()
    test_lending_values()
    print("All tests passed!")
