from typing import overload

import pandas as pd

from holisticai_sdk.engine.definitions import (
    HAIClustering,
    HAIBinaryClassification,
    HAIMultiClassification,
    HAIRegression,
    HAIModel,
    BootstrapMetric,
    Metric,
    BiasDatasetTypes,
    Bootstrapping
)
from holisticai_sdk.engine.metrics.bias._learning_metrics import (
    BiasMetricsIds
)
from typing import Optional

@overload
def compute_bias_metrics(
    model: HAIBinaryClassification | HAIMultiClassification | HAIRegression,
    x: pd.DataFrame,
    group_a: pd.Series,
    group_b: pd.Series,
    y: pd.Series,
    bootstrapping: Bootstrapping,
)-> list[BootstrapMetric]: ...

@overload
def compute_bias_metrics(
    model: HAIClustering,
    x: pd.DataFrame,
    group_a: pd.Series,
    group_b: pd.Series,
    bootstrapping: Bootstrapping,
)-> list[BootstrapMetric]: ...

@overload
def compute_bias_metrics(
    model: HAIBinaryClassification | HAIMultiClassification | HAIRegression,
    x: pd.DataFrame,
    group_a: pd.Series,
    group_b: pd.Series,
    y: pd.Series,
)-> list[Metric]: ...

@overload
def compute_bias_metrics(
    model: HAIClustering,
    x: pd.DataFrame,
    group_a: pd.Series,
    group_b: pd.Series,
)-> list[Metric]: ...


@overload
def bias_metrics(
    model: HAIModel,
    test: BiasDatasetTypes,
    bootstrapping: Bootstrapping,
    metric_names: Optional[list[BiasMetricsIds]] = None,
)-> list[BootstrapMetric]: ...


@overload
def bias_metrics(
    model: HAIModel,
    test: BiasDatasetTypes,
    metric_names: Optional[list[BiasMetricsIds]] = None,
)-> list[Metric]: ...

