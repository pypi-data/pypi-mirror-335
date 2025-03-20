from pydantic import BaseModel
from typing import Optional, Union

class SecuritySettings(BaseModel):
    attack_attribute: Optional[str] = None

class RobustnessSettings(BaseModel):
    attack_attributes: Optional[list[str]] = None

VerticalSettingsTypes = Union[SecuritySettings, RobustnessSettings]