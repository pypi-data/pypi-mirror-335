from holisticai_sdk.engine.definitions import (
    HAIModel,
    DatasetTypes,
    SecuritySettings,
    MetricCost
)
from holisticai_sdk.engine.metrics.security._learning_metrics import (
    SecurityMetricsIds, metrics_mapping
)
from holisticai.security.commons import DataMinimizer
from holisticai_sdk.engine.metrics.security._metric_entry import get_metric_entry

def compute_security_cost(
    model: HAIModel,
    train: DatasetTypes,
    test: DatasetTypes,
    settings: SecuritySettings,
    data_minimizer: DataMinimizer,
    metric_name: SecurityMetricsIds,
):  
    metric = metrics_mapping(metric_name)
    entry = get_metric_entry(model, train, test, [metric], settings=settings, data_minimizer=data_minimizer)
    try:
        score = metric.fn(entry)
        cost = metric.cost_fn(score)
        return MetricCost(cost_value=cost, metric_value=score)
    except Exception:
        return MetricCost(cost_value=1, metric_value=None)