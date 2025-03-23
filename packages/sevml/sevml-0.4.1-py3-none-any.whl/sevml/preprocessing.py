import pandas as pd
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import MinMaxScaler
from sklearn.model_selection import train_test_split

def preprocess_elisa_dataset(filepath, label_mapping, test_size=0.2, random_state=5):
    df = pd.read_csv(filepath)
    df = df.drop(["nom_cohorte", "nom_parametre", "followup"], axis=1)
    df_2 = df.pivot(columns="nom_marqueur", index="id_patient", values="valeur_elisa")
    df_3 = df.drop(["nom_marqueur", "valeur_elisa"], axis=1).drop_duplicates(subset=["id_patient"])
    df_merged = df_2.merge(df_3, on="id_patient", how="inner").drop(["id_patient"], axis=1)
    X = df_merged.drop(["valeur_criteres_DPI"], axis=1).copy()
    y = df_merged["valeur_criteres_DPI"].map(label_mapping)
    if y.isnull().any():
        missing_labels = df_merged["valeur_criteres_DPI"][y.isnull()].unique()
        raise ValueError(f"Certaines valeurs cibles n'ont pas été mappées : {missing_labels}")
    imputer = SimpleImputer(strategy='median')
    X = imputer.fit_transform(X)
    scaler = MinMaxScaler()
    X = scaler.fit_transform(X)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=test_size, random_state=random_state)
    print('Train set:', X_train.shape)
    print('Test set:', X_test.shape)
    print('Train set (labels):', y_train.shape)
    print('Test set (labels):', y_test.shape)
    return X_train, X_test, y_train, y_test
