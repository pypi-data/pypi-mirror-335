from __future__ import annotations

from holisticai_sdk.engine.definitions import (
    BiasDatasetTypes,
    HAIModel,
    MetricCost
)

from holisticai_sdk.engine.metrics.bias._learning_metrics import (
    BiasMetricsIds, metrics_mapping
)

from holisticai_sdk.engine.metrics.bias._metric_entry import get_metric_entry


def compute_bias_cost(
    model: HAIModel,
    test: BiasDatasetTypes,
    metric_name:BiasMetricsIds
) -> MetricCost:  
    metric = metrics_mapping(metric_name)
    entry = get_metric_entry(model, test, [metric])
    try:
        score = metric.fn(entry)
        cost = metric.cost_fn(score)
        return MetricCost(cost_value=cost, metric_value=score)
    except Exception:
        return MetricCost(cost_value=1, metric_value=None)
