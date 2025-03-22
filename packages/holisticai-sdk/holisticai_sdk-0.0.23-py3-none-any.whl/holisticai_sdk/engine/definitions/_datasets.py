from typing import Annotated, Literal, TypeVar, Union

import pandas as pd
from pydantic import BaseModel, ConfigDict, Field


class BiasUnsupervisedDataset(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    learning_task: Literal["clustering"] = "clustering"
    vertical: Literal["bias"] = "bias"
    X: pd.DataFrame
    group_a: pd.Series
    group_b: pd.Series


class UnsupervisedDataset(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    learning_task: Literal["clustering"] = "clustering"
    vertical: Literal["efficacy", "explainability", "robustness", "security"]
    X: pd.DataFrame


class SupervisedDataset(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    learning_task: Literal["binary_classification","multi_classification", "regression"]
    vertical: Literal["efficacy", "explainability", "robustness", "security"]
    X: pd.DataFrame
    y_true: pd.Series


class BiasSupervisedDataset(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    learning_task: Literal["binary_classification","multi_classification", "regression"]
    vertical: Literal["bias"] = "bias"
    X: pd.DataFrame
    y_true: pd.Series
    group_a: pd.Series
    group_b: pd.Series


BiasDatasetTypes = Annotated[
    Union[BiasSupervisedDataset, BiasUnsupervisedDataset],
    Field(discriminator="learning_task"),
]
DatasetTypes = Annotated[
    Union[SupervisedDataset, UnsupervisedDataset],
    Field(discriminator="learning_task"),
]
GenericDatasetTypes = Annotated[
    Union[SupervisedDataset, UnsupervisedDataset, BiasSupervisedDataset, BiasUnsupervisedDataset],
    Field(discriminator="learning_task"),
]
GenericDatasetTypeVar = TypeVar(
    "GenericDatasetTypeVar",
    SupervisedDataset,
    UnsupervisedDataset,
    BiasSupervisedDataset,
    BiasUnsupervisedDataset,
)
