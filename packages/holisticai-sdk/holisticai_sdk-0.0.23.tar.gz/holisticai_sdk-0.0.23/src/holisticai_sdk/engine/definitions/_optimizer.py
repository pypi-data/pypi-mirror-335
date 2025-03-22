from typing import Literal, Callable, Optional, Any
from holisticai_sdk.engine.definitions._vertical_settings import SecuritySettings, RobustnessSettings
from holisticai_sdk.engine.definitions._base import HAIModel
from pydantic import BaseModel, ConfigDict

class ModelOptparams(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    categorical_mask : list[int]
    encoded_dim : int 

class VerticalOptParams(BaseModel):
    security_settings: Optional[SecuritySettings] = None
    robustness_settings: Optional[RobustnessSettings] = None

class OptimizerParams(BaseModel):
    strategy : Literal["cma","ga"]
    opt_options: dict[str, Any] = {"sigma0": 0.3, "inopts":{"popsize": 50, "maxiter": 20}}
    callbacks: list[Callable]

class TrainingParams(BaseModel):
    model_params: ModelOptparams
    vertical_params: VerticalOptParams
    optimizer_params: OptimizerParams
    model: HAIModel
