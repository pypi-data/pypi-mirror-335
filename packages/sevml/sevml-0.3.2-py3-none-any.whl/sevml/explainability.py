import pandas as pd
import shap

def plot_shap_explanations(X, model, df_features):
    features_array = pd.unique(df_features["nom_marqueur"]).tolist()
    X = pd.DataFrame(X, columns=features_array)
    explainer = shap.TreeExplainer(model)
    shap_values = explainer(X)
    shap.plots.heatmap(shap_values)
    shap.plots.violin(shap_values)
    shap.plots.bar(shap_values)
    shap.plots.beeswarm(shap_values)
    shap.plots.waterfall(shap_values[0])
    shap.decision_plot(shap_values.base_values[0], shap_values.values, X)
