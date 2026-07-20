from pydantic import BaseModel, ValidationError
from pathlib import Path
from typing import Literal
import json


class FunctionSignature(BaseModel):
    """List of authorized parameters types"""
    # todo : change this to parsing each elements of parameters.x.type
    parameters: dict[str, Literal['string', 'integer', 'float', 'boolean', 'number']]


class SchemasBuilder:
    def __init__(self) -> None:
        pass

    @staticmethod
    def build_prompt(func_path: str) -> str:
        """Creates the system prompt with instructions and the available
        functions/their signature."""
        with open(func_path) as f:
            functions = json.load(f)

        system_prompt = "You are a function-calling AI assistant."\
            "Your task is to: "\
            "1. Analyze the user's request and determine which "\
            "function would be the more relevant. 2. When a match "\
            "is found, extract the function name and its arguments."

        for func in functions:
            fn_name = func['fn_name']
            args = func.get('args_types', {})

            param_strings = [f"{k}: {v}" for k, v in args.items()]
            params_formatted = ", ".join(param_strings)

            system_prompt += f"- {fn_name}({params_formatted})\n"
        return system_prompt

    @staticmethod
    def build_schema(func_path: str) -> tuple[dict, str]:
        """Creates the schema for each functions for the later state queue."""
        with open(func_path) as f:
            functions = json.load(f)

        raw = json.loads(
            Path('./data/input/functions_definition.json').read_text())
        try:
            for function in raw:
                # validated = FunctionSignature.model_validate(function)
                FunctionSignature.model_validate(function)
        except ValidationError as e:
            raise RuntimeError(f"functions_definition.json is malformed: {e}")
        models = {}
        for func in functions:
            models[func['name']] = func.get('parameters', {})
        return models, SchemasBuilder.build_prompt(func_path)
