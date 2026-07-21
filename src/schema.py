from pydantic import BaseModel, ValidationError
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

        system_prompt = "Among the following functions, select the most \
                        relevant one based on the user prompt. Extract \
                        the parameters (verbatim for strings parameters)\
                         required by the selected function's signature. \
                         If of float or of numbers types add a floating \
                         value. Do not include leading or trailing \
                         whitespaces inside string parameters"

        for func in functions:
            fn_name = func.get('name')
            desc = func.get('description', '')
            parameters = func.get('parameters', {})
            param_strings = [f"{k}: {v.get('type')}"
                             for k, v in parameters.items()]
            params_formatted = ", ".join(param_strings)

            system_prompt += f"- {fn_name}({params_formatted}) - {desc}\n"
        system_prompt += 'Example : User: "Turn \"Hello there {person} !\" to \
        uppercase with placeholders" -> OUtput : {"name": \
        "fn_to_uppercase_with_placeholders","parameters":{"string": \
        "Hello there {person} !}}'
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
