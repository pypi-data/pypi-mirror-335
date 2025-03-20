from __future__ import annotations  # noqa: I001
import pandas as pd  # noqa: TCH002
from numpy.typing import ArrayLike  # noqa: TCH002
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC

from holisticai_sdk.engine.definitions import (
    HAIModel,
    HAIProbBinaryClassification,
)


def logistic_regression_baseline(x: pd.DataFrame, y: ArrayLike):
    if x.shape[0]<10000:
        solver = 'liblinear'
    else:
        solver = 'saga'
    lr = LogisticRegression(max_iter=1000, solver=solver)

    lr.fit(X=x, y=y)

    return HAIProbBinaryClassification(
            predict=lr.predict,
            predict_proba=lambda x: lr.predict_proba(X=x)[:, 1],
            classes=list(lr.classes_),
            name="Logistic Regression")


def svc_baseline(x: pd.DataFrame, y: ArrayLike):
    svc = SVC(probability=True)
    svc.fit(X=x, y=y)

    return HAIProbBinaryClassification(
        predict=svc.predict,
        predict_proba=lambda x: svc.predict_proba(X=x)[:, 1],
        classes=list(svc.classes_),
        name="SVC",
    )

    
def get_binary_classification_baselines(x: pd.DataFrame, y: ArrayLike) -> list[HAIModel[HAIProbBinaryClassification]]:
    baselines = [logistic_regression_baseline, svc_baseline]
    return [baseline(x=x, y=y) for baseline in baselines]
