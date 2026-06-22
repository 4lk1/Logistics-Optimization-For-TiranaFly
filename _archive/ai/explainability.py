import numpy as np
import pandas as pd
from typing import Dict, Any, List, Optional

try:
    import shap
except ImportError:
    shap = None

class ModelExplainer:
    """
    Provides explainability for TiranaFly ML models.
    Supports Global Feature Importance and Local SHAP explanations.
    """
    
    def __init__(self, model: Any):
        self.model = model

    def get_feature_importance(self, feature_names: List[str]) -> pd.DataFrame:
        """Returns the global feature importance of the model."""
        if hasattr(self.model, 'feature_importances_'):
            importances = self.model.feature_importances_
        elif hasattr(self.model, 'coef_'):
            importances = np.abs(self.model.coef_)
        else:
            return pd.DataFrame()
            
        return pd.DataFrame({
            'Feature': feature_names,
            'Importance': importances
        }).sort_values('Importance', ascending=False)

    def get_local_explanation(self, instance: pd.DataFrame) -> Dict[str, float]:
        """
        Returns SHAP values for a single prediction.
        Helps operators understand why a certain forecast or failure risk was generated.
        """
        if shap is None:
            return {"error": "SHAP library not installed."}
            
        explainer = shap.Explainer(self.model)
        shap_values = explainer(instance)
        
        # Return a dictionary of feature contributions
        contributions = dict(zip(instance.columns, shap_values.values[0]))
        return contributions
