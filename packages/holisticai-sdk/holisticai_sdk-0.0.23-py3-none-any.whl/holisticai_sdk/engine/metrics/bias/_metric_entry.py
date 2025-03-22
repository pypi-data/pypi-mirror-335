from __future__ import annotations

from holisticai_sdk.engine.definitions import (
    BiasMetricEntry,
    MetricEntry,
    BiasDatasetTypes,
    HAIModel,
    LearningMetric
)



def get_metric_entry(model: HAIModel, test: BiasDatasetTypes, learning_metrics: list[LearningMetric])->BiasMetricEntry:
    obj = {param:get_entry_param(param, model, test) for metric in learning_metrics for param in metric.entry_params}
    return MetricEntry(vertical="bias", learning_task=model.learning_task, obj=obj)


def get_entry_param(param:str, model: HAIModel, test: BiasDatasetTypes):
    match param:
        case "y_true"| "group_a"| "group_b":
            return getattr(test, param)
        case "y_pred":
            return model.predict(test.X)
        case "x":
            return test.X
        case _:
            raise NotImplementedError(f"{param} is not a valid entry parameter for bias metrics")
