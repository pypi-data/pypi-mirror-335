from typing import Literal, overload

from holisticai_sdk.engine.definitions import HAIModel, HAIBinaryClassification, HAIMultiClassification, HAIRegression, HAIClustering

@overload
def get_proxy_from_sdk_model(
    task: Literal["binary_classification"],
    predict_fn: str,
    predict_proba_fn: str | None = None,
    classes: list | None = None,
    name: str = "",
) -> HAIModel[HAIBinaryClassification]: ...

@overload
def get_proxy_from_sdk_model(
    task: Literal["regression"], 
    predict_fn: str, 
    name: str = ""
) -> HAIModel[HAIRegression]: ...

@overload

def get_proxy_from_sdk_model(
    task: Literal["multi_classification"],
    predict_fn: str,
    predict_proba_fn: str | None,
    classes: list | None = None,
    name: str = "",
) -> HAIModel[HAIMultiClassification]: ...

@overload

def get_proxy_from_sdk_model(
    task: Literal["clustering"],
    predict_fn: str,
    classes: list | None = None,
    name: str = "",
) -> HAIModel[HAIClustering]: ...