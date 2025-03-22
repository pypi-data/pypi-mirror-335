from __future__ import annotations

from holisticai_sdk.engine.definitions import (
    DatasetTypes,
    HAIModel,
    MetricCost
)

from holisticai_sdk.engine.metrics.efficacy._learning_metrics import (
    EfficacyMetricsIds, metrics_mapping
)

from holisticai_sdk.engine.metrics.efficacy._metric_entry import get_metric_entry


def compute_efficacy_cost(
    model: HAIModel,
    test: DatasetTypes,
    metric_name: EfficacyMetricsIds
) -> MetricCost:  
    metric = metrics_mapping(metric_name)
    entry = get_metric_entry(model, test, [metric])
    try:
        score = metric.fn(entry)
        cost = metric.cost_fn(score)
        return MetricCost(cost_value=cost, metric_value=score)
    except Exception:
        return MetricCost(cost_value=1, metric_value=None)