from __future__ import annotations

from typing import Literal
from typing_extensions import assert_never
import holisticai.bias.metrics as haimetrics
from typing_extensions import get_args

from holisticai_sdk.engine.definitions import LearningMetric, LearningTask, Target

binary_classification_metric_ids = Literal[
    "average_odds_diff",
    "statistical_parity",
    "disparate_impact",
    "four_fifths",
    "cohen_d",
    "z_test_diff",
    "z_test_ratio",
    "equal_opportunity_diff",
]

regression_metric_ids = Literal[
    "disparate_impact_regression",
    "statistical_parity_regression",
    "avg_score_diff",
    "avg_score_ratio",
    "statistical_parity_auc",
    "correlation_diff",
    "rmse_ratio",
    "rmse_ratio_q80",
    "mae_ratio",
    "mae_ratio_q80",
]

multi_classification_metric_ids = Literal[
    "multiclass_equality_of_opp",
    "multiclass_average_odds",
    "multiclass_statistical_parity",
]
clustering_metric_ids = Literal[
    "cluster_balance",
    "min_cluster_ratio",
    "cluster_dist_l1",
    "cluster_dist_kl",
    "silhouette_diff",
]

BiasMetricsIds = (
    regression_metric_ids | binary_classification_metric_ids | multi_classification_metric_ids | clustering_metric_ids
)

def metrics_mapping(metric_name: BiasMetricsIds)-> LearningMetric:
    match metric_name:
        case "multiclass_average_odds": 
            return LearningMetric(
            fn=lambda entry: haimetrics.multiclass_average_odds(entry.group_a, entry.y_pred, entry.y_true),
            entry_params = ["group_a", "y_pred", "y_true"],
            name="Statistical Parity",
            target=Target(range=(-0.1, 0.1), value=0),
            cost_fn=lambda value: abs(value)
        )
        case "multiclass_statistical_parity": 
            return LearningMetric(
            fn=lambda entry: haimetrics.multiclass_statistical_parity(entry.group_a, entry.y_pred),
            entry_params = ["group_a", "y_pred"],
            name="Statistical Parity",
            target=Target(range=(-0.1, 0.1), value=0),
            cost_fn=lambda value: abs(value),
        )
        case "statistical_parity": 
            return LearningMetric(
            fn=lambda entry: haimetrics.statistical_parity(entry.group_a, entry.group_b, entry.y_pred),
            entry_params = ["group_a", "group_b", "y_pred"],
            name="Statistical Parity",
            target=Target(range=(-0.1, 0.1), value=0),
            cost_fn=lambda value: abs(value),
        )
        case "statistical_parity_regression": 
            return LearningMetric(
            fn=lambda entry: haimetrics.statistical_parity_regression(entry.group_a, entry.group_b, entry.y_pred),
            entry_params=["group_a", "group_b", "y_pred"],
            name="Statistical Parity Q50",
            target=Target(range=(0.8, 1.2), value=1),
            cost_fn=lambda value: abs(1 - value),
        )
        case "statistical_parity_auc": 
            return LearningMetric(
            fn=lambda entry: haimetrics.statistical_parity_auc(entry.group_a, entry.group_b, entry.y_pred),
            entry_params=["group_a", "group_b", "y_pred"],
            name="Statistical parity (AUC)",
            target=Target(range=(0, 0.075), value=0),
            cost_fn=lambda value: abs(0 - value),
        )
        case "correlation_diff": 
            return LearningMetric(
            fn=lambda entry: haimetrics.correlation_diff(entry.group_a, entry.group_b, entry.y_pred, entry.y_true),
            entry_params=["group_a", "group_b", "y_pred", "y_true"],
            name="Correlation difference",
            target=Target(range=None, value=0),
            cost_fn=lambda value: abs(0 - value),
        )
        case "disparate_impact": 
            return LearningMetric(
            fn=lambda entry: haimetrics.disparate_impact(group_a=entry.group_a, group_b=entry.group_b, y_pred=entry.y_pred),
            entry_params=["group_a", "group_b", "y_pred"],
            name="Disparate Impact",
            target=Target(range=(0.8, 1.2), value=1),
            cost_fn=lambda value: abs(1 - value),
        )
        case "avg_score_diff": 
            return LearningMetric(
            fn=lambda entry: haimetrics.avg_score_diff(entry.group_a, entry.group_b, entry.y_pred),
            entry_params=["group_a", "group_b", "y_pred"],
            name="Average Score Difference",
            target=Target(range=None, value=0),
            cost_fn=lambda value: abs(value),
        )
        case "avg_score_ratio": 
            return LearningMetric(
            fn=lambda entry: haimetrics.avg_score_ratio(entry.group_a, entry.group_b, entry.y_pred),
            entry_params=["group_a", "group_b", "y_pred"],
            name="Average Score Ratio",
            target=Target(range=None, value=1),
            cost_fn=lambda value: abs(1 - value),
        )
        case "four_fifths": 
            return LearningMetric(
            fn=lambda entry: haimetrics.four_fifths(entry.group_a, entry.group_b, entry.y_pred),
            entry_params=["group_a", "group_b", "y_pred"],
            name="Four Fifths",
            target=Target(range=(0.8, 1), value=1),
            cost_fn=lambda value: abs(1 - value),
        )
        case "cohen_d": 
            return LearningMetric(
            fn=lambda entry: haimetrics.cohen_d(entry.group_a, entry.group_b, entry.y_pred),
            entry_params=["group_a", "group_b", "y_pred"],
            name="Cohen D",
            target=Target(range=(-0.2, 0.2), value=0),
            cost_fn=lambda value: abs(value),
        )
        case "z_test_diff": 
            return LearningMetric(
            fn=lambda entry: haimetrics.z_test_diff(entry.group_a, entry.group_b, entry.y_pred),
            entry_params=["group_a", "group_b", "y_pred"],
            name="Z Test (Difference)",
            target=Target(range=(-2, 2), value=0),
            cost_fn=lambda value: abs(value),
        )
        case "z_test_ratio": 
            return LearningMetric(
            fn=lambda entry: haimetrics.z_test_ratio(entry.group_a, entry.group_b, entry.y_pred),
            entry_params=["group_a", "group_b", "y_pred"],
            name="Z Test (Ratio)",
            target=Target(range=(-2, 2), value=0),
            cost_fn=lambda value: abs(value),
        )
        case "rmse_ratio_q80": 
            return LearningMetric(
            fn=lambda entry: haimetrics.rmse_ratio(entry.group_a, entry.group_b, entry.y_pred, entry.y_true, q=0.8),  # type: ignore
            entry_params=["group_a", "group_b", "y_pred", "y_true"],
            name="RMSE ratio Q80",
            target=Target(range=None, value=1),
            cost_fn=lambda value: abs(value),
        )
        case "rmse_ratio": 
            return LearningMetric(
            fn=lambda entry: haimetrics.rmse_ratio(entry.group_a, entry.group_b, entry.y_pred, entry.y_true),
            entry_params=["group_a", "group_b", "y_pred", "y_true"],
            name="RMSE ratio",
            target=Target(range=None, value=1),
            cost_fn=lambda value: abs(value),
        )
        case "mae_ratio_q80": 
            return LearningMetric(
            fn=lambda entry: haimetrics.mae_ratio(entry.group_a, entry.group_b, entry.y_pred, entry.y_true, q=0.8),  # type: ignore
            entry_params=["group_a", "group_b", "y_pred", "y_true"],
            name="MAE ratio Q80",
            target=Target(range=None, value=1),
            cost_fn=lambda value: abs(value),
        )
        case "mae_ratio": 
            return LearningMetric(
            fn=lambda entry: haimetrics.mae_ratio(entry.group_a, entry.group_b, entry.y_pred, entry.y_true),
            entry_params=["group_a", "group_b", "y_pred", "y_true"],
            name="MAE ratio",
            target=Target(range=None, value=1),
            cost_fn=lambda value: abs(value),
        )
        case "equal_opportunity_diff": 
            return LearningMetric(
            fn=lambda entry: haimetrics.equal_opportunity_diff(entry.group_a, entry.group_b, entry.y_pred, entry.y_true),
            entry_params=["group_a", "group_b", "y_pred", "y_true"],
            name="Equality of opportunity difference",
            target=Target(range=None, value=0),
            cost_fn=lambda value: abs(value),
        )
        case "average_odds_diff": 
            return LearningMetric(
            fn=lambda entry: haimetrics.average_odds_diff(group_a=entry.group_a, group_b=entry.group_b, y_pred=entry.y_pred, y_true=entry.y_true),
            entry_params=["group_a", "group_b", "y_pred", "y_true"],
            name="Average Odds Difference",
            target=Target(range=(-0.2, 0.2), value=0),
            cost_fn=lambda value: abs(value),
        )
        case "disparate_impact_regression": 
            return LearningMetric(
            fn=lambda entry: haimetrics.disparate_impact_regression(entry.group_a, entry.group_b, entry.y_pred),
            entry_params=["group_a", "group_b", "y_pred"],
            name="Disparate Impact Regression",
            target=Target(range=(0.8, 1.2), value=1),
            cost_fn=lambda value: abs(1 - value),
        )
        case "multiclass_equality_of_opp": 
            return LearningMetric(
            fn=lambda entry: float(haimetrics.multiclass_equality_of_opp(entry.group_a, entry.y_true, entry.y_pred)),
            entry_params=["group_a", "y_true", "y_pred"],
            name="Multiclass Equality of Opportunity",
            target=Target(range=(-0.1, 0.1), value=0),
            cost_fn=lambda value: abs(value),
        )
        case "cluster_balance": return LearningMetric(
            fn=lambda entry: haimetrics.cluster_balance(group_a=entry.group_a, group_b=entry.group_b, y_pred=entry.y_pred),
            entry_params=["group_a", "group_b", "y_pred"],
            name="Cluster Balance",
            target=Target(range=(0.8, 1), value=1),
            cost_fn=lambda value: abs(value),
        )
        case "min_cluster_ratio": return LearningMetric(
            fn=lambda entry: haimetrics.min_cluster_ratio(group_a=entry.group_a, group_b=entry.group_b, y_pred=entry.y_pred),
            entry_params=["group_a", "group_b", "y_pred"],
            name="Min Cluster Ratio",
            target=Target(range=None, value=0),
            cost_fn=lambda value: abs(value),
        )
        case "cluster_dist_l1":return  LearningMetric(
            fn=lambda entry: haimetrics.cluster_dist_l1(group_a=entry.group_a, group_b=entry.group_b, y_pred=entry.y_pred),
            entry_params=["group_a", "group_b", "y_pred"],
            name="Cluster Distribution Total Variation",
            target=Target(range=(0, 0.2), value=0),
            cost_fn=lambda value: abs(value),
        )
        case "cluster_dist_kl": return LearningMetric(
            fn=lambda entry: haimetrics.cluster_dist_kl(group_a=entry.group_a, group_b=entry.group_b, y_pred=entry.y_pred),
            entry_params=["group_a", "group_b", "y_pred"],
            name="Cluster Distribution KL Div",
            target=Target(range=None, value=0),
            cost_fn=lambda value: abs(value),
        )
        case "silhouette_diff": return LearningMetric(
            fn=lambda entry: haimetrics.silhouette_diff(group_a=entry.group_a, group_b=entry.group_b, data=entry.x, y_pred=entry.y_pred),
            entry_params=["group_a", "group_b", "x", "y_pred"],
            name="Silhouette Diff",
            target=Target(range=(-0.1, 0.1), value=0),
            cost_fn=lambda value: abs(value),
        )
    assert_never(metric_name)


def get_metrics_names(learning_task: LearningTask) -> list[BiasMetricsIds]:
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