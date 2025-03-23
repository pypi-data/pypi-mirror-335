import warnings
from xgboost import XGBClassifier
from sklearn.model_selection import GridSearchCV

def train_xgb_with_gridsearch(X, y, eval_metric='logloss', random_state=5, cv=3):
    warnings.filterwarnings('ignore')
    param_grid = {
        'n_estimators': [10, 30, 50, 100],
        'max_depth': [3, 4, 5, 6, 7],
        'learning_rate': [0.01, 0.1]
    }
    grid = GridSearchCV(
        XGBClassifier(eval_metric=eval_metric, random_state=random_state),
        param_grid=param_grid,
        cv=cv,
        verbose=2,
        n_jobs=-1
    )
    grid.fit(X, y)
    print("Best parameters:", grid.best_params_)
    model = grid.best_estimator_
    return model, grid.best_params_
