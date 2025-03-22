from typing import Optional
from holisticai_sdk.engine.definitions._base import Vertical
from holisticai_sdk.engine.definitions._vertical_settings import SecuritySettings, RobustnessSettings, VerticalSettingsTypes

def VerticalSettings(vertical: Vertical, attack_attribute: Optional[str]=None, attack_attributes: Optional[list[str]]=None) -> VerticalSettingsTypes:
    match vertical:
        case "security":
            return SecuritySettings(attack_attribute=attack_attribute)
        case "robustness":
            return RobustnessSettings(attack_attributes=attack_attributes)
        case _:
            raise NotImplementedError(f"Vertical {vertical} is not implemented.")