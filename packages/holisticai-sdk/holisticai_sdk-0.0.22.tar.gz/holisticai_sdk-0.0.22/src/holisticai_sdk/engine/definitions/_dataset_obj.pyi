from re import L
from holisticai_sdk.engine.definitions._datasets import BiasUnsupervisedDataset, UnsupervisedDataset, BiasSupervisedDataset, SupervisedDataset
import pandas as pd
from typing import overload, Literal

@overload
def Dataset(
    vertical: Literal["bias"], 
    learning_task: Literal["clustering"], 
    X: pd.DataFrame, 
    group_a: pd.Series, 
    group_b: pd.Series) -> BiasUnsupervisedDataset:...

@overload
def Dataset(
    vertical: Literal["efficacy", "explainability", "robustness", "security"], 
    learning_task: Literal["clustering"], 
    X: pd.DataFrame)-> UnsupervisedDataset:...

@overload
def Dataset(
    vertical: Literal["bias"], 
    learning_task: Literal["binary_classification", "multi_classification", "regression"], 
    X: pd.DataFrame, 
    y_true: pd.Series|None, 
    group_a: pd.Series, 
    group_b: pd.Series)-> BiasSupervisedDataset:...

@overload
def Dataset(
    vertical: Literal["efficacy", "explainability", "robustness", "security"], 
    learning_task: Literal["binary_classification", "multi_classification", "regression"], 
    X: pd.DataFrame, 
    y_true: pd.Series|None)-> SupervisedDataset:...