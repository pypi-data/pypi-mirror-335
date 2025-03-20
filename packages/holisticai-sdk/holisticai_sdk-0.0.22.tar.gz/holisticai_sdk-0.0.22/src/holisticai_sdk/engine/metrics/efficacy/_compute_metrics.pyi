from typing import overload, Optional

import pandas as pd

from holisticai_sdk.engine.definitions import (
    HAIClustering,
    HAIBinaryClassification,
    HAIMultiClassification,
    HAIModel,
    HAIRegression,
    BootstrapMetric,
    Metric,
    DatasetTypes,
    Bootstrapping
)

from holisticai_sdk.engine.metrics.efficacy._learning_metrics import (
    EfficacyMetricsIds
)


@overload
def compute_efficacy_metrics(
    model: HAIBinaryClassification | HAIMultiClassification | HAIRegression,
    x: pd.DataFrame,
    y: pd.Series,
    bootstrapping: Bootstrapping,
) -> list[BootstrapMetric]: ...

@overload
def compute_efficacy_metrics(
    model: HAIClustering, 
    x: pd.DataFrame, 
    bootstrapping: Bootstrapping) -> list[BootstrapMetric]: ...

@overload
def compute_efficacy_metrics(
    model: HAIBinaryClassification | HAIMultiClassification | HAIRegression,
    x: pd.DataFrame,
    y: pd.Series,
) -> list[Metric]: ...

@overload
def compute_efficacy_metrics(
    model: HAIClustering, 
    x: pd.DataFrame) -> list[Metric]: ...


@overload
def efficacy_metrics(
    model: HAIModel,
    test: DatasetTypes,
    bootstrapping: Bootstrapping,
    metric_names: Optional[list[EfficacyMetricsIds]] = None,
)-> list[BootstrapMetric]: ...


@overload
def efficacy_metrics(
    model: HAIModel,
    test: DatasetTypes,
    metric_names: Optional[list[EfficacyMetricsIds]] = None,
)-> list[Metric]: ...