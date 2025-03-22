from __future__ import annotations

import sys
from typing import Literal
from typing_extensions import assert_never

import numpy as np
from holisticai.robustness.metrics import adversarial_accuracy, empirical_robustness
from typing_extensions import get_args

from holisticai_sdk.engine.definitions import LearningMetric, LearningTask, Target


binary_classification_metric_ids = Literal[
    "zoo_adversarial_accuracy",
    "zoo_empirical_robustness",
    "hsj_adversarial_accuracy",
    "hsj_empirical_robustness",
]

multi_classification_metric_ids = Literal[
    "zoo_adversarial_accuracy",
    "zoo_empirical_robustness",
    "hsj_adversarial_accuracy",
    "hsj_empirical_robustness",
]

regression_metric_ids = Literal[None]

RobustnessmetricsIds = binary_classification_metric_ids | multi_classification_metric_ids

def metrics_mapping(metric_name: RobustnessmetricsIds) -> LearningMetric:
    match metric_name:
        case "hsj_adversarial_accuracy": 
            return LearningMetric(
                name="HSJ Adversarial Accuracy",
                target=Target(range=None, value=1),
                fn=lambda entry: adversarial_accuracy(
                    y_adv_pred=np.array(entry.hsj_attacks_data.y_adv_pred),
                    y_pred=np.array(entry.y_pred_test),
                    y=np.array(entry.y_test),
                ),
                entry_params=["hsj_attacks_data", "y_pred_test", "y_test"],
                cost_fn=lambda value: abs(1 - value),
            )
        case "hsj_empirical_robustness": 
            return LearningMetric(
                name="HSJ Empirical Robustness",
                target=Target(range=None, value=sys.float_info.max),
                fn=lambda entry: empirical_robustness(
                    adv_x=np.array(entry.hsj_attacks_data.adv_x),
                    norm=2,
                    y_adv_pred=np.array(entry.hsj_attacks_data.y_adv_pred),
                    y_pred=np.array(entry.y_pred_test),
                    x=np.array(entry.x_test),
                ),
                entry_params=["hsj_attacks_data", "y_pred_test", "x_test"],
                cost_fn=lambda value: abs(value),
            )
        case "zoo_adversarial_accuracy": 
            return LearningMetric(
                name="Zoo Adversarial Accuracy",
                target=Target(range=None, value=1),
                fn=lambda entry: adversarial_accuracy(
                    y_adv_pred=np.array(entry.zoo_attacks_data.y_adv_pred),
                    y_pred=np.array(entry.y_pred_test),
                    y=np.array(entry.y_test),
                ),
                entry_params=["zoo_attacks_data", "y_pred_test", "y_test"],
                cost_fn=lambda value: abs(1 - value),
            )
        case "zoo_empirical_robustness": 
            return LearningMetric(
            name="Zoo Empirical Robustness",
            target=Target(range=None, value=sys.float_info.max),
            fn=lambda entry: empirical_robustness(
                adv_x=np.array(entry.zoo_attacks_data.adv_x),
                norm=2,
                y_adv_pred=np.array(entry.zoo_attacks_data.y_adv_pred),
                y_pred=np.array(entry.y_pred_test),
                x=np.array(entry.x_test),
            ),
            entry_params=["zoo_attacks_data", "y_pred_test", "x_test"],
            cost_fn=lambda value: abs(value),
        )

def get_metrics_names(learning_task: LearningTask) -> list[RobustnessmetricsIds]:
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