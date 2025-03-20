from __future__ import annotations  # noqa: I001
import pandas as pd  # noqa: TCH002
from numpy.typing import ArrayLike  # noqa: TCH002
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.neighbors import KNeighborsClassifier

from holisticai_sdk.engine.definitions import (
    HAIModel,
    HAIProbMultiClassification,
)



def logistic_regression_baseline(x: pd.DataFrame, y: ArrayLike):
    lr = LogisticRegression()

    lr.fit(X=x, y=y)

    return HAIProbMultiClassification(
        predict=lr.predict,
        predict_proba=lr.predict_proba,
        classes=list(lr.classes_),
        name="Logistic Regression",
    )



def svc_baseline(x: pd.DataFrame, y: ArrayLike):
    svc = SVC(probability=True)
    svc.fit(X=x, y=y)

    return HAIProbMultiClassification(
        predict=svc.predict,
        predict_proba=svc.predict_proba,
        classes=list(svc.classes_),
        name="SVC",
    )



def dt_baseline(x: pd.DataFrame, y: ArrayLike):
    dt = DecisionTreeClassifier()
    dt.fit(X=x, y=y)
    return HAIProbMultiClassification(
        predict=dt.predict,
        predict_proba=dt.predict_proba,
        classes=list(dt.classes_),
        name="DecisionTree",
    )



def rf_baseline(x: pd.DataFrame, y: ArrayLike):
    rf = RandomForestClassifier()
    rf.fit(X=x, y=y)
    return HAIProbMultiClassification(
        predict=rf.predict,
        predict_proba=rf.predict_proba,
        classes=list(rf.classes_),
        name="RandomForest",
    )



def knn_baseline(x: pd.DataFrame, y: ArrayLike):
    knn = KNeighborsClassifier()
    knn.fit(X=x, y=y)
    return HAIProbMultiClassification(
        predict=knn.predict,
        predict_proba=knn.predict_proba,
        classes=list(knn.classes_),
        name="KNN",
    )



def get_multi_classification_baselines(x: pd.DataFrame, y: ArrayLike) -> list[HAIModel[HAIProbMultiClassification]]:
    baselines = [
        logistic_regression_baseline,
        svc_baseline,
        dt_baseline,
        rf_baseline,
        knn_baseline,

    ]

    return [baseline(x=x, y=y) for baseline in baselines]
