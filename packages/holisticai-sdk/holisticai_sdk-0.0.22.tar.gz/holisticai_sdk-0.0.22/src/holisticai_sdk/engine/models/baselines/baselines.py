from __future__ import annotations

from typing import TYPE_CHECKING, Literal

from typing_extensions import assert_never

from holisticai_sdk.engine.models.baselines.binary_classification_baselines import (
    get_binary_classification_baselines,
)
from holisticai_sdk.engine.models.baselines.clustering_baselines import (
    get_clustering_baselines,
)
from holisticai_sdk.engine.models.baselines.multi_classification_baselines import (
    get_multi_classification_baselines,
)
from holisticai_sdk.engine.models.baselines.regression_baselines import (
    get_regression_baselines,
)

if TYPE_CHECKING:
    import pandas as pd

    from holisticai_sdk.engine.definitions import HAIModel



def get_baselines(
    learning_task: Literal["binary_classification", "regression", "multi_classification", "clustering"],
    x: pd.DataFrame,
    y: pd.Series | None = None,
    n_clusters: int | None = None,
) -> list[HAIModel]:
    match learning_task:
        case "binary_classification":
            if y is None:
                message = "y must be provided for binary classification task"
                raise ValueError(message)
            return get_binary_classification_baselines(x=x, y=y)
        case "regression":
            if y is None:
                message = "y must be provided for regression task"
                raise ValueError(message)
            return get_regression_baselines(x=x, y=y)
        case "multi_classification":
            if y is None:
                message = "y must be provided for multi classification task"
                raise ValueError(message)
            return get_multi_classification_baselines(x=x, y=y)
        case "clustering":
            if n_clusters is None:
                message = "n_clusters must be provided for clustering task"
                raise ValueError(message)
            return get_clustering_baselines(x=x, n_clusters=n_clusters)
    assert_never(learning_task)
