from pydantic import BaseModel, field_validator

class Config(BaseModel):
    automonkey_users: list
    #automonkey_command_priority: int = 10
    automonkey_plugin_enabled: bool = True

    @field_validator("automonkey_command_priority")
    @classmethod
    def check_priority(cls, v: int) -> int:
        if v >= 1:
            return v
        raise ValueError("automonkey command priority must greater than 1")