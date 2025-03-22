from __future__ import annotations

from functools import partial
from typing import TYPE_CHECKING, Optional

from holisticai_sdk.engine.metrics.robustness._learning_metrics import (
    RobustnessmetricsIds, metrics_mapping, get_metrics_names
)
from holisticai_sdk.engine.definitions import (
    HAIBinaryClassification,
    HAIMultiClassification,
    HAIRegression,
    DatasetTypes,
    Dataset,
    HAIModel,
    Metric,
    RobustnessSettings,
    VerticalSettings,
    Bootstrapping
)
from holisticai_sdk.engine.bootstrap import compute_aggregates_from_bootstrap_metrics
from holisticai_sdk.engine.bootstrap import compute_bootstrap_metrics
from holisticai_sdk.engine.metrics.robustness._metric_entry import get_metric_entry

if TYPE_CHECKING:
    import pandas as pd


def compute_robustness_metrics(
    model: HAIBinaryClassification | HAIMultiClassification | HAIRegression,
    x: pd.DataFrame,
    y: pd.Series,
    attack_attributes: list[str],
    bootstrapping: Bootstrapping|None = None,
):
    test = Dataset(vertical="robustness", learning_task=model.learning_task, X=x, y_true=y)

    settings = VerticalSettings(vertical="robustness", attack_attributes=attack_attributes)
    return robustness_metrics(model, test, settings, bootstrapping)
    

def robustness_metrics(
    model: HAIModel,
    test: DatasetTypes,
    settings: RobustnessSettings,
    bootstrapping: Optional[Bootstrapping] = None,
    metric_names: Optional[list[RobustnessmetricsIds]] = None,
):  

    if metric_names is None:
        metric_names = get_metrics_names(model.learning_task)

    learning_metrics = [metrics_mapping(metric_name) for metric_name in metric_names]
    _get_metric_entry = partial(get_metric_entry, model=model, learning_metrics=learning_metrics, settings=settings)

    if bootstrapping is None:
        entry = _get_metric_entry(test=test)
        return [Metric(name=metric.name, value=metric.fn(entry), target=metric.target) for metric in learning_metrics]
    return compute_bootstrap_metrics(bootstrapping, _get_metric_entry, learning_metrics, test)