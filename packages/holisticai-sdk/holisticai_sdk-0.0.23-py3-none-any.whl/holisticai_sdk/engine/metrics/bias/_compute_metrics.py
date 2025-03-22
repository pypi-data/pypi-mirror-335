from __future__ import annotations

from functools import partial
from typing import TYPE_CHECKING, Optional

from holisticai_sdk.engine.definitions import (
    Dataset,
    HAIModel,
    Metric,
    BiasDatasetTypes,
    Bootstrapping
)

from holisticai_sdk.engine.bootstrap import compute_bootstrap_metrics
from holisticai_sdk.engine.metrics.bias._learning_metrics import (
    metrics_mapping, BiasMetricsIds, get_metrics_names
)

from holisticai_sdk.engine.metrics.bias._metric_entry import get_metric_entry

if TYPE_CHECKING:
    import pandas as pd


def compute_bias_metrics(
    model: HAIModel,
    x: pd.DataFrame,
    group_a: pd.Series,
    group_b: pd.Series,
    y: pd.Series | None = None,
    bootstrapping: Bootstrapping | None = None,
):  
    match model.learning_task:
        case "clustering":
            test = Dataset(vertical="bias", learning_task=model.learning_task, X=x, group_a=group_a, group_b=group_b)
        case _ if y is not None:
            test = Dataset(vertical="bias", learning_task=model.learning_task, X=x, y_true=y, group_a=group_a, group_b=group_b)
        case _:
            raise NotImplementedError

    return bias_metrics(model, test, bootstrapping=bootstrapping)

def bias_metrics(
    model: HAIModel,
    test: BiasDatasetTypes,
    bootstrapping: Optional[Bootstrapping] = None,
    metric_names: Optional[list[BiasMetricsIds]] =None,
):  
    if metric_names is None:
        metric_names = get_metrics_names(model.learning_task)
    learning_metrics = [metrics_mapping(metric_name) for metric_name in metric_names]
    _get_metric_entry = partial(get_metric_entry, model=model, learning_metrics=learning_metrics)

    if bootstrapping is None:
        entry = _get_metric_entry(test=test)
        return [Metric(name=metric.name, value=metric.fn(entry), target=metric.target) for metric in learning_metrics]
    return compute_bootstrap_metrics(bootstrapping, _get_metric_entry, learning_metrics, test)