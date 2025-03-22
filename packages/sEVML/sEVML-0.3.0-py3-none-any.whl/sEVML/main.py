import warnings
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import shap
import random
from xgboost import XGBClassifier
import sklearn
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import MinMaxScaler
from sklearn.model_selection import train_test_split, StratifiedKFold
from sklearn.metrics import (
    confusion_matrix, ConfusionMatrixDisplay,
    roc_curve, auc, roc_auc_score, f1_score
)
from sklearn.model_selection import (
    validation_curve, learning_curve, GridSearchCV
)
from sklearn.utils.validation import check_is_fitted

def main():
    """Entry point for the 'sevml' command-line script."""
    print("Welcome to sEVML!")

def preprocess_elisa_dataset(filepath, label_mapping, test_size=0.2, random_state=5):
    """
    Charge, nettoie et prépare le dataset ELISA pour l'entraînement et le test.

    Parameters:
        filepath (str): Chemin vers le fichier CSV contenant les données.
        label_mapping (dict): Dictionnaire pour mapper les valeurs cibles, ex: {"S": 0, "PD": 1}.
        test_size (float): Proportion du dataset à inclure dans le test split.
        random_state (int): Graine pour le random split.

    Returns:
        X_train, X_test, y_train, y_test: Données prêtes pour l'entraînement et le test.
    """
    # Importation du dataset
    df = pd.read_csv(filepath)

    # Nettoyage des colonnes inutiles
    df = df.drop(["nom_cohorte", "nom_parametre", "followup"], axis=1)

    # Pivot des marqueurs en colonnes
    df_2 = df.pivot(columns="nom_marqueur", index="id_patient", values="valeur_elisa")

    # Informations complémentaires
    df_3 = df.drop(["nom_marqueur", "valeur_elisa"], axis=1).drop_duplicates(subset=["id_patient"])

    # Fusion des données
    df_merged = df_2.merge(df_3, on="id_patient", how="inner").drop(["id_patient"], axis=1)

    # Séparation des variables
    X = df_merged.drop(["valeur_criteres_DPI"], axis=1).copy()
    y = df_merged["valeur_criteres_DPI"].map(label_mapping)

    # Vérification si toutes les valeurs ont été mappées
    if y.isnull().any():
        missing_labels = df_merged["valeur_criteres_DPI"][y.isnull()].unique()
        raise ValueError(f"Certaines valeurs cibles n'ont pas été mappées : {missing_labels}")

    # Imputation des valeurs manquantes
    imputer = SimpleImputer(strategy='median')
    X = imputer.fit_transform(X)

    # Normalisation des données
    scaler = MinMaxScaler()
    X = scaler.fit_transform(X)

    # Découpage du dataset
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=test_size, random_state=random_state)

    print('Train set:', X_train.shape)
    print('Test set:', X_test.shape)
    print('Train set (labels):', y_train.shape)
    print('Test set (labels):', y_test.shape)

    return X_train, X_test, y_train, y_test

def train_xgb_with_gridsearch(X, y, eval_metric='logloss', random_state=5, cv=3):
    """
    Entraîne un modèle XGBoost avec GridSearchCV.

    Paramètres obligatoires :
        - X : Features (ex. X_train)
        - y : Labels (ex. y_train)

    Paramètres optionnels :
        - eval_metric : Métrique d'évaluation pour XGBoost (default = 'logloss')
        - random_state : Graine pour la reproductibilité (default = 5)
        - cv : Nombre de folds pour la cross-validation (default = 3)

    Retour :
        - model : Meilleur estimateur entraîné
        - best_params : Dictionnaire des meilleurs hyperparamètres
    """
    warnings.filterwarnings('ignore')

    param_grid = {
        'n_estimators': [10, 30, 50, 100],
        'max_depth': [3, 4, 5, 6, 7],
        'learning_rate': [0.01, 0.1]
    }

    grid = GridSearchCV(
        XGBClassifier(use_label_encoder=False,
                      eval_metric=eval_metric,
                      random_state=random_state),
        param_grid=param_grid,
        cv=cv,
        verbose=2,
        n_jobs=-1
    )

    grid.fit(X, y)
    print("Best parameters:", grid.best_params_)

    model = grid.best_estimator_
    return model, grid.best_params_


plt.style.use('ggplot')

def plot_model_curves(
    model,
    X=None,
    y=None,
    cv=5,
    scoring='accuracy',
    param_name='max_depth',
    param_range=None,
    train_sizes=None
):
    import numpy as np
    import matplotlib.pyplot as plt
    from sklearn.model_selection import learning_curve, validation_curve

    # Vérifications
    if X is None or y is None:
        raise ValueError("Les arguments X et y doivent être fournis pour générer les courbes.")

    # Paramètres par défaut
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

    # --- Courbe d'apprentissage ---
    train_sizes_abs, train_scores, val_scores = learning_curve(
        estimator=model,
        X=X,
        y=y,
        train_sizes=train_sizes,
        cv=cv,
        scoring=scoring,
        n_jobs=-1
    )

    train_mean = np.mean(train_scores, axis=1)
    val_mean = np.mean(val_scores, axis=1)
    train_std = np.std(train_scores, axis=1)
    val_std = np.std(val_scores, axis=1)

    plot_curve(
        x=train_sizes_abs,
        train_mean=train_mean,
        val_mean=val_mean,
        train_std=train_std,
        val_std=val_std,
        xlabel="Taille de l'échantillon d'entraînement",
        title='Courbe d\'apprentissage'
    )

    # --- Courbe de validation ---
    train_scores, val_scores = validation_curve(
        estimator=model,
        X=X,
        y=y,
        param_name=param_name,
        param_range=param_range,
        cv=cv,
        scoring=scoring,
        n_jobs=-1
    )

    train_mean = np.mean(train_scores, axis=1)
    val_mean = np.mean(val_scores, axis=1)
    train_std = np.std(train_scores, axis=1)
    val_std = np.std(val_scores, axis=1)

    plot_curve(
        x=param_range,
        train_mean=train_mean,
        val_mean=val_mean,
        train_std=train_std,
        val_std=val_std,
        xlabel=param_name,
        title=f'Courbe de validation : {param_name}'
    )



def evaluate_model(model, X_train, y_train, X_test, y_test):
    # Predictions from your model
    y_pred_train = model.predict(X_train)
    y_pred_test = model.predict(X_test)

    # Probabilities for ROC curve
    # Use predict_proba if available, else decision_function
    try:
        y_proba_train = model.predict_proba(X_train)[:, 1]
        y_proba_test = model.predict_proba(X_test)[:, 1]
    except AttributeError:
        y_proba_train = model.decision_function(X_train)
        y_proba_test = model.decision_function(X_test)

    # ROC curve
    fpr_train, tpr_train, _ = roc_curve(y_train, y_proba_train)
    roc_auc_train = auc(fpr_train, tpr_train)

    fpr_test, tpr_test, _ = roc_curve(y_test, y_proba_test)
    roc_auc_test = auc(fpr_test, tpr_test)

    # Confusion matrices
    conf_matrix_train = confusion_matrix(y_train, y_pred_train)
    conf_matrix_test = confusion_matrix(y_test, y_pred_test)

    # F1-scores
    f1_train = f1_score(y_train, y_pred_train)
    f1_test = f1_score(y_test, y_pred_test)

    # Accuracy
    acc_train = np.mean(y_pred_train == y_train)
    acc_test = np.mean(y_pred_test == y_test)

    # Création de la figure avec 3 sous-graphes (1 en haut, 2 en bas)
    fig = plt.figure(figsize=(12, 10))
    plt.style.use('seaborn-v0_8-whitegrid')

    # ROC sur toute la largeur du haut
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
    # Sous-titre avec l'accuracy
    ax1.text(0.5, -0.2, f"Train Accuracy: {acc_train:.2f} | Test Accuracy: {acc_test:.2f}",
             transform=ax1.transAxes, ha='center', fontsize=12)

    # Confusion Matrix Train
    ax2 = fig.add_subplot(2, 2, 3)
    disp_train = ConfusionMatrixDisplay(confusion_matrix=conf_matrix_train)
    disp_train.plot(ax=ax2, cmap='Blues', colorbar=False)
    ax2.set_title(f"Train Confusion Matrix\nF1-score: {f1_train:.2f}", fontsize=12)
    ax2.grid(False)
    # Confusion Matrix Test
    ax3 = fig.add_subplot(2, 2, 4)
    disp_test = ConfusionMatrixDisplay(confusion_matrix=conf_matrix_test)
    disp_test.plot(ax=ax3, cmap='Blues', colorbar=False)
    ax3.set_title(f"Test Confusion Matrix\nF1-score: {f1_test:.2f}", fontsize=12)
    ax3.grid(False)

    plt.tight_layout()
    plt.show()


def plot_shap_explanations(X, model, df_features):
    # Extraction des noms de colonnes
    features_array = pd.unique(df_features["nom_marqueur"]).tolist()
    X = pd.DataFrame(X, columns=features_array)

    # Création de l'explainer SHAP
    explainer = shap.TreeExplainer(model)
    shap_values = explainer(X)

    # Visualisations SHAP
    shap.plots.heatmap(shap_values)
    shap.plots.violin(shap_values)
    shap.plots.bar(shap_values)
    shap.plots.beeswarm(shap_values)
    shap.plots.waterfall(shap_values[0])
    shap.decision_plot(
        shap_values.base_values[0],
        shap_values.values,
        X
    )
