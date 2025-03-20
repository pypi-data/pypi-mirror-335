# Monetary Classifier

A scikit-learn compatible package for classification with monetary outcomes. This package allows you to optimize classifiers based on the actual monetary value of correct and incorrect predictions rather than just accuracy or other traditional metrics.

## Installation

```bash
# Basic installation
pip install monetary-classifier

# With gradient boosting integrations
pip install monetary-classifier[xgboost,lightgbm,catboost]

# For development
pip install monetary-classifier[dev]
```

Or install directly from the repository:

```bash
git clone https://github.com/yourusername/monetary-classifier.git
cd monetary-classifier
pip install -e .
```

## Quick Start

```python
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from monetary_classifier import MonetaryClassifier, create_lending_monetary_values

# Prepare your data
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)

# Define monetary values for each prediction outcome
monetary_values = {
    'tp': 100,    # Profit from true positive (e.g., approving a good loan)
    'tn': 0,      # No gain/loss from true negative (e.g., denying a bad loan)
    'fp': -1000,  # Loss from false positive (e.g., approving a bad loan)
    'fn': -100,   # Loss from false negative (e.g., denying a good loan)
}

# Or use the built-in function for lending scenarios
monetary_values = create_lending_monetary_values(
    loan_amount=10000,
    interest_rate=0.15,
    default_cost_factor=1.0
)

# Create and train the monetary classifier
clf = MonetaryClassifier(
    base_estimator=RandomForestClassifier(),
    monetary_values=monetary_values,
    use_monetary_weights=True  # Use monetary values as weights during training
)
clf.fit(X_train, y_train)

# Evaluate the monetary outcome
monetary_score = clf.monetary_score(X_test, y_test)
print(f"Monetary outcome: ${monetary_score:.2f}")

# Get detailed breakdown
summary = clf.get_monetary_summary(X_test, y_test)
print(summary)
```

## Key Features

1. **Monetary value-based classification**: Optimize for business value rather than just accuracy
2. **Automatic threshold optimization**: Find the optimal decision threshold to maximize monetary outcome
3. **Cost-sensitive learning**: Use monetary values as weights during model training
4. **Direct objective optimization**: Custom loss functions for gradient boosting models (XGBoost, LightGBM, CatBoost)
5. **scikit-learn compatible**: Works with existing scikit-learn pipelines and models
6. **Comprehensive evaluation**: Detailed monetary analysis of model performance

## Examples

Check the `examples` directory for detailed usage examples:

- `lending_example.py`: Basic example for a lending scenario
- `weighted_model_example.py`: Advanced example with different weighting strategies

## License

This project is licensed under the MIT License - see the LICENSE file for details.
