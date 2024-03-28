from typing import Type, TypeVar

from pydantic import BaseModel
import yaml


ExpectedType = TypeVar("ExpectedType", bound=BaseModel)


def parse_yaml_object(data: str, response_type: Type[ExpectedType]) -> ExpectedType:
    if not issubclass(
        response_type, BaseModel
    ):  # Turns out the fancy typing here isn't enough information for VS Code python tools to understand the type constraint
        # So, do a runtime check to be sure
        raise ValueError(f"{response_type} is not a subclass of BaseModel")

    # LLM loves to put yaml in markdown despite instructions, so try to cleanse
    if "```" in data:
        data = data.replace("```yaml", "```")
        data = data.split("```")[1]

    return response_type.model_validate(yaml.safe_load(data))
