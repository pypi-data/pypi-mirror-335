from __future__ import annotations

import statistics
from collections import defaultdict
from typing import Generator, Literal

import numpy as np
import pandas as pd
from numpy.random import RandomState


from holisticai_sdk.engine.definitions import BootstrapMetric, Metric, MetricAggregate, MetricAggregates, BootstrapModelMetrics, BootstrapModelMetricAggregates
from holisticai_sdk.engine.definitions._datasets import (
    GenericDatasetTypes
)
from holisticai_sdk.engine.metrics.utils import compute_metrics_from_entry
from holisticai_sdk.engine.metrics.utils import filter_valid_learning_metrics
from holisticai_sdk.engine.definitions import Bootstrapping

BootstrapIndices = list[list[int]]

BootstrapType = Literal["iid", "stratified"]



def iid_bootstrap(idx: pd.Series, size: int, random_state: RandomState) -> np.ndarray:
    """
    Implement iid bootstrap
    """
    # idx - ids to be shuffled and selected
    # size - size of the bootstrap sample
    return np.array(random_state.choice(idx, size).tolist())


def stratified_bootstrap(
    idx: pd.Series,
    max_samples: int,
    groups: pd.Series,
    random_state: RandomState,
) -> np.ndarray:
    """
    Implement stratified bootstrap

    idx - ids to be shuffled and selected
    groups - variable that constrains selection
    size - size of the bootstrap sample
    """
    ids = np.array([], dtype=np.int32)
    num_groups = len(np.unique(groups))
    size = max_samples // num_groups
    for g in np.unique(groups):
        subidx = pd.Series(idx[(groups == g).values.ravel()])
        ids = np.append(ids, iid_bootstrap(subidx, size, random_state))
    return np.array(ids.tolist())


def sampling_dataset(dataset: GenericDatasetTypes, indexes: np.ndarray) -> GenericDatasetTypes:
    match dataset.learning_task:
        case "binary_classification"|"multi_classification"|"regression":
            if dataset.vertical == "bias":
                return dataset.model_copy(
                    update={
                        "X": dataset.X.iloc[indexes],
                        "y_true": dataset.y_true.iloc[indexes],
                        "group_a": dataset.group_a.iloc[indexes],
                        "group_b": dataset.group_b.iloc[indexes],
                    }
                )
            else:
                return dataset.model_copy(
                    update={
                        "X": dataset.X.iloc[indexes],
                        "y_true": dataset.y_true.iloc[indexes],
                    }
                )

        case "clustering":
            if dataset.vertical == "bias":
                return dataset.model_copy(
                    update={
                        "X": dataset.X.iloc[indexes],
                        "group_a": dataset.group_a.iloc[indexes],
                        "group_b": dataset.group_b.iloc[indexes],
                    }
                )
            else:
                return dataset.model_copy(update={"X": dataset.X.iloc[indexes]})

def bootstrapping_generator(
    dataset: GenericDatasetTypes,
    num_bootstraps: int = 100,
    max_samples=10000,
    random_state: RandomState | None = None,
) -> Generator[GenericDatasetTypes]:
    if random_state is None:
        random_state = RandomState(0)

    max_samples = min(max_samples, dataset.X.shape[0])
    match dataset.learning_task:
        case "binary_classification" | "multi_classification":
            num_samples = dataset.X.shape[0]
            indexes = pd.Series(list(range(num_samples)))
            groups = dataset.y_true.astype(int)
            for _ in range(num_bootstraps):
                boostrap_indexes = stratified_bootstrap(
                    indexes,
                    max_samples=max_samples,
                    groups=groups,
                    random_state=random_state,
                )
                yield sampling_dataset(dataset, boostrap_indexes)

        case "regression":
            num_samples = dataset.X.shape[0]
            indexes = pd.Series(list(range(num_samples)))
            for _ in range(num_bootstraps):
                boostrap_indexes = iid_bootstrap(indexes, size=max_samples, random_state=random_state)
                yield sampling_dataset(dataset, boostrap_indexes)

        case "clustering":
            num_samples = dataset.X.shape[0]
            indexes = pd.Series(list(range(num_samples)))
            for _ in range(num_bootstraps):
                boostrap_indexes = iid_bootstrap(indexes, size=max_samples, random_state=random_state)
                yield sampling_dataset(dataset, boostrap_indexes)



def compute_metrics_from_partial_compute_metric_entry(compute_metric_entry, _test, learning_metrics):
    entry = compute_metric_entry(test=_test)
    learning_metrics = filter_valid_learning_metrics(entry, learning_metrics)
    metric_outputs = compute_metrics_from_entry(learning_metrics, entry)
    return metric_outputs

def compute_bootstrap_metrics(bootstrapping: Bootstrapping, compute_metric_entry, learning_metrics, test: GenericDatasetTypes) -> list[BootstrapMetric]:
    results = defaultdict(list[Metric])


    for _test in bootstrapping_generator(
        test,
        num_bootstraps=bootstrapping.num_bootstraps,
        max_samples=bootstrapping.max_samples,
        random_state=bootstrapping.random_state,
    ):
        metric_outputs = compute_metrics_from_partial_compute_metric_entry(compute_metric_entry, _test, learning_metrics)
        for m in metric_outputs:
            results[m.name].append(m)

    return [
        BootstrapMetric(name=name, values=[m.value for m in m], target=m[0].target) for name, m in results.items()
    ]


def compute_metric_aggregates(bootstrap_metrics: list[BootstrapMetric]):
    def q05(arr):
        return np.quantile(arr, q=0.05)

    def q95(arr):
        return np.quantile(arr, q=0.95)

    def mad(arr):
        arr = np.ma.array(arr).compressed()  # should be faster to not use masked arrays.
        med = np.median(arr)
        return np.median(np.abs(arr - med))

    def std_error(arr: list[float]):
        try:
            return statistics.stdev(arr) / np.sqrt(len(arr))
        except:
            return np.inf

    return [
        MetricAggregates(
            name=i["name"],
            aggregates=[
                MetricAggregate(name="mean", value=statistics.mean(i["values"])),
                MetricAggregate(name="median", value=statistics.median(i["values"])),
                MetricAggregate(name="q05", value=q05(i["values"])),
                MetricAggregate(name="q95", value=q95(i["values"])),
                MetricAggregate(name="mad", value=mad(i["values"])),
                MetricAggregate(name="std_error", value=std_error(i["values"])),
            ],
            target=i["target"],
        )
        for i in bootstrap_metrics
    ]


def compute_aggregates_from_bootstrap_metrics(metrics: list[BootstrapModelMetrics]):
    return [
        BootstrapModelMetricAggregates(model_name=x["model_name"], metrics=compute_metric_aggregates(x["metrics"]))
        for x in metrics
    ]
