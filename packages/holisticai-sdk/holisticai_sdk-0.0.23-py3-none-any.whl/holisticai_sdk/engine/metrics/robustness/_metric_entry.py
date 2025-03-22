from __future__ import annotations

from typing import TYPE_CHECKING, Optional

import numpy as np
from holisticai.robustness.attackers import HopSkipJump, ZooAttack
from holisticai_sdk.engine.metrics.utils import convert_to_holisticai_proxy
from holisticai_sdk.engine.definitions import (
    RobustnessMetricEntry,
    AdversarialAttackerOutput,
    DatasetTypes,
    HAIModel,
    LearningMetric,
    MetricEntry,
    RobustnessSettings
)

if TYPE_CHECKING:
    import pandas as pd


def __get_zoo_attack_data(model: HAIModel, x: pd.DataFrame):
    proxy = convert_to_holisticai_proxy(model)
    attacker = ZooAttack(proxy=proxy)

    adv_x = attacker.generate(x_df=x)
    y_adv_pred = model.predict(adv_x)
    return AdversarialAttackerOutput(attacker_name="Zoo", y_adv_pred=y_adv_pred, adv_x=adv_x)


def __get_hsj_attack_data(model: HAIModel, x: pd.DataFrame, attributes_attack: Optional[list[str]] = None):
    proxy = convert_to_holisticai_proxy(model)
    attacker = HopSkipJump(predictor=proxy.predict)

    if attributes_attack is not None:
        column_names = list(x.columns)
        mask = np.ones(shape=(len(column_names),))
        for attribute_attack in attributes_attack:
            mask[column_names.index(attribute_attack)] = 0

        adv_x = attacker.generate(x_df=x, mask=mask)
    else:
        adv_x = attacker.generate(x_df=x)
    y_adv_pred = model.predict(adv_x)
    return AdversarialAttackerOutput(attacker_name="HSJ", y_adv_pred=y_adv_pred, adv_x=adv_x)


def get_entry_param(entry_param: str, model: HAIModel, test: DatasetTypes, settings: RobustnessSettings):
    match test.learning_task:
        case "binary_classification"| "multi_classification"| "regression":
            match entry_param:
                case "x_test":
                    return test.X
                case "y_test":
                    return test.y_true
                case "y_pred_test":
                    return model.predict(test.X)

    match test.learning_task:
        case "binary_classification"| "multi_classification":
            match entry_param:
                case "zoo_attacks_data":
                    if not hasattr(model,'predict_proba'):
                        return None
                    return __get_zoo_attack_data(model, test.X)
                case "hsj_attacks_data" if settings.attack_attributes is not None:
                    return __get_hsj_attack_data(model, test.X, settings.attack_attributes)
                case "hsj_attacks_data" if settings.attack_attributes is None:
                    return __get_hsj_attack_data(model, test.X)
    
    raise NotImplementedError


def get_metric_entry(model: HAIModel, test: DatasetTypes, learning_metrics: list[LearningMetric], settings: RobustnessSettings)->RobustnessMetricEntry:
    obj = {param:get_entry_param(param, model, test, settings) for metric in learning_metrics for param in metric.entry_params}
    return MetricEntry(vertical="robustness", learning_task=model.learning_task, obj=obj)

