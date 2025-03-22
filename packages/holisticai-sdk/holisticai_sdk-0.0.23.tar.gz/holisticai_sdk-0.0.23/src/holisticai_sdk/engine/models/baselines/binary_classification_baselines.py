from __future__ import annotations  # noqa: I001
import pandas as pd  # noqa: TCH002
from numpy.typing import ArrayLike  # noqa: TCH002
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.tree import DecisionTreeClassifier, ExtraTreeClassifier
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

def random_forest_baseline(x: pd.DataFrame, y: ArrayLike):
    rf = RandomForestClassifier()
    rf.fit(X=x, y=y)

    return HAIProbBinaryClassification(
        predict=rf.predict,
        predict_proba=lambda x: rf.predict_proba(X=x)[:, 1],
        classes=list(rf.classes_),
        name="Random Forest",
    )

def gradient_boosting_baseline(x: pd.DataFrame, y: ArrayLike):
    gb = GradientBoostingClassifier()
    gb.fit(X=x, y=y)

    return HAIProbBinaryClassification(
        predict=gb.predict,
        predict_proba=lambda x: gb.predict_proba(X=x)[:, 1],
        classes=list(gb.classes_),
        name="Gradient Boosting",
    )

def decision_tree_baseline(x: pd.DataFrame, y: ArrayLike):
    dt = DecisionTreeClassifier()
    dt.fit(X=x, y=y)

    return HAIProbBinaryClassification(
        predict=dt.predict,
        predict_proba=lambda x: dt.predict_proba(X=x)[:, 1],
        classes=list(dt.classes_),
        name="Decision Tree",
    )

def extra_tree_baseline(x: pd.DataFrame, y: ArrayLike):
    et = ExtraTreeClassifier()
    et.fit(X=x, y=y)

    return HAIProbBinaryClassification(
        predict=et.predict,
        predict_proba=lambda x: et.predict_proba(X=x)[:, 1],
        classes=list(et.classes_),
        name="Extra Tree",
    )

def get_binary_classification_baselines(x: pd.DataFrame, y: ArrayLike) -> list[HAIModel[HAIProbBinaryClassification]]:
    baselines = [logistic_regression_baseline, svc_baseline, random_forest_baseline, gradient_boosting_baseline, decision_tree_baseline, extra_tree_baseline]
    return [baseline(x=x, y=y) for baseline in baselines]
