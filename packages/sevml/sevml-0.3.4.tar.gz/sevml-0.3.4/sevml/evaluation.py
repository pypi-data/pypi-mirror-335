import numpy as np
import matplotlib.pyplot as plt
from sklearn.metrics import confusion_matrix, ConfusionMatrixDisplay, roc_curve, auc, f1_score

def evaluate_model(model, X_train, y_train, X_test, y_test):
    y_pred_train = model.predict(X_train)
    y_pred_test = model.predict(X_test)
    try:
        y_proba_train = model.predict_proba(X_train)[:, 1]
        y_proba_test = model.predict_proba(X_test)[:, 1]
    except AttributeError:
        y_proba_train = model.decision_function(X_train)
        y_proba_test = model.decision_function(X_test)

    fpr_train, tpr_train, _ = roc_curve(y_train, y_proba_train)
    roc_auc_train = auc(fpr_train, tpr_train)
    fpr_test, tpr_test, _ = roc_curve(y_test, y_proba_test)
    roc_auc_test = auc(fpr_test, tpr_test)
    conf_matrix_train = confusion_matrix(y_train, y_pred_train)
    conf_matrix_test = confusion_matrix(y_test, y_pred_test)
    f1_train = f1_score(y_train, y_pred_train)
    f1_test = f1_score(y_test, y_pred_test)
    acc_train = np.mean(y_pred_train == y_train)
    acc_test = np.mean(y_pred_test == y_test)

    fig = plt.figure(figsize=(12, 10))
    plt.style.use('seaborn-v0_8-whitegrid')

    ax1 = fig.add_subplot(2, 1, 1)
    ax1.set_aspect('equal', adjustable='box')
    ax1.plot(fpr_train, tpr_train, label=f"Train ROC (AUC = {roc_auc_train:.2f})", color='blue')
    ax1.plot(fpr_test, tpr_test, label=f"Test ROC (AUC = {roc_auc_test:.2f})", color='orange')
    ax1.plot([0, 1], [0, 1], linestyle='--', color='grey')
    ax1.set_title("Courbe ROC", fontsize=14)
    ax1.set_xlabel("Taux de faux positifs")
    ax1.set_ylabel("Taux de vrais positifs")
    ax1.legend()
    ax1.grid(True)
    ax1.text(0.5, -0.2, f"Train Accuracy: {acc_train:.2f} | Test Accuracy: {acc_test:.2f}", transform=ax1.transAxes, ha='center', fontsize=12)

    ax2 = fig.add_subplot(2, 2, 3)
    disp_train = ConfusionMatrixDisplay(confusion_matrix=conf_matrix_train)
    disp_train.plot(ax=ax2, cmap='Blues', colorbar=False)
    ax2.set_title(f"Train Confusion Matrix\nF1-score: {f1_train:.2f}", fontsize=12)
    ax2.grid(False)

    ax3 = fig.add_subplot(2, 2, 4)
    disp_test = ConfusionMatrixDisplay(confusion_matrix=conf_matrix_test)
    disp_test.plot(ax=ax3, cmap='Blues', colorbar=False)
    ax3.set_title(f"Test Confusion Matrix\nF1-score: {f1_test:.2f}", fontsize=12)
    ax3.grid(False)

    plt.tight_layout()
    plt.show()
