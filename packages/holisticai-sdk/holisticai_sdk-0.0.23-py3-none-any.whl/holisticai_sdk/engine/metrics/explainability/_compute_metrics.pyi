from typing import overload, Optional

import pandas as pd

from holisticai_sdk.engine.definitions import (
    HAIClustering,
    HAIBinaryClassification,
    HAIMultiClassification,
    HAIRegression,
    HAIModel,
    Metric,
    BootstrapMetric,
    DatasetTypes,
    Bootstrapping
)
from holisticai_sdk.engine.metrics.explainability._learning_metrics import ExplainabilityMetricsIds

# compute_explainability_metrics
@overload
def compute_explainability_metrics(
    model: HAIBinaryClassification | HAIMultiClassification | HAIRegression,
    x: pd.DataFrame,
    y: pd.Series,
    bootstrapping: Bootstrapping,
)-> list[BootstrapMetric]: ...

@overload
def compute_explainability_metrics(
    model: HAIClustering, 
    x: pd.DataFrame, 
    bootstrapping: Bootstrapping
)->list[BootstrapMetric]: ...

@overload
def compute_explainability_metrics(
    model: HAIBinaryClassification | HAIMultiClassification | HAIRegression,
    x: pd.DataFrame,
    y: pd.Series,
)-> list[Metric]: ...

@overload
def compute_explainability_metrics(
    model: HAIClustering,
    x: pd.DataFrame,
)-> list[Metric]: ...


# explainability_metrics
@overload
def explainability_metrics(
    model: HAIModel,
    test: DatasetTypes,
    bootstrapping: Bootstrapping,
    metric_names: Optional[list[ExplainabilityMetricsIds]] = None,
)->list[BootstrapMetric]: ...

@overload
def explainability_metrics(
    model: HAIModel,
    test: DatasetTypes,
    metric_names: Optional[list[ExplainabilityMetricsIds]] = None,
) -> list[Metric]: ...
