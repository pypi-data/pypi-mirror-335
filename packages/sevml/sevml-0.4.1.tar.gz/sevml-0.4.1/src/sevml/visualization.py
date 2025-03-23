import numpy as np
import matplotlib.pyplot as plt
from sklearn.model_selection import learning_curve, validation_curve

def plot_model_curves(model, X=None, y=None, cv=5, scoring='accuracy', param_name='max_depth', param_range=None, train_sizes=None):
    if X is None or y is None:
        raise ValueError("Les arguments X et y doivent être fournis pour générer les courbes.")
    if param_range is None:
        param_range = np.arange(1, 11)
    if train_sizes is None:
        train_sizes = np.linspace(0.1, 1.0, 5)

    def plot_curve(x, train_mean, val_mean, train_std, val_std, xlabel, title):
        plt.figure(figsize=(10, 6))
        plt.plot(x, train_mean, label='Score entraînement', color='red', linewidth=2)
        plt.fill_between(x, train_mean - train_std, train_mean + train_std, alpha=0.2, color='red')
        plt.plot(x, val_mean, label='Score validation', color='green', linewidth=2)
        plt.fill_between(x, val_mean - val_std, val_mean + val_std, alpha=0.2, color='green')
        plt.xlabel(xlabel, fontsize=12)
        plt.ylabel(scoring.capitalize(), fontsize=12)
        plt.title(title, fontsize=14, weight='bold')
        plt.legend(loc='best', fontsize=10)
        plt.grid(True, linestyle='--', alpha=0.6)
        plt.tight_layout()
        plt.show()

    train_sizes_abs, train_scores, val_scores = learning_curve(
        estimator=model, X=X, y=y, train_sizes=train_sizes, cv=cv, scoring=scoring, n_jobs=-1)
    train_mean = np.mean(train_scores, axis=1)
    val_mean = np.mean(val_scores, axis=1)
    train_std = np.std(train_scores, axis=1)
    val_std = np.std(val_scores, axis=1)
    plot_curve(train_sizes_abs, train_mean, val_mean, train_std, val_std, "Taille de l'échantillon d'entraînement", 'Courbe d\'apprentissage')

    train_scores, val_scores = validation_curve(
        estimator=model, X=X, y=y, param_name=param_name, param_range=param_range, cv=cv, scoring=scoring, n_jobs=-1)
    train_mean = np.mean(train_scores, axis=1)
    val_mean = np.mean(val_scores, axis=1)
    train_std = np.std(train_scores, axis=1)
    val_std = np.std(val_scores, axis=1)
    plot_curve(param_range, train_mean, val_mean, train_std, val_std, param_name, f'Courbe de validation : {param_name}')
