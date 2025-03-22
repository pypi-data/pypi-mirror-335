from holisticai_sdk.engine.definitions._base import Vertical, LearningTask
from holisticai_sdk.engine.definitions._metric_entries import (
    BinaryClassificationBiasMetricEntry, 
    BinaryClassificationEfficacyMetricEntry, 
    BinaryClassificationExplainabilityMetricEntry, 
    BinaryClassificationRobustnessMetricEntry, 
    BinaryClassificationSecurityMetricEntry, 
    RegressionBiasMetricEntry, 
    RegressionEfficacyMetricEntry,
    RegressionExplainabilityMetricEntry,
    RegressionRobustnessMetricEntry,
    RegressionSecurityMetricEntry,
    MultiClassificationBiasMetricEntry,
    MultiClassificationEfficacyMetricEntry,
    MultiClassificationExplainabilityMetricEntry,
    MultiClassificationRobustnessMetricEntry,
    MultiClassificationSecurityMetricEntry,
    ClusteringEfficacyMetricEntry,
    ClusteringBiasMetricEntry,
    ClusteringExplainabilityMetricEntry
)

def MetricEntry(vertical: Vertical, learning_task: LearningTask, obj: dict):
    match vertical:
        case "efficacy":
            match learning_task:
                case "binary_classification":
                    return BinaryClassificationEfficacyMetricEntry(**obj)
                case "multi_classification":
                    return MultiClassificationEfficacyMetricEntry(**obj)
                case "regression":
                    return RegressionEfficacyMetricEntry(**obj)
                case "clustering":
                    return ClusteringEfficacyMetricEntry(**obj)
        case "bias":
            match learning_task:
                case "binary_classification":
                    return BinaryClassificationBiasMetricEntry(**obj)
                case "multi_classification":
                    return MultiClassificationBiasMetricEntry(**obj)
                case "regression":
                    return RegressionBiasMetricEntry(**obj)
                case "clustering":
                    return ClusteringBiasMetricEntry(**obj)
        case "explainability":
            match learning_task:
                case "binary_classification":
                    return BinaryClassificationExplainabilityMetricEntry(**obj)
                case "multi_classification":
                    return MultiClassificationExplainabilityMetricEntry(**obj)
                case "regression":
                    return RegressionExplainabilityMetricEntry(**obj)
                case "clustering":
                    return ClusteringExplainabilityMetricEntry(**obj)
        case "robustness":
            match learning_task:
                case "binary_classification":
                    return BinaryClassificationRobustnessMetricEntry(**obj)
                case "multi_classification":
                    return MultiClassificationRobustnessMetricEntry(**obj)
                case "regression":
                    return RegressionRobustnessMetricEntry(**obj)
                case "clustering":
                    raise ValueError("Robustness metric is not supported for clustering")
        case "security":
            match learning_task:
                case "binary_classification":
                    return BinaryClassificationSecurityMetricEntry(**obj)
                case "multi_classification":
                    return MultiClassificationSecurityMetricEntry(**obj)
                case "regression":
                    return RegressionSecurityMetricEntry(**obj)
                case "clustering":
                    raise ValueError("Security metric is not supported for clustering")