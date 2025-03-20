from typing import Literal, overload

import pandas as pd

from holisticai_sdk.engine.definitions import HAIModel, HAIBinaryClassification, HAIMultiClassification, HAIRegression, HAIClustering

@overload
def get_baselines(
    learning_task: Literal["binary_classification"],
    x: pd.DataFrame,
    y: pd.Series,
) -> list[HAIModel[HAIBinaryClassification]]: ...

@overload
def get_baselines(
    learning_task: Literal["multi_classification"],
    x: pd.DataFrame,
    y: pd.Series,
) -> list[HAIModel[HAIMultiClassification]]: ...

@overload
def get_baselines(
    learning_task: Literal["regression"],
    x: pd.DataFrame,
    y: pd.Series,
) -> list[HAIModel[HAIRegression]]: ...

@overload
def get_baselines(
    learning_task: Literal["clustering"], 
    x: pd.DataFrame, 
    n_clusters: int,
) -> list[HAIModel[HAIClustering]]: ...
