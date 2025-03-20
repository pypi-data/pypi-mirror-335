from holisticai_sdk.engine.definitions._vertical_settings import SecuritySettings, RobustnessSettings
from typing import overload, Literal

@overload
def VerticalSettings(vertical: Literal["security"], attack_attribute: str) -> SecuritySettings:
    ...

@overload
def VerticalSettings(vertical: Literal["robustness"], attack_attributes: list[str]) -> RobustnessSettings:
    ...

