from __future__ import annotations

from typing import Literal
from typing_extensions import assert_never

import numpy as np
import sklearn.metrics as skmetrics
from sklearn.metrics import mean_squared_error
from typing_extensions import get_args


from holisticai_sdk.engine.definitions import LearningMetric, LearningTask, Target

binary_classification_metric_ids = Literal["accuracy_score", "f1_score", "brier_score_loss", "roc_auc_score"]

regression_metric_ids = Literal["mean_absolute_percentage_error", "mean_squared_error"]

multi_classification_metric_ids = Literal["accuracy_score", "multi_roc_auc_score"]

clustering_metric_ids = Literal["silhouette_score", "calinski_harabasz_score", "davies_bouldin_score"]

EfficacyMetricsIds = (
    regression_metric_ids | binary_classification_metric_ids | multi_classification_metric_ids | clustering_metric_ids
)

def metrics_mapping(metric_name: EfficacyMetricsIds) -> LearningMetric:
    match metric_name:
        case "accuracy_score":
            return LearningMetric(
            fn=lambda entry: skmetrics.accuracy_score(y_true=entry.y_true, y_pred=entry.y_pred),
            entry_params=["y_true", "y_pred"],
            name="Accuracy Score",
            target=Target(range=None, value=1),
            cost_fn=lambda value: abs(1 - value),
        )
        case "f1_score": 
            return LearningMetric(
            fn=lambda entry: skmetrics.f1_score(y_true=entry.y_true, y_pred=entry.y_pred),
            entry_params=["y_true", "y_pred"],
            name="F1 Score",
            target=Target(range=None, value=1),
            cost_fn=lambda value: 1 - value,
        )
        case "brier_score_loss": 
            def brier_score_loss(y_true, y_prob):
                from packaging.version import Version
                import sklearn
                if Version(sklearn.__version__) >= Version("1.7"):
                    return skmetrics.brier_score_loss(y_true=y_true, y_proba=y_prob)
                else:
                    return skmetrics.brier_score_loss(y_true=y_true, y_prob=y_prob)

            return LearningMetric(
            fn=lambda entry: float(brier_score_loss(y_true=entry.y_true, y_prob=entry.y_prob)),
            entry_params=["y_true", "y_prob"],
            name="Brier Score Loss",
            target=Target(range=None, value=0),
            cost_fn=lambda value: abs(value),
        )
        case "roc_auc_score": 
            return LearningMetric(
            fn=lambda entry: float(skmetrics.roc_auc_score(y_true=entry.y_true, y_score=entry.y_prob, multi_class="raise")),
            entry_params=["y_true", "y_prob"],
            name="ROC AUC",
            target=Target(range=None, value=1),
            cost_fn=lambda value: 1 - value,
        )
        case "mean_absolute_percentage_error": 
            return LearningMetric(
            fn=lambda entry: skmetrics.mean_absolute_percentage_error(entry.y_true, entry.y_pred),
            entry_params=["y_true", "y_pred"],
            name="Mean Absolute Percentage Error",
            target=Target(range=None, value=1),
            cost_fn=lambda value: abs(value),
        )
        case "multi_roc_auc_score": 
            return LearningMetric(
            fn=lambda entry: float(skmetrics.roc_auc_score(y_true=entry.y_true, y_score=entry.y_prob, multi_class="ovr")),
            entry_params=["y_true", "y_prob"],
            name="ROC AUC",
            target=Target(range=None, value=1),
            cost_fn=lambda value: abs(value),
        )
        case "mean_squared_error": 
            return LearningMetric(
            fn=lambda entry: np.sqrt(mean_squared_error(entry.y_true, entry.y_pred)),
            entry_params=["y_true", "y_pred"],
            name="Root Mean Squared Error",
            target=Target(range=None, value=0),
            cost_fn=lambda value: abs(value),
        )
        case "silhouette_score":
            return LearningMetric(
            fn=lambda entry: skmetrics.silhouette_score(X=entry.x, labels=entry.y_pred),
            entry_params=["x", "y_pred"],
            name="Silhouette Score",
            target=Target(range=None, value=1),
            cost_fn=lambda value: abs(value),
        )
        case "calinski_harabasz_score": 
            return LearningMetric(
            fn=lambda entry: skmetrics.calinski_harabasz_score(X=entry.x, labels=entry.y_pred),
            entry_params=["x", "y_pred"],
            name="Calinski Harabasz Score",
            target=Target(range=None, value=1),
            cost_fn=lambda value: abs(value),
        )
        case "davies_bouldin_score": 
            return LearningMetric(
            fn=lambda entry: skmetrics.davies_bouldin_score(X=entry.x, labels=entry.y_pred),
            entry_params=["x", "y_pred"],
            name="Davies Bouldin Score",
            target=Target(range=None, value=1),
            cost_fn=lambda value: abs(value),
        )
    assert_never(metric_name)


def get_metrics_names(learning_task: LearningTask) -> list[EfficacyMetricsIds]:
    match learning_task:
        case "binary_classification":
            return list(get_args(binary_classification_metric_ids))
        case "multi_classification":
            return list(get_args(multi_classification_metric_ids))
        case "regression":
            return list(get_args(regression_metric_ids))
        case "clustering":
            return list(get_args(clustering_metric_ids))
    assert_never(learning_task)