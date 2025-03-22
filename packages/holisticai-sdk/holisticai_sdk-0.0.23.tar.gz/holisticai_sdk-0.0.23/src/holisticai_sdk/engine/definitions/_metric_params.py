
"""
from __future__ import annotations

from typing import Annotated, Generic, Literal, Union

from pydantic import BaseModel, ConfigDict, Field

from holisticai_engine.definitions._datasets import GenericDatasetTypeVar
from holisticai_engine.definitions._base import GenericModelType
from holisticai_engine.definitions._vertical_settings import RobustnessSettings, SecuritySettings

DatasetTypes = Literal["train", "test"]


class EfficacyMetricInputParams(BaseModel, Generic[GenericModelType, GenericDatasetTypeVar]):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    learning_task: Literal["binary_classification", "multi_classification", "regression", "clustering"]
    vertical: Literal["efficacy"]
    model: GenericModelType
    test: GenericDatasetTypeVar


class BiasMetricInputParams(BaseModel, Generic[GenericModelType, GenericDatasetTypeVar]):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    learning_task: Literal["binary_classification", "multi_classification", "regression", "clustering"]
    vertical: Literal["bias"]
    model: GenericModelType
    test: GenericDatasetTypeVar


class ExplainabilityMetricInputParams(BaseModel, Generic[GenericModelType, GenericDatasetTypeVar]):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    learning_task: Literal["binary_classification", "multi_classification", "regression", "clustering"]
    vertical: Literal["explainability"]
    model: GenericModelType
    test: GenericDatasetTypeVar


class SecurityMetricInputParams(BaseModel, Generic[GenericModelType, GenericDatasetTypeVar]):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    learning_task: Literal["binary_classification", "multi_classification", "regression", "clustering"]
    vertical: Literal["security"]
    model: GenericModelType
    train: GenericDatasetTypeVar
    test: GenericDatasetTypeVar
    settings: SecuritySettings


class RobustnessMetricInputParams(BaseModel, Generic[GenericModelType, GenericDatasetTypeVar]):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    learning_task: Literal["binary_classification", "multi_classification", "regression", "clustering"]
    vertical: Literal["robustness"]
    model: GenericModelType
    test: GenericDatasetTypeVar
    settings: RobustnessSettings


MetricInputParams = Annotated[
    Union[
        EfficacyMetricInputParams,
        BiasMetricInputParams,
        ExplainabilityMetricInputParams,
        SecurityMetricInputParams,
        RobustnessMetricInputParams,
    ],
    Field(discriminator="vertical"),
]
"""