from __future__ import annotations

from typing import TYPE_CHECKING, overload, Optional

from holisticai_sdk.engine.definitions import (
    HAIBinaryClassification,
    HAIMultiClassification,
    HAIRegression,
    HAIModel,
    Metric,
    BootstrapMetric,
    DatasetTypes,
    RobustnessSettings,
    Bootstrapping
)
from holisticai_sdk.engine.metrics.robustness._learning_metrics import RobustnessmetricsIds

if TYPE_CHECKING:
    import pandas as pd



@overload
def compute_robustness_metrics(
    model: HAIBinaryClassification | HAIMultiClassification | HAIRegression,
    x: pd.DataFrame,
    y: pd.Series,
    attack_attributes: list[str],
    bootstrapping: Bootstrapping,
)-> list[BootstrapMetric]:...

@overload
def compute_robustness_metrics(
    model: HAIBinaryClassification | HAIMultiClassification | HAIRegression,
    x: pd.DataFrame,
    y: pd.Series,
    attack_attributes: list[str],
)-> list[Metric]:...


@overload
def robustness_metrics(
    model: HAIModel,
    test: DatasetTypes,
    settings: RobustnessSettings,
    metric_names: Optional[list[RobustnessmetricsIds]] = None,
)-> list[Metric]:  ...

@overload
def robustness_metrics(
    model: HAIModel,
    test: DatasetTypes,
    settings: RobustnessSettings,
    bootstrapping: Bootstrapping,
    metric_names: Optional[list[RobustnessmetricsIds]] = None,
)-> list[BootstrapMetric]:  ...