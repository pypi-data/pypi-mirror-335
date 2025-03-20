from __future__ import annotations

from typing import TYPE_CHECKING

from holisticai_sdk.engine.definitions import (
    HAIModel,
    LearningMetric,
    Metric,
    EfficacyMetricEntry, 
    SecurityMetricEntry, 
    RobustnessMetricEntry,
    ExplainabilityMetricEntry, 
    BiasMetricEntry,
    HAIProbBinaryClassification,
    HAIProbMultiClassification
)
from holisticai_sdk.utils.logger import get_logger
from typing import TypeVar

logger = get_logger(__name__)


MetricEntryType = TypeVar("MetricEntryType", EfficacyMetricEntry, SecurityMetricEntry, RobustnessMetricEntry, ExplainabilityMetricEntry, BiasMetricEntry)

if TYPE_CHECKING:
    from holisticai.utils import ModelProxy


def convert_to_holisticai_proxy(proxy: HAIModel) -> ModelProxy:
    from holisticai.utils import (
        BinaryClassificationProxy,
        MultiClassificationProxy,
        RegressionProxy,
    )

    match proxy.learning_task:
        case "binary_classification":
            predict_proba = None
            if isinstance(proxy, HAIProbBinaryClassification):
                predict_proba= proxy.predict_proba

            return BinaryClassificationProxy(
                predict=proxy.predict,
                predict_proba= predict_proba,   # type: ignore
                classes=proxy.classes,
            )  # type: ignore

        case "multi_classification":
            predict_proba = None
            if isinstance(proxy, HAIProbMultiClassification):
                predict_proba= proxy.predict_proba

            return MultiClassificationProxy(
                predict=proxy.predict,
                predict_proba=proxy.predict_proba, # type: ignore
                classes=proxy.classes,
            )  # type: ignore

        case "regression":
            return RegressionProxy(predict=proxy.predict)
    raise NotImplementedError


def is_valid_metric_entry(learning_metric: LearningMetric, e: MetricEntryType) -> bool:
    fn = learning_metric.fn
    required_attrs = set()
    lambda_code = fn.__code__
    freevars = lambda_code.co_freevars
    for var in freevars:
        if var.startswith("e."):
            attr = var.split(".", 1)[1]
            required_attrs.add(attr)

    return all(hasattr(e, attr) and getattr(e, attr) is not None for attr in required_attrs)


def compute_metrics_from_entry(learning_metrics, entry: MetricEntryType) -> list[Metric]:
    return [
        Metric(
            value=learning_metric.fn(entry),
            name=learning_metric.name,
            target=learning_metric.target,
        )
        for learning_metric in learning_metrics
        if is_valid_metric_entry(learning_metric, entry)
    ]


def filter_valid_learning_metrics(entry: MetricEntryType, learning_metrics: list[LearningMetric]) -> list[LearningMetric]:
    def is_valid_param(param, metric):
        if not hasattr(entry, param):
            logger.warning(f"{param} not found in entry: {type(entry)}, skipping metric: {metric.name}")
            return False
        if getattr(entry, param) is None:
            logger.warning(f"{param} is None, skipping metric: {metric.name}")
            return False
        return True

    return [
        metric for metric in learning_metrics
        if all(is_valid_param(param, metric) for param in metric.entry_params)
    ]

