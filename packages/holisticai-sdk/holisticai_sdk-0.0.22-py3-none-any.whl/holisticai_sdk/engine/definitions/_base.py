from __future__ import annotations

from typing import Annotated, Any, Callable, Generic, Literal, TypeVar, Union

import pandas as pd
from numpy.typing import ArrayLike, NDArray  # noqa: TCH002
from pydantic import BaseModel, ConfigDict, Field
from typing_extensions import TypedDict

DEFAULT_NAME = "default"

class HAIRigidBinaryClassification(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    name: str = DEFAULT_NAME
    learning_task: Literal["binary_classification"] = "binary_classification"
    has_probability: Literal[False] = False
    predict: Callable[[pd.DataFrame], ArrayLike]
    classes: list[Any]



class HAIProbBinaryClassification(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True) 
    name: str = DEFAULT_NAME
    learning_task: Literal["binary_classification"] = "binary_classification"
    has_probability: Literal[True] = True
    predict: Callable[[pd.DataFrame], ArrayLike]
    predict_proba: Callable[[pd.DataFrame], ArrayLike | NDArray]
    classes: list[Any]



HAIBinaryClassification = Annotated[
    Union[HAIRigidBinaryClassification, HAIProbBinaryClassification],
    Field(discriminator="has_probability"),
]


class HAIRigidMultiClassification(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    name: str = DEFAULT_NAME
    learning_task: Literal["multi_classification"] = "multi_classification"
    has_probability: Literal[False] = False
    predict: Callable[[pd.DataFrame], ArrayLike]
    classes: list[Any]



class HAIProbMultiClassification(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    name: str = DEFAULT_NAME
    learning_task: Literal["multi_classification"] = "multi_classification"
    has_probability: Literal[True] = True
    predict: Callable[[pd.DataFrame], ArrayLike]
    predict_proba: Callable[[pd.DataFrame], ArrayLike | NDArray]
    classes: list[Any]



HAIMultiClassification = Annotated[
    Union[HAIRigidMultiClassification, HAIProbMultiClassification],
    Field(discriminator="has_probability"),
]
HAIClassification = Union[HAIBinaryClassification, HAIMultiClassification]


class HAIRegression(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    name: str = DEFAULT_NAME
    has_probability: Literal[False] = False
    learning_task: Literal["regression"] = "regression"
    predict: Callable[[pd.DataFrame], ArrayLike]



class HAIClustering(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    name: str = DEFAULT_NAME
    has_probability: Literal[False] = False
    learning_task: Literal["clustering"] = "clustering"
    predict: Callable[[pd.DataFrame], ArrayLike]
    classes: list[Any]



HAIModel = Annotated[
    Union[HAIBinaryClassification, HAIMultiClassification, HAIRegression, HAIClustering],
    Field(discriminator="learning_task"),
]
GenericModelType = TypeVar(
    "GenericModelType",
    HAIBinaryClassification,
    HAIMultiClassification,
    HAIRegression,
    HAIClustering,
)

Vertical = Literal["efficacy", "bias", "explainability", "robustness", "security"]
LearningTask = Literal["binary_classification", "multi_classification", "regression", "clustering"]

class Target(TypedDict):
    range: tuple[float, float] | None
    value: float


class Metric(BaseModel):
    name: str
    value: float
    target: Target


class LearningMetric(BaseModel):
    name: str
    fn: Callable
    entry_params: list[str]
    target: Target
    cost_fn: Callable[[float], float]


class MetricCost(BaseModel):
    cost_value: float
    metric_value: float|None