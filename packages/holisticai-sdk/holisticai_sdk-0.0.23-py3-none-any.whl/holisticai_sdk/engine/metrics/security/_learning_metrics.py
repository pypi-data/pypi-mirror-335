from __future__ import annotations

from typing import Literal
from typing_extensions import assert_never
from holisticai.security.metrics import (
    attribute_attack_score,
    data_minimization_score,
    shapr_score,
)
from typing_extensions import get_args

from holisticai_sdk.engine.definitions import LearningMetric, LearningTask, Target

binary_classification_metric_ids = Literal["shapr_score", "data_minimization_score", "attribute_attack_score"]
regression_metric_ids = Literal["data_minimization_score", "attribute_attack_score"]
multi_classification_metric_ids = Literal["shapr_score", "data_minimization_score", "attribute_attack_score"]

SecurityMetricsIds = binary_classification_metric_ids | regression_metric_ids | multi_classification_metric_ids

def metrics_mapping(metric_name:SecurityMetricsIds) -> LearningMetric:
    match metric_name:
        case "shapr_score": 
            return LearningMetric(
            name="SHAPr Score",
            fn=lambda e: shapr_score(e.y_train, e.y_test, e.y_pred_train, e.y_pred_test, batch_size=32, train_size=0.5),
            entry_params=["y_train", "y_test", "y_pred_train", "y_pred_test"],
            target=Target(range=None, value=1),
            cost_fn=lambda value: abs(value)
        )
        case "data_minimization_score": 
            return LearningMetric(
            name="Data Minimization Score",
            fn=lambda e: data_minimization_score(e.y_test, e.y_pred_test, e.y_pred_test_dm),
            entry_params=["y_test", "y_pred_test", "y_pred_test_dm"],
            target=Target(range=None, value=0),
            cost_fn=lambda value: abs(value),
        )
        case "attribute_attack_score": 
            return LearningMetric(
            name="Attribute Attack Score",
            fn=lambda e: attribute_attack_score(x_train=e.x_train, x_test=e.x_test, y_train=e.y_train, y_test=e.y_test, attribute_attack=e.attack_attribute),
            entry_params=["x_train", "x_test", "y_train", "y_test", "attack_attribute"],
            target=Target(range=None, value=1),
            cost_fn=lambda value: abs(value),
        )
    assert_never(metric_name)


def get_metrics_names(learning_task: LearningTask) -> list[SecurityMetricsIds]:
    match learning_task:
        case "binary_classification":
            return list(get_args(binary_classification_metric_ids))
        case "multi_classification":
            return list(get_args(multi_classification_metric_ids))
        case "regression":
            return list(get_args(regression_metric_ids))
        case "clustering":
            raise 
    assert_never(learning_task)