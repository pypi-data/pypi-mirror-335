import numpy as np
from sklearn.base import BaseEstimator, ClassifierMixin
from sklearn.utils.validation import check_X_y, check_array, check_is_fitted
from sklearn.metrics import make_scorer
from sklearn.model_selection import GridSearchCV
import warnings

class MonetaryClassificationScorer:
    """
    A scorer for classification problems with monetary outcomes.
    
    Parameters
    ----------
    monetary_values : dict
        Dictionary with keys 'tp', 'tn', 'fp', 'fn' representing monetary
        values for true positives, true negatives, false positives, and
        false negatives.
    """
    
    def __init__(self, monetary_values):
        self.monetary_values = monetary_values
    
    def __call__(self, y_true, y_pred):
        """
        Calculate the monetary score.
        
        Parameters
        ----------
        y_true : array-like of shape (n_samples,)
            True target values.
        y_pred : array-like of shape (n_samples,)
            Predicted target values.
            
        Returns
        -------
        score : float
            Monetary score.
        """
        # Convert to numpy arrays
        y_true = np.asarray(y_true)
        y_pred = np.asarray(y_pred)
        
        # Calculate confusion matrix entries
        tp = np.sum((y_true == 1) & (y_pred == 1))
        tn = np.sum((y_true == 0) & (y_pred == 0))
        fp = np.sum((y_true == 0) & (y_pred == 1))
        fn = np.sum((y_true == 1) & (y_pred == 0))
        
        # Calculate monetary outcome
        monetary_outcome = (
            tp * self.monetary_values['tp'] +
            tn * self.monetary_values['tn'] +
            fp * self.monetary_values['fp'] +
            fn * self.monetary_values['fn']
        )
        
        return monetary_outcome
    
    def individual_monetary_values(self, y_true, y_pred):
        """
        Calculate individual monetary values for each prediction.
        
        Parameters
        ----------
        y_true : array-like of shape (n_samples,)
            True target values.
        y_pred : array-like of shape (n_samples,)
            Predicted target values.
            
        Returns
        -------
        values : ndarray of shape (n_samples,)
            Monetary values for each sample.
        """
        # Convert to numpy arrays
        y_true = np.asarray(y_true)
        y_pred = np.asarray(y_pred)
        
        # Initialize values array
        values = np.zeros(len(y_true))
        
        # True positives
        mask = (y_true == 1) & (y_pred == 1)
        values[mask] = self.monetary_values['tp']
        
        # True negatives
        mask = (y_true == 0) & (y_pred == 0)
        values[mask] = self.monetary_values['tn']
        
        # False positives
        mask = (y_true == 0) & (y_pred == 1)
        values[mask] = self.monetary_values['fp']
        
        # False negatives
        mask = (y_true == 1) & (y_pred == 0)
        values[mask] = self.monetary_values['fn']
        
        return values

    def calculate_sample_weights(self, y):
        """
        Calculate sample weights based on monetary values.
        
        Parameters
        ----------
        y : array-like of shape (n_samples,)
            Target values.
            
        Returns
        -------
        weights : ndarray of shape (n_samples,)
            Sample weights.
        """
        # Convert to numpy array
        y = np.asarray(y)
        
        # Initialize weights array
        weights = np.ones(len(y))
        
        # Weight for positive samples: cost of misclassification (fn) relative to correct classification (tp)
        weights[y == 1] = abs(self.monetary_values['fn'] - self.monetary_values['tp'])
        
        # Weight for negative samples: cost of misclassification (fp) relative to correct classification (tn)
        weights[y == 0] = abs(self.monetary_values['fp'] - self.monetary_values['tn'])
        
        # Normalize weights
        if np.sum(weights) > 0:
            weights = weights / np.mean(weights)
        
        return weights

class MonetaryClassifier(BaseEstimator, ClassifierMixin):
    """
    A classifier that optimizes for monetary outcomes.
    
    Parameters
    ----------
    base_estimator : object
        The base estimator to wrap. Must implement fit, predict, and predict_proba methods.
    monetary_values : dict, default=None
        Dictionary with keys 'tp', 'tn', 'fp', 'fn' representing monetary
        values for true positives, true negatives, false positives, and
        false negatives. If None, these will be provided during fit.
    threshold : float or None, default=None
        Custom threshold for binary classification. If None, the optimal
        threshold is determined based on monetary values during fit.
    use_monetary_weights : bool, default=False
        Whether to use monetary values as sample weights during training.
    """
    
    def __init__(self, base_estimator, monetary_values=None, threshold=None, use_monetary_weights=False):
        self.base_estimator = base_estimator
        self.monetary_values = monetary_values
        self.threshold = threshold
        self.use_monetary_weights = use_monetary_weights
    
    def fit(self, X, y, dollar_values=None, sample_weight=None):
        """
        Fit the classifier with X, y and monetary values.
        
        Parameters
        ----------
        X : array-like of shape (n_samples, n_features)
            Training data.
        y : array-like of shape (n_samples,)
            Target values.
        dollar_values : dict or array-like, default=None
            If dict: Dictionary with keys 'tp', 'tn', 'fp', 'fn' representing monetary
            values for prediction outcomes.
            If array-like: Dollar values for each sample, to be used to calculate
            monetary values for prediction outcomes.
        sample_weight : array-like of shape (n_samples,), default=None
            Sample weights. If None, then samples are equally weighted.
        
        Returns
        -------
        self : object
            Returns self.
        """
        X, y = check_X_y(X, y)
        self.classes_ = np.unique(y)
        
        # Set or calculate monetary values
        if dollar_values is not None:
            if isinstance(dollar_values, dict):
                self.monetary_values_ = dollar_values
            else:
                # Calculate monetary values based on provided dollar values per sample
                self._calculate_monetary_values(y, dollar_values)
        elif self.monetary_values is not None:
            self.monetary_values_ = self.monetary_values
        else:
            # Default values (neutral)
            self.monetary_values_ = {'tp': 1, 'tn': 1, 'fp': -1, 'fn': -1}
        
        # Create the monetary scorer
        self.scorer_ = MonetaryClassificationScorer(self.monetary_values_)
        
        # Generate monetary-based sample weights if requested
        if self.use_monetary_weights:
            monetary_weights = self.scorer_.calculate_sample_weights(y)
            if sample_weight is not None:
                # Combine with provided sample weights
                combined_weights = sample_weight * monetary_weights
                combined_weights = combined_weights / np.mean(combined_weights)
                fit_sample_weight = combined_weights
            else:
                fit_sample_weight = monetary_weights
        else:
            fit_sample_weight = sample_weight
        
        # Fit the base estimator
        self.base_estimator.fit(X, y, sample_weight=fit_sample_weight)
        
        # Find optimal threshold if none provided
        if self.threshold is None and hasattr(self.base_estimator, 'predict_proba'):
            self._find_optimal_threshold(X, y)
        
        # Store training data stats for later use
        self.X_ = X
        self.y_ = y
        
        return self
    
    def _calculate_monetary_values(self, y, dollar_values):
        """
        Calculate monetary values based on dollar values per sample.
        
        Parameters
        ----------
        y : array-like of shape (n_samples,)
            Target values.
        dollar_values : array-like of shape (n_samples,)
            Dollar values for each sample.
        """
        # Convert to numpy arrays
        y = np.asarray(y)
        dollar_values = np.asarray(dollar_values)
        
        # Calculate average dollar values for positive and negative classes
        positive_dollars = np.mean(dollar_values[y == 1])
        negative_dollars = np.mean(dollar_values[y == 0])
        
        # Set monetary values
        self.monetary_values_ = {
            'tp': positive_dollars,  # Gain from correctly approving a good loan
            'tn': 0,  # No gain/loss from correctly denying a bad loan
            'fp': -negative_dollars,  # Loss from incorrectly approving a bad loan
            'fn': -positive_dollars * 0.1  # Loss of potential interest from incorrectly denying a good loan
        }
    
    def _find_optimal_threshold(self, X, y):
        """
        Find the optimal threshold that maximizes monetary outcome.
        
        Parameters
        ----------
        X : array-like of shape (n_samples, n_features)
            Training data.
        y : array-like of shape (n_samples,)
            Target values.
        """
        probas = self.base_estimator.predict_proba(X)[:, 1]
        
        # Try different thresholds
        thresholds = np.linspace(0, 1, 100)
        best_score = float('-inf')
        best_threshold = 0.5
        
        for threshold in thresholds:
            y_pred = (probas >= threshold).astype(int)
            score = self.scorer_(y, y_pred)
            
            if score > best_score:
                best_score = score
                best_threshold = threshold
        
        self.threshold_ = best_threshold
    
    def predict(self, X):
        """
        Predict class for X.
        
        Parameters
        ----------
        X : array-like of shape (n_samples, n_features)
            Samples.
            
        Returns
        -------
        y_pred : ndarray of shape (n_samples,)
            Predicted classes.
        """
        check_is_fitted(self)
        X = check_array(X)
        
        if hasattr(self, 'threshold_') and hasattr(self.base_estimator, 'predict_proba'):
            probas = self.base_estimator.predict_proba(X)[:, 1]
            return (probas >= self.threshold_).astype(int)
        else:
            return self.base_estimator.predict(X)
    
    def predict_proba(self, X):
        """
        Predict class probabilities for X.
        
        Parameters
        ----------
        X : array-like of shape (n_samples, n_features)
            Samples.
            
        Returns
        -------
        y_pred_proba : ndarray of shape (n_samples, n_classes)
            Predicted probabilities.
        """
        check_is_fitted(self)
        X = check_array(X)
        
        if hasattr(self.base_estimator, 'predict_proba'):
            return self.base_estimator.predict_proba(X)
        else:
            raise AttributeError("Base estimator does not have predict_proba method")
    
    def map_to_monetary_value(self, X, y_true=None):
        """
        Map classifications to monetary values.
        
        Parameters
        ----------
        X : array-like of shape (n_samples, n_features)
            Samples.
        y_true : array-like of shape (n_samples,), optional
            True target values. If provided, actual monetary outcomes are calculated.
            
        Returns
        -------
        values : ndarray of shape (n_samples,)
            Monetary values for each sample.
        """
        check_is_fitted(self)
        X = check_array(X)
        
        # Get predictions
        y_pred = self.predict(X)
        
        if y_true is not None:
            # Calculate actual monetary values
            values = self.scorer_.individual_monetary_values(y_true, y_pred)
        else:
            # Calculate expected monetary values based on probabilities
            if hasattr(self.base_estimator, 'predict_proba'):
                probas = self.predict_proba(X)[:, 1]
                
                # Calculate expected value for each prediction
                values = np.zeros(len(y_pred))
                
                # For predicted positives
                mask = (y_pred == 1)
                values[mask] = (
                    probas[mask] * self.monetary_values_['tp'] +
                    (1 - probas[mask]) * self.monetary_values_['fp']
                )
                
                # For predicted negatives
                mask = (y_pred == 0)
                values[mask] = (
                    probas[mask] * self.monetary_values_['fn'] +
                    (1 - probas[mask]) * self.monetary_values_['tn']
                )
            else:
                # Simple mapping based on prediction only
                values = np.zeros(len(y_pred))
                values[y_pred == 1] = self.monetary_values_['tp']  
                values[y_pred == 0] = self.monetary_values_['tn']  
        
        return values
    
    def monetary_score(self, X, y):
        """
        Calculate the monetary score for the predictions.
        
        Parameters
        ----------
        X : array-like of shape (n_samples, n_features)
            Samples.
        y : array-like of shape (n_samples,)
            True target values.
            
        Returns
        -------
        score : float
            Monetary score.
        """
        check_is_fitted(self)
        X = check_array(X)
        
        y_pred = self.predict(X)
        
        return float(self.scorer_(y, y_pred))
    
    def get_monetary_summary(self, X, y):
        """
        Get a detailed summary of monetary outcomes.
        
        Parameters
        ----------
        X : array-like of shape (n_samples, n_features)
            Samples.
        y : array-like of shape (n_samples,)
            True target values.
            
        Returns
        -------
        summary : dict
            Dictionary with detailed monetary outcomes.
        """
        check_is_fitted(self)
        X = check_array(X)
        
        y_pred = self.predict(X)
        
        # Convert to numpy arrays
        y = np.asarray(y)
        
        # Calculate confusion matrix entries
        tp = np.sum((y == 1) & (y_pred == 1))
        tn = np.sum((y == 0) & (y_pred == 0))
        fp = np.sum((y == 0) & (y_pred == 1))
        fn = np.sum((y == 1) & (y_pred == 0))
        
        # Calculate monetary outcomes
        tp_value = tp * self.monetary_values_['tp']
        tn_value = tn * self.monetary_values_['tn']
        fp_value = fp * self.monetary_values_['fp']
        fn_value = fn * self.monetary_values_['fn']
        total = tp_value + tn_value + fp_value + fn_value
        
        return {
            'true_positives': {'count': int(tp), 'value': float(tp_value)},
            'true_negatives': {'count': int(tn), 'value': float(tn_value)},
            'false_positives': {'count': int(fp), 'value': float(fp_value)},
            'false_negatives': {'count': int(fn), 'value': float(fn_value)},
            'total_value': float(total)
        }

class MonetaryGradientBoostingClassifier(MonetaryClassifier):
    """
    A specialized MonetaryClassifier for gradient boosting models that can directly
    optimize for monetary outcomes using custom loss functions.
    
    This class is designed to work with models that support custom objective functions,
    such as XGBoost, LightGBM, and CatBoost.
    
    Parameters
    ----------
    base_estimator : object
        The base gradient boosting estimator that supports custom objective functions.
    monetary_values : dict, default=None
        Dictionary with keys 'tp', 'tn', 'fp', 'fn' representing monetary
        values for true positives, true negatives, false positives, and
        false negatives. If None, these will be provided during fit.
    threshold : float or None, default=None
        Custom threshold for binary classification. If None, the optimal
        threshold is determined based on monetary values during fit.
    use_monetary_weights : bool, default=False
        Whether to use monetary values as sample weights during training.
    use_custom_objective : bool, default=True
        Whether to use a custom objective function based on monetary values.
    """
    
    def __init__(self, base_estimator, monetary_values=None, threshold=None, 
                 use_monetary_weights=False, use_custom_objective=True):
        super().__init__(base_estimator, monetary_values, threshold, use_monetary_weights)
        self.use_custom_objective = use_custom_objective
    
    def fit(self, X, y, dollar_values=None, sample_weight=None):
        """
        Fit the classifier with X, y and monetary values.
        
        Parameters
        ----------
        X : array-like of shape (n_samples, n_features)
            Training data.
        y : array-like of shape (n_samples,)
            Target values.
        dollar_values : dict or array-like, default=None
            If dict: Dictionary with keys 'tp', 'tn', 'fp', 'fn' representing monetary
            values for prediction outcomes.
            If array-like: Dollar values for each sample, to be used to calculate
            monetary values for prediction outcomes.
        sample_weight : array-like of shape (n_samples,), default=None
            Sample weights. If None, then samples are equally weighted.
        
        Returns
        -------
        self : object
            Returns self.
        """
        X, y = check_X_y(X, y)
        self.classes_ = np.unique(y)
        
        # Set or calculate monetary values
        if dollar_values is not None:
            if isinstance(dollar_values, dict):
                self.monetary_values_ = dollar_values
            else:
                # Calculate monetary values based on provided dollar values per sample
                self._calculate_monetary_values(y, dollar_values)
        elif self.monetary_values is not None:
            self.monetary_values_ = self.monetary_values
        else:
            # Default values (neutral)
            self.monetary_values_ = {'tp': 1, 'tn': 1, 'fp': -1, 'fn': -1}
        
        # Create the monetary scorer
        self.scorer_ = MonetaryClassificationScorer(self.monetary_values_)
        
        # Generate monetary-based sample weights if requested
        if self.use_monetary_weights:
            monetary_weights = self.scorer_.calculate_sample_weights(y)
            if sample_weight is not None:
                fit_sample_weight = sample_weight * monetary_weights
            else:
                fit_sample_weight = monetary_weights
        else:
            fit_sample_weight = sample_weight
        
        # Get the name of the library the base estimator is from
        estimator_name = type(self.base_estimator).__module__.split('.')[0]
        
        # Apply custom objective function if requested and supported
        if self.use_custom_objective:
            if estimator_name == 'xgboost':
                # Create a custom monetary objective for XGBoost
                self._fit_with_xgboost_monetary_objective(X, y, fit_sample_weight)
            elif estimator_name == 'lightgbm':
                # Create a custom monetary objective for LightGBM
                self._fit_with_lightgbm_monetary_objective(X, y, fit_sample_weight)
            elif estimator_name == 'catboost':
                # Create a custom monetary objective for CatBoost
                self._fit_with_catboost_monetary_objective(X, y, fit_sample_weight)
            else:
                # For unsupported estimators, fall back to regular fit
                warnings.warn(f"Custom objective not supported for {estimator_name}. "
                             "Using regular fit with sample weights.")
                self.base_estimator.fit(X, y, sample_weight=fit_sample_weight)
        else:
            # Use regular fit with sample weights
            self.base_estimator.fit(X, y, sample_weight=fit_sample_weight)
        
        # Find optimal threshold if none provided
        if self.threshold is None and hasattr(self.base_estimator, 'predict_proba'):
            self._find_optimal_threshold(X, y)
        
        # Store training data stats for later use
        self.X_ = X
        self.y_ = y
        
        return self
    
    def _fit_with_xgboost_monetary_objective(self, X, y, sample_weight=None):
        """
        Fit XGBoost model with a custom monetary objective function.
        
        Parameters
        ----------
        X : array-like of shape (n_samples, n_features)
            Training data.
        y : array-like of shape (n_samples,)
            Target values.
        sample_weight : array-like of shape (n_samples,), default=None
            Sample weights.
        """
        # Check if the model is an XGBoost model
        if not hasattr(self.base_estimator, 'get_xgb_params'):
            raise ValueError("Base estimator must be an XGBoost model")
        
        # Create monetary objective function
        def monetary_objective(preds, dtrain):
            y_true = dtrain.get_label()
            # Convert probabilities to class predictions using 0.5 threshold
            # (we'll optimize the threshold later)
            y_pred = (preds >= 0).astype(int)
            
            # Calculate gradients and hessians
            tp_cost = self.monetary_values_['tp']
            tn_cost = self.monetary_values_['tn']
            fp_cost = self.monetary_values_['fp']
            fn_cost = self.monetary_values_['fn']
            
            # Get probability
            p = 1 / (1 + np.exp(-preds))
            
            # Calculate gradients
            grad = np.zeros(len(y_true))
            # For positive samples (y=1)
            pos_mask = (y_true == 1)
            grad[pos_mask] = p[pos_mask] * tp_cost + (1 - p[pos_mask]) * fn_cost
            # For negative samples (y=0)
            neg_mask = (y_true == 0)
            grad[neg_mask] = p[neg_mask] * fp_cost + (1 - p[neg_mask]) * tn_cost
            
            # Calculate hessians (second derivatives)
            hess = p * (1 - p) * np.abs(
                y_true * (tp_cost - fn_cost) + (1 - y_true) * (fp_cost - tn_cost)
            )
            
            return grad, hess
        
        # Create a validation function
        def monetary_metric(preds, dtrain):
            y_true = dtrain.get_label()
            y_pred = (preds >= 0).astype(int)
            monetary_outcome = (
                np.sum((y_true == 1) & (y_pred == 1)) * self.monetary_values_['tp'] +
                np.sum((y_true == 0) & (y_pred == 0)) * self.monetary_values_['tn'] +
                np.sum((y_true == 0) & (y_pred == 1)) * self.monetary_values_['fp'] +
                np.sum((y_true == 1) & (y_pred == 0)) * self.monetary_values_['fn']
            )
            return 'monetary_score', monetary_outcome
        
        # Get XGBoost parameters
        params = self.base_estimator.get_params()
        
        # Extract XGBoost-specific parameters
        xgb_params = {}
        for key, value in params.items():
            if key.startswith('n_estimators') or key.startswith('learning_rate') or \
               key.startswith('max_depth') or key.startswith('subsample') or \
               key.startswith('colsample_') or key.startswith('reg_') or \
               key.startswith('min_') or key.startswith('gamma'):
                xgb_params[key] = value
        
        # Create DMatrix
        import xgboost as xgb
        dtrain = xgb.DMatrix(X, label=y, weight=sample_weight)
        
        # Set custom objective and evaluation metric
        xgb_params['objective'] = monetary_objective
        
        # Train the model
        num_boost_round = params.get('n_estimators', 100)
        self.base_estimator.fit(
            X, y, 
            sample_weight=sample_weight,
            obj=monetary_objective,
            eval_metric=monetary_metric
        )
    
    def _fit_with_lightgbm_monetary_objective(self, X, y, sample_weight=None):
        """
        Fit LightGBM model with a custom monetary objective function.
        
        Parameters
        ----------
        X : array-like of shape (n_samples, n_features)
            Training data.
        y : array-like of shape (n_samples,)
            Target values.
        sample_weight : array-like of shape (n_samples,), default=None
            Sample weights.
        """
        # Check if the model is a LightGBM model
        if not hasattr(self.base_estimator, 'get_params') or \
           not isinstance(self.base_estimator, object):
            raise ValueError("Base estimator must be a LightGBM model")

        # Create monetary objective function for LightGBM
        def monetary_objective(y_true, y_pred):
            # Convert sigmoid predictions to probabilities
            p = 1 / (1 + np.exp(-y_pred))
            
            # Calculate gradients
            grad = np.zeros(len(y_true))
            # For positive samples (y=1)
            pos_mask = (y_true == 1)
            grad[pos_mask] = p[pos_mask] * self.monetary_values_['tp'] + \
                           (1 - p[pos_mask]) * self.monetary_values_['fn']
            # For negative samples (y=0)
            neg_mask = (y_true == 0)
            grad[neg_mask] = p[neg_mask] * self.monetary_values_['fp'] + \
                           (1 - p[neg_mask]) * self.monetary_values_['tn']
            
            # Calculate hessians (second derivatives)
            hess = p * (1 - p) * np.abs(
                y_true * (self.monetary_values_['tp'] - self.monetary_values_['fn']) + 
                (1 - y_true) * (self.monetary_values_['fp'] - self.monetary_values_['tn'])
            )
            
            return grad, hess
            
        # Create a validation metric
        def monetary_metric(y_true, y_pred):
            y_pred_binary = (y_pred >= 0).astype(int)
            monetary_outcome = (
                np.sum((y_true == 1) & (y_pred_binary == 1)) * self.monetary_values_['tp'] +
                np.sum((y_true == 0) & (y_pred_binary == 0)) * self.monetary_values_['tn'] +
                np.sum((y_true == 0) & (y_pred_binary == 1)) * self.monetary_values_['fp'] +
                np.sum((y_true == 1) & (y_pred_binary == 0)) * self.monetary_values_['fn']
            )
            return 'monetary_score', monetary_outcome, True
            
        # Set the custom objective and eval function
        self.base_estimator.set_params(objective=monetary_objective)
        
        # Train the model
        try:
            from lightgbm import Dataset
            train_data = Dataset(X, label=y, weight=sample_weight)
            params = self.base_estimator.get_params()
            
            # Extract parameters for LightGBM
            lgb_params = {}
            for key, value in params.items():
                if key not in ['objective', 'metrics']:
                    lgb_params[key] = value
                    
            self.base_estimator.fit(
                X, y,
                sample_weight=sample_weight,
                eval_metric=monetary_metric
            )
        except Exception as e:
            warnings.warn(f"Error fitting LightGBM with custom objective: {e}. "
                         "Falling back to regular fit with sample weights.")
            self.base_estimator.fit(X, y, sample_weight=sample_weight)
    
    def _fit_with_catboost_monetary_objective(self, X, y, sample_weight=None):
        """
        Fit CatBoost model with a custom monetary objective function.
        
        Parameters
        ----------
        X : array-like of shape (n_samples, n_features)
            Training data.
        y : array-like of shape (n_samples,)
            Target values.
        sample_weight : array-like of shape (n_samples,), default=None
            Sample weights.
        """
        try:
            from catboost import Pool
            from catboost.core import CatBoostError
            
            # Create a custom monetary objective
            class MonetaryObjective:
                def __init__(self, monetary_values):
                    self.monetary_values = monetary_values
                
                def calc_ders_range(self, approxes, targets, weights):
                    assert len(approxes) == 1
                    approx = approxes[0]
                    
                    # Convert to probabilities
                    sigmoid = lambda x: 1 / (1 + np.exp(-x))
                    p = sigmoid(approx)
                    
                    # Calculate gradients
                    grad = np.zeros(len(targets))
                    # For positive samples (y=1)
                    pos_mask = (targets == 1)
                    grad[pos_mask] = p[pos_mask] * self.monetary_values['tp'] + \
                                  (1 - p[pos_mask]) * self.monetary_values['fn']
                    # For negative samples (y=0)
                    neg_mask = (targets == 0)
                    grad[neg_mask] = p[neg_mask] * self.monetary_values['fp'] + \
                                  (1 - p[neg_mask]) * self.monetary_values['tn']
                    
                    # Calculate hessians (second derivatives)
                    hess = p * (1 - p) * np.abs(
                        targets * (self.monetary_values['tp'] - self.monetary_values['fn']) + 
                        (1 - targets) * (self.monetary_values['fp'] - self.monetary_values['tn'])
                    )
                    
                    if weights is not None:
                        grad *= weights
                        hess *= weights
                    
                    return (grad, hess)
            
            # Create a custom monetary metric
            class MonetaryMetric:
                def __init__(self, monetary_values):
                    self.monetary_values = monetary_values
                
                def get_final_error(self, error, weight):
                    return error
                
                def is_max_optimal(self):
                    return True
                
                def evaluate(self, approxes, target, weight):
                    assert len(approxes) == 1
                    approx = approxes[0]
                    
                    # Convert to binary predictions
                    y_pred = (approx >= 0).astype(int)
                    
                    # Calculate monetary outcome
                    monetary_outcome = (
                        np.sum((target == 1) & (y_pred == 1)) * self.monetary_values['tp'] +
                        np.sum((target == 0) & (y_pred == 0)) * self.monetary_values['tn'] +
                        np.sum((target == 0) & (y_pred == 1)) * self.monetary_values['fp'] +
                        np.sum((target == 1) & (y_pred == 0)) * self.monetary_values['fn']
                    )
                    
                    return monetary_outcome, 1
            
            # Create Pool object
            train_pool = Pool(X, y, weight=sample_weight)
            
            # Get original parameters
            params = self.base_estimator.get_params()
            
            # Create a new instance of CatBoost with custom objective
            try:
                # Try to set custom loss function
                self.base_estimator.set_params(
                    loss_function=MonetaryObjective(self.monetary_values_)
                )
                
                # Create custom metric
                monetary_metric = MonetaryMetric(self.monetary_values_)
                
                # Train with custom objective and metric
                self.base_estimator.fit(
                    train_pool,
                    eval_metric=monetary_metric
                )
            except CatBoostError:
                warnings.warn("CatBoost does not support fully custom objectives. "
                             "Using sample weights instead.")
                self.base_estimator.fit(X, y, sample_weight=sample_weight)
        except ImportError:
            warnings.warn("CatBoost not installed. Using regular fit with sample weights.")
            self.base_estimator.fit(X, y, sample_weight=sample_weight)
        except Exception as e:
            warnings.warn(f"Error fitting CatBoost with custom objective: {e}. "
                         "Falling back to regular fit with sample weights.")
            self.base_estimator.fit(X, y, sample_weight=sample_weight)

def make_monetary_scorer(monetary_values):
    """
    Make a scorer that evaluates a classifier based on monetary outcomes.
    
    Parameters
    ----------
    monetary_values : dict
        Dictionary with keys 'tp', 'tn', 'fp', 'fn' representing monetary
        values for true positives, true negatives, false positives, and
        false negatives.
        
    Returns
    -------
    scorer : callable
        Scorer object that can be used with scikit-learn.
    """
    scorer = MonetaryClassificationScorer(monetary_values)
    
    # Make it compatible with scikit-learn's scoring interface
    def scorer_wrapper(estimator, X, y):
        y_pred = estimator.predict(X)
        return scorer(y, y_pred)
    
    return make_scorer(scorer_wrapper)

def optimize_monetary_classifier(estimator, X, y, monetary_values, param_grid, cv=5, 
                                use_monetary_weights=True, n_jobs=-1):
    """
    Optimize a classifier for monetary outcomes using grid search.
    
    Parameters
    ----------
    estimator : object
        The base estimator to optimize.
    X : array-like of shape (n_samples, n_features)
        Training data.
    y : array-like of shape (n_samples,)
        Target values.
    monetary_values : dict
        Dictionary with keys 'tp', 'tn', 'fp', 'fn' representing monetary
        values for true positives, true negatives, false positives, and
        false negatives.
    param_grid : dict
        Parameter grid for grid search.
    cv : int, default=5
        Number of cross-validation folds.
    use_monetary_weights : bool, default=True
        Whether to use monetary values as sample weights during training.
    n_jobs : int, default=-1
        Number of jobs for parallel processing.
        
    Returns
    -------
    clf : MonetaryClassifier
        Optimized monetary classifier.
    """
    # Create a monetary classifier with the base estimator
    monetary_clf = MonetaryClassifier(
        estimator, 
        monetary_values=monetary_values,
        use_monetary_weights=use_monetary_weights
    )
    
    # Create a monetary scorer
    scorer = make_monetary_scorer(monetary_values)
    
    # Perform grid search
    grid_search = GridSearchCV(
        monetary_clf,
        param_grid,
        scoring=scorer,
        cv=cv,
        n_jobs=n_jobs
    )
    
    grid_search.fit(X, y)
    
    return grid_search.best_estimator_, grid_search.best_params_, grid_search.best_score_

# Utility function for lending scenarios
def create_lending_monetary_values(loan_amount, interest_rate=0.05, default_cost_factor=1.0):
    """
    Create monetary values for lending scenarios.
    
    Parameters
    ----------
    loan_amount : float
        Amount of the loan.
    interest_rate : float, default=0.05
        Interest rate for the loan.
    default_cost_factor : float, default=1.0
        Factor for the cost of a default. 1.0 means the entire loan amount is lost.
        
    Returns
    -------
    monetary_values : dict
        Dictionary with monetary values for lending scenarios.
    """
    return {
        'tp': loan_amount * interest_rate,  # Approve loan that is repaid - gain interest
        'tn': 0,  # Deny loan that would default - no gain/loss
        'fp': -loan_amount * default_cost_factor,  # Approve loan that defaults - lose principal
        'fn': -loan_amount * interest_rate  # Deny loan that would be repaid - lose interest
    }
