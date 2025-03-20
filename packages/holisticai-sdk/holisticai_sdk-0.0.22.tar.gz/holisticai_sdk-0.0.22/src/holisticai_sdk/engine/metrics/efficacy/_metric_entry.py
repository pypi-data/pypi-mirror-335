from __future__ import annotations

from holisticai_sdk.engine.definitions import (
    EfficacyMetricEntry,
    MetricEntry,
    DatasetTypes,
    HAIModel,
    LearningMetric
)
from holisticai_sdk.engine.models import predict_proba


def get_metric_entry(model: HAIModel, test: DatasetTypes, learning_metrics: list[LearningMetric])->EfficacyMetricEntry:
    obj = {param:get_entry_param(param, model, test) for metric in learning_metrics for param in metric.entry_params}
    return MetricEntry(vertical="efficacy", learning_task=model.learning_task, obj=obj)


def get_entry_param(param:str, model: HAIModel, test: DatasetTypes):
    match param:
        case "y_true":
            return getattr(test, param)
        case "y_pred":
            return model.predict(test.X)
        case "y_prob":
            return predict_proba(model, test.X)
        case "x":
            return test.X
        case _:
            raise NotImplementedError(f"{param} not implemented")   


