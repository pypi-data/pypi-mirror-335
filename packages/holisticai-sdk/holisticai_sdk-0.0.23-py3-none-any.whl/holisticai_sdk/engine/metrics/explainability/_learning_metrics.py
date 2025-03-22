from __future__ import annotations

from typing import Literal
from typing_extensions import assert_never

from holisticai.explainability.metrics import (  # type: ignore
    alpha_score,

    position_parity,
    rank_alignment,
    surrogate_accuracy_score,
    surrogate_mean_squared_error_degradation,
    xai_ease_score,
    spread_divergence,
    spread_ratio
)

from typing_extensions import get_args

from holisticai_sdk.engine.definitions import LearningMetric, LearningTask, Target
import sklearn.metrics as skmetrics

binary_classification_pred_metric_ids = Literal["position_parity", "rank_alignment", "alpha_score", "spread_divergence", "spread_ratio"]
binary_classification_prob_metric_ids = Literal["xai_ease_score"]
binary_classification_surrogate_metric_ids = Literal["surrogate_accuracy", "surrogate_brier_score_loss"]
binary_classification_metric_ids = Literal[
    binary_classification_pred_metric_ids,
    binary_classification_prob_metric_ids,
    binary_classification_surrogate_metric_ids,
]


regression_pred_metric_ids = Literal["position_parity", "rank_alignment", "xai_ease_score", "spread_divergence", "spread_ratio"]
regression_surrogate_metric_ids = Literal["surrogate_mean_squared_error"]
regression_metric_ids = Literal[regression_pred_metric_ids, regression_surrogate_metric_ids]

multi_classification_pred_metric_ids = Literal["position_parity", "rank_alignment", "alpha_score", "spread_divergence", "spread_ratio"]
multi_classification_prob_metric_ids = Literal["xai_ease_score"]
multi_classification_surrogate_metric_ids = Literal["surrogate_accuracy"]
multi_classification_metric_ids = Literal[
    multi_classification_pred_metric_ids,
    multi_classification_prob_metric_ids,
    multi_classification_surrogate_metric_ids,
]

ExplainabilityMetricsIds = binary_classification_metric_ids | regression_metric_ids | multi_classification_metric_ids

def metrics_mapping(metric_name: ExplainabilityMetricsIds) -> LearningMetric:
    match metric_name:
        case "surrogate_brier_score_loss": 
            return LearningMetric(
            fn=lambda e: float(skmetrics.brier_score_loss(y_true=e.y_pred, y_prob=e.y_prob_surrogate)),
            entry_params=["y_pred", "y_prob_surrogate"],
            name="Brier Score Loss",
            target=Target(range=None, value=0),
            cost_fn=lambda value: abs(value),
        )
        case "surrogate_accuracy": 
            return LearningMetric(
                name="Surrogate Accuracy",
                fn=lambda e: surrogate_accuracy_score(y_pred=e.y_pred, y_surrogate=e.y_surrogate),
                entry_params=["y_pred", "y_surrogate"],
                target=Target(range=None, value=1),
                cost_fn=lambda value: 1 - value,
            )
        case "alpha_score":
            return LearningMetric(
                name="Alpha Score",
                fn=lambda e: alpha_score(feature_importance=e.permutation_importances),
                entry_params=["permutation_importances"],
                target=Target(range=None, value=1),
                cost_fn=lambda value: abs(value),
            )
        case "surrogate_mean_squared_error": 
            return LearningMetric(
                name="Surrogate MSE",
                fn=lambda e: surrogate_mean_squared_error_degradation(y=e.y, y_pred=e.y_pred, y_surrogate=e.y_surrogate),
                entry_params=["y", "y_pred", "y_surrogate"],
                target=Target(range=None, value=0),
                cost_fn=lambda value: abs(0 - value),

            )
        case "position_parity": 
            return LearningMetric(
                name="Position Parity",
                fn=lambda e: position_parity(
                    conditional_feature_importance=e.permutation_conditional_importances,
                    ranked_feature_importance=e.permutation_importances,
                ),
                entry_params=["permutation_conditional_importances", "permutation_importances"],
                target=Target(range=None, value=1),
                cost_fn=lambda value: abs(1 - value),
            )
        case "rank_alignment": 
            return LearningMetric(
                name="Rank Alignment",
                fn=lambda e: rank_alignment(
                    conditional_feature_importance=e.permutation_conditional_importances,
                    ranked_feature_importance=e.permutation_importances,
                ),
                entry_params=["permutation_conditional_importances", "permutation_importances"],
                target=Target(range=None, value=1),
                cost_fn=lambda value: abs(1 - value),
        )
        case "xai_ease_score": 
            return LearningMetric(
                name="Explainability Ease",
                fn=lambda e: xai_ease_score(
                    partial_dependence=e.permutation_partial_dependencies,
                    ranked_feature_importance=e.permutation_importances.top_alpha(),
                ),
                entry_params=["permutation_partial_dependencies", "permutation_importances"],
                target=Target(range=None, value=1),
                cost_fn=lambda value: abs(1 - value),
            )
        case "spread_divergence": 
            return LearningMetric(
                name="Spread Divergence",
                fn=lambda e: spread_divergence(
                    feature_importance=e.permutation_importances,
                ),
                entry_params=["permutation_importances"],
                target=Target(range=None, value=1),
                cost_fn=lambda value: abs(1 - value),
            )
        case "spread_ratio": 
            return LearningMetric(
                name="Spread Ratio",
                fn=lambda e: spread_ratio(
                    feature_importance=e.permutation_importances,
                ),
                entry_params=["permutation_importances"],
                target=Target(range=None, value=1),
                cost_fn=lambda value: abs(1 - value),
            )
    assert_never(metric_name)



def get_metrics_names(learning_task: LearningTask) -> list[ExplainabilityMetricsIds]:
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