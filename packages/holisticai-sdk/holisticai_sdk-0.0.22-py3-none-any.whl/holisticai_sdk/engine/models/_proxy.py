from __future__ import annotations

from typing import Literal, Callable
from numpy.typing import ArrayLike, NDArray  # noqa: TCH002
import pandas as pd
from holisticai_sdk.engine.definitions import (
    HAIClustering,
    HAIProbBinaryClassification,
    HAIProbMultiClassification,
    HAIRegression,
    HAIRigidBinaryClassification,
    HAIRigidMultiClassification,
    HAIModel,
)

def get_proxy_from_sdk_model(
    task: Literal["binary_classification", "regression", "multi_classification", "clustering"],
    predict_fn: Callable[[pd.DataFrame], ArrayLike],
    predict_proba_fn: Callable[[pd.DataFrame], ArrayLike] | None = None,
    classes: list | None = None,
    name: str = "",
) -> HAIModel:
    if classes is None:
        classes = []

    match task:
        case "binary_classification":
            if predict_proba_fn is None:
                return HAIRigidBinaryClassification(name=name, predict=predict_fn, classes=classes)
            
            return HAIProbBinaryClassification(
                    name=name,
                    predict=predict_fn,
                    predict_proba=predict_proba_fn,
                    classes=classes,
                )
        
        case "regression":
            return HAIRegression(name=name, predict=predict_fn)

        case "multi_classification":
            if predict_proba_fn is None:
                return HAIRigidMultiClassification(name=name, predict=predict_fn, classes=classes)
            
            return HAIProbMultiClassification(
                    name=name,
                    predict=predict_fn,
                    predict_proba=predict_proba_fn,
                    classes=classes,
                )
        
        case "clustering":
            return HAIClustering(name=name, predict=predict_fn, classes=classes)
