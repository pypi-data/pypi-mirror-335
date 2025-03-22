import pandas as pd

from holisticai_sdk.engine.definitions import (
    HAIModel,
    Dataset,
    Metric,
    DatasetTypes,
    VerticalSettings,
    SecuritySettings,
    Bootstrapping
)
from holisticai_sdk.engine.metrics.security._learning_metrics import (
    SecurityMetricsIds, metrics_mapping, get_metrics_names
)

from functools import partial
from holisticai_sdk.engine.metrics.security._metric_entry import get_metric_entry
from holisticai.security.commons import DataMinimizer
from typing import Optional
from holisticai_sdk.engine.models.utils import convert_to_holisticai_proxy

def compute_security_metrics(
    model: HAIModel,
    x_train: pd.DataFrame,
    y_train: pd.Series,
    x_test: pd.DataFrame,
    y_test: pd.Series,
    attack_attribute: str,
    bootstrapping: Bootstrapping|None = None,
):
    match model.learning_task:
        case "clustering":
            raise NotImplementedError
        case _:
            train = Dataset(vertical="security", learning_task=model.learning_task, X=x_train, y_true=y_train)
            test = Dataset(vertical="security", learning_task=model.learning_task, X=x_test, y_true=y_test)
    
    settings = VerticalSettings(vertical="security", attack_attribute=attack_attribute)
    return security_metrics(model, train, test, settings=settings, bootstrapping=bootstrapping)



def security_metrics(
    model: HAIModel,
    train: DatasetTypes,
    test: DatasetTypes,
    settings: SecuritySettings,
    bootstrapping: Optional[Bootstrapping] = None,
    data_minimizer: Optional[DataMinimizer] = None,
    metric_names: Optional[list[SecurityMetricsIds]] = None,
    
):  
    if data_minimizer is None:      
        if train.learning_task == "clustering":
            raise NotImplementedError
        proxy = convert_to_holisticai_proxy(model)
        data_minimizer = DataMinimizer(proxy=proxy, selector_types=["Percentile", "Variance"])
        data_minimizer.fit(train.X, train.y_true)

    if metric_names is None:
        metric_names = get_metrics_names(model.learning_task)

    learning_metrics = [metrics_mapping(metric_name) for metric_name in metric_names]
    _get_metric_entry = partial(get_metric_entry, model=model, learning_metrics=learning_metrics, settings=settings, data_minimizer=data_minimizer, train=train)

    if bootstrapping is None:
        entry = _get_metric_entry(test=test)
        return [Metric(name=metric.name, value=metric.fn(entry), target=metric.target) for metric in learning_metrics]
    return bootstrapping.run(_get_metric_entry, learning_metrics, test)