from holisticai_sdk.engine.definitions._base import Vertical, LearningTask
from holisticai_sdk.engine.definitions._datasets import BiasUnsupervisedDataset, UnsupervisedDataset, BiasSupervisedDataset, SupervisedDataset
import pandas as pd

def Dataset(vertical: Vertical, learning_task: LearningTask, X: pd.DataFrame, y_true: pd.Series|None=None, group_a: pd.Series|None=None, group_b: pd.Series|None=None):
    match learning_task:
        case "binary_classification" | "multi_classification" | "regression":
            assert y_true is not None
            if vertical == "bias":
                assert group_a is not None and group_b is not None
                return BiasSupervisedDataset(learning_task=learning_task, X=X, y_true=y_true, group_a=group_a, group_b=group_b)
            return SupervisedDataset(learning_task=learning_task, vertical=vertical, X=X, y_true=y_true)
        case "clustering":
            if vertical == "bias":
                assert group_a is not None and group_b is not None
                return BiasUnsupervisedDataset(learning_task=learning_task, vertical=vertical, X=X, group_a=group_a, group_b=group_b)
            return UnsupervisedDataset(learning_task=learning_task, vertical=vertical, X=X)

