from pydantic import BaseModel, ValidationError
from pathlib import Path
from typing import Literal, Dict
import json


class ParameterDefinition(BaseModel):
    type: Literal['string', 'number', 'integer', 'float', 'boolean']


class FunctionSignature(BaseModel):
    """Schema for the new function configuration format"""
    name: str
    description: str
    parameters: Dict[str, ParameterDefinition]


class SchemasBuilder:
    def __init__(self) -> None:
        pass

    @staticmethod
    def build_prompt(func_path: str) -> str:
        """Creates the system prompt with instructions and the available
        functions/their signature."""
        with open(func_path) as f:
            functions = json.load(f)

        # system_prompt = "Among the following functions, select the most relevant one from the user prompt, then enumerate the parameters according to the selected function signature. Strip the strings of whitespace in the parameters, but keep them as they are (Except for numbers and float who MUST have a floating value like 12.0)\n"
        system_prompt = "Among the following functions, select the most relevant one from the user prompt, then enumerate the parameters according to the selected function signature. Strip the strings of whitespace in the parameters, but keep them as they are. Floats and number must have a floating value, strings end with double quotes and don't start with whitespace.\n"
        # system_prompt = "You are a function-calling AI assistant. Your task is to: Analyze the user's request and determine which of the given functions would be the more relevant. Once the function is selected, fill the parameters according to the given function signature."
            # "is found, extract the function name and its arguments."

        for func in functions:
            fn_name = func.get('name')
            desc = func.get('description', '')
            parameters = func.get('parameters', {})
            param_strings = [f"{k}: {v.get('type')}" for k, v in parameters.items()]
            params_formatted = ", ".join(param_strings)

            system_prompt += f"- {fn_name}({params_formatted}) - {desc}\n"
            # system_prompt += f"- {fn_name}({params_formatted})\n"
        return system_prompt + "\nUser:"

    @staticmethod
    def build_schema(func_path: str) -> tuple[dict, str]:
        """Creates the schema for each functions for the later state queue."""
        with open(func_path) as f:
            functions = json.load(f)

        try:
            for function in functions:
                FunctionSignature.model_validate(function)
        except ValidationError as e:
            raise RuntimeError(f"functions_definition.json is malformed: {e}")
        models = {}
        for func in functions:
            models[func['name']] = {
                k: v['type'] for k, v in func.get('parameters', {}).items()
            }

        return models, SchemasBuilder.build_prompt(func_path)
