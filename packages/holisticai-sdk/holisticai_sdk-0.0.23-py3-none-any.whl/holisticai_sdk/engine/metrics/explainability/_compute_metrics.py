from __future__ import annotations

from functools import partial
from typing import Optional
import pandas as pd

from holisticai_sdk.engine.definitions import (
    Dataset,
    HAIModel,
    Metric,
    DatasetTypes,
    Bootstrapping
)
from holisticai_sdk.engine.metrics.explainability._learning_metrics import (
    ExplainabilityMetricsIds, metrics_mapping, get_metrics_names
)
from holisticai_sdk.engine.metrics.explainability._metric_entry import get_metric_entry
from holisticai_sdk.engine.bootstrap import compute_bootstrap_metrics

def compute_explainability_metrics(
    model: HAIModel,
    x: pd.DataFrame,
    y: pd.Series | None = None,
    bootstrapping: Bootstrapping | None = None,
):  
    match model.learning_task:
        case "clustering":
            test = Dataset(vertical="explainability", learning_task=model.learning_task, X=x)
        case _ if y is not None:
            test = Dataset(vertical="explainability", learning_task=model.learning_task, X=x, y_true=y)
        case _:
            raise NotImplementedError
    
    return explainability_metrics(model, test, bootstrapping=bootstrapping)


def explainability_metrics(
    model: HAIModel,
    test: DatasetTypes,
    bootstrapping: Optional[Bootstrapping] = None,
    metric_names: Optional[list[ExplainabilityMetricsIds]] = None,
):  
    if metric_names is None:
        metric_names = get_metrics_names(model.learning_task)
    learning_metrics = [metrics_mapping(metric_name) for metric_name in metric_names]
    _get_metric_entry = partial(get_metric_entry, model=model, learning_metrics=learning_metrics)

    if bootstrapping is None:
        entry = _get_metric_entry(test=test)
        return [Metric(name=metric.name, value=metric.fn(entry), target=metric.target) for metric in learning_metrics]
    return compute_bootstrap_metrics(bootstrapping, _get_metric_entry, learning_metrics, test)