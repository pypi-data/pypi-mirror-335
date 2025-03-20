from __future__ import annotations

from typing import TYPE_CHECKING

from joblib import logger
import numpy as np
import pandas as pd
from holisticai_sdk.engine.definitions import HAIModel, HAIProbBinaryClassification, HAIProbMultiClassification

if TYPE_CHECKING:
    from holisticai.utils import ModelProxy

from holisticai_sdk.utils.logger import get_logger


logger = get_logger(__name__)


def convert_to_holisticai_proxy(model: HAIModel) -> ModelProxy:
    from holisticai.utils import (
        BinaryClassificationProxy,
        MultiClassificationProxy,
        RegressionProxy,
    )

    match model.learning_task:
        case "binary_classification":
            if model.has_probability:
                matrix_dim = 2
                binary_dim = 2

                def predict_proba_from_probability(X: pd.DataFrame):  # noqa: N803
                    y = model.predict_proba(X)  # type: ignore
                    if len(y.shape) == matrix_dim and y.shape[1] == binary_dim:  # type: ignore
                        return y
                    if len(y.shape) == 1:  # type: ignore
                        y_ = y.reshape(-1, 1)  # type: ignore
                        return np.concatenate([1 - y_, y_], axis=1)
                    raise ValueError

                predict_proba = predict_proba_from_probability
            else:

                def predict_proba_from_predict(X: pd.DataFrame):  # noqa: N803
                    y = model.predict(X)  # type: ignore
                    y_ = y.reshape(-1, 1)  # type: ignore
                    return np.concatenate([1 - y_, y_], axis=1)

                predict_proba = predict_proba_from_predict
            return BinaryClassificationProxy(
                predict=model.predict,
                predict_proba=predict_proba,
                classes=model.classes,
            )

        case "multi_classification":
            predict_proba = model.predict_proba if model.has_probability is True else None
            return MultiClassificationProxy(
                predict=model.predict,
                predict_proba=predict_proba, # type: ignore
                classes=model.classes,
            )  # type: ignore

        case "regression":
            return RegressionProxy(predict=model.predict)
    raise NotImplementedError


def predict(model: HAIModel | None, X: pd.DataFrame):  # noqa: N803
    if model is None:
        return None
    return model.predict(X)


def predict_proba(model: HAIModel | None, X: pd.DataFrame):  # noqa: N803
    if model is None:
        return None
    if isinstance(model, HAIProbBinaryClassification):
        return pd.Series(model.predict_proba(X))
    if isinstance(model, HAIProbMultiClassification):
        return model.predict_proba(X)
    logger.warning(f"predict_proba function is not supported for model type: {type(model)}")
    return None
