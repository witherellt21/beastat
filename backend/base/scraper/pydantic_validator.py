from typing import Any

from pydantic import GetCoreSchemaHandler
from pydantic_core import CoreSchema, core_schema


class PydanticValidatorMixin:
    @classmethod
    def validate(cls, __input_value: Any, _: core_schema.ValidationInfo):
        if not isinstance(__input_value, cls):
            raise ValueError(f"Expected {cls}, received: {type(__input_value)}")
        return __input_value

    @classmethod
    def __get_pydantic_core_schema__(
        cls, source_type: Any, handler: GetCoreSchemaHandler
    ) -> CoreSchema:
        return core_schema.with_info_plain_validator_function(cls.validate)
