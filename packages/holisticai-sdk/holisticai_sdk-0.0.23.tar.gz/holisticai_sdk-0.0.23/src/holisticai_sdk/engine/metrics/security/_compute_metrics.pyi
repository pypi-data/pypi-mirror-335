import pandas as pd

from holisticai_sdk.engine.definitions import (
    HAIBinaryClassification,
    HAIMultiClassification,
    HAIRegression,
    Metric,
    BootstrapMetric,
    DatasetTypes,
    SecuritySettings,
    HAIModel,
    Bootstrapping
)
from typing import overload, Optional

from holisticai_sdk.engine.metrics.security._learning_metrics import SecurityMetricsIds
from holisticai.security.commons import DataMinimizer

@overload
def compute_security_metrics(
    model: HAIBinaryClassification | HAIMultiClassification | HAIRegression,
    x_train: pd.DataFrame,
    y_train: pd.Series,
    x_test: pd.DataFrame,
    y_test: pd.Series,
    attack_attribute: str,
    bootstrapping: Bootstrapping,
)-> list[BootstrapMetric]: ...
   
@overload
def compute_security_metrics(
    model: HAIBinaryClassification | HAIMultiClassification | HAIRegression,
    x_train: pd.DataFrame,
    y_train: pd.Series,
    x_test: pd.DataFrame,
    y_test: pd.Series,
    attack_attribute: str,
)-> list[Metric]: ...
   
@overload  
def security_metrics(
    model: HAIModel,
    train: DatasetTypes,
    test: DatasetTypes,
    settings: SecuritySettings,
    bootstrapping: Bootstrapping,
    data_minimizer: Optional[DataMinimizer]=None,
    metric_names: Optional[list[SecurityMetricsIds]] = None,
    
)-> list[BootstrapMetric]: ...

@overload  
def security_metrics(
    model: HAIModel,
    train: DatasetTypes,
    test: DatasetTypes,
    settings: SecuritySettings,
    data_minimizer: Optional[DataMinimizer]=None,
    metric_names: Optional[list[SecurityMetricsIds]] = None,
    
)-> list[BootstrapMetric]: ...