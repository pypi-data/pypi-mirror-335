from __future__ import annotations

import pandas as pd
from holisticai.inspection import (
    compute_surrogate_feature_importance,
    compute_partial_dependence,
    compute_permutation_importance,
    compute_conditional_permutation_importance
)    


from holisticai_sdk.engine.definitions import (
    DatasetTypes,
    ExplainabilityMetricEntry,
    MetricEntry,
    HAIModel,
    LearningMetric
)

from holisticai_sdk.engine.metrics.utils import convert_to_holisticai_proxy


def get_metric_entry(model: HAIModel, test: DatasetTypes, learning_metrics: list[LearningMetric])->ExplainabilityMetricEntry:
    entry_names =[param for metric in learning_metrics for param in metric.entry_params]
    obj = get_entry_params(model, test, entry_names)
    return MetricEntry(vertical="explainability", learning_task=model.learning_task, obj=obj)


def get_entry_params(model: HAIModel, test: DatasetTypes, entry_names: list[str]):
    hai_proxy = convert_to_holisticai_proxy(model)
    entry_kargs = {}

    for param in entry_names:
        if param in entry_kargs:
            continue

        if test.learning_task in ["binary_classification", "multi_classification", "regression"]:
            handle_classification_regression_params(param, test, model, hai_proxy, entry_kargs)
        elif test.learning_task == "clustering":
            raise NotImplementedError("Clustering task not implemented")
    
    return entry_kargs

def handle_classification_regression_params(param, test, model, hai_proxy, entry_kargs):
    match param:
        case "y_true":
            entry_kargs[param] = getattr(test, param)

        case "y_pred":
            entry_kargs[param] = model.predict(test.X)

        case "permutation_importances":
            handle_permutation_importances(test, hai_proxy, entry_kargs)

        case "permutation_conditional_importances":
            entry_kargs[param] = compute_conditional_permutation_importance(
                X=test.X, y=test.y_true, proxy=hai_proxy,
            )

        case "permutation_partial_dependencies":
            handle_permutation_partial_dependencies(test, hai_proxy, entry_kargs)

        case "surrogate_importances":
            entry_kargs[param] = compute_surrogate_feature_importance(
                X=test.X, y=test.y_true, proxy=hai_proxy,
            )

        case "surrogate_conditional_importances":
            entry_kargs[param] = compute_conditional_permutation_importance(
                X=test.X, y=test.y_true, proxy=hai_proxy,
            )

        case "y_surrogate":
            handle_y_surrogate(test, hai_proxy, entry_kargs)
        
        case "y_prob_surrogate":
            handle_y_proba_surrogate(test, hai_proxy, entry_kargs)


def handle_permutation_importances(test, hai_proxy, entry_kargs):
    entry_kargs["permutation_importances"] = compute_permutation_importance(
        X=test.X, y=test.y_true, proxy=hai_proxy,
    )

def handle_permutation_partial_dependencies(test, hai_proxy, entry_kargs):
    if hai_proxy.predict_proba is None:
        return None
        
    if "permutation_importances" not in entry_kargs:
        handle_permutation_importances(test, hai_proxy, entry_kargs)
    
    ranked_importances = entry_kargs["permutation_importances"].top_alpha()
    entry_kargs["permutation_partial_dependencies"] = compute_partial_dependence(
        test.X, features=ranked_importances.feature_names, proxy=hai_proxy
    )

def handle_y_surrogate(test, hai_proxy, entry_kargs):
    if "surrogate_importances" not in entry_kargs:
        entry_kargs["surrogate_importances"] = compute_surrogate_feature_importance(
            X=test.X, y=test.y_true, proxy=hai_proxy,
        )
    
    entry_kargs["y_surrogate"] = pd.Series(
        entry_kargs["surrogate_importances"].extra_attrs["surrogate"].predict(test.X)
    )


def handle_y_proba_surrogate(test, hai_proxy, entry_kargs):
    if "surrogate_importances" not in entry_kargs:
        entry_kargs["surrogate_importances"] = compute_surrogate_feature_importance(
            X=test.X, y=test.y_true, proxy=hai_proxy
        )
    
    entry_kargs["y_prob_surrogate"] = pd.Series(
        entry_kargs["surrogate_importances"].extra_attrs["surrogate"].predict_proba(test.X)[:,1]
    )
