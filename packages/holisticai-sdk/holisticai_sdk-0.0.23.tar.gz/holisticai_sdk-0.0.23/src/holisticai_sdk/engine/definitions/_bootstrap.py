from typing_extensions import TypedDict
from holisticai_sdk.engine.definitions._base import Target
from pydantic import BaseModel, ConfigDict
from numpy.random import RandomState

class BootstrapMetric(TypedDict):
    name: str
    values: list[float]
    target: Target


class BootstrapModelMetrics(TypedDict):
    model_name: str
    metrics: list[BootstrapMetric]


class MetricAggregate(TypedDict):
    name: str
    value: float
    
class MetricAggregates(BaseModel):
    name: str
    aggregates: list[MetricAggregate]
    target: Target

class BootstrapModelMetricAggregates(TypedDict):
    model_name: str
    metrics: list[MetricAggregates]

class Bootstrapping(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    num_bootstraps: int
    max_samples: int = 10000
    random_state: RandomState = RandomState(42)



