from pydantic import BaseModel, Field, create_model
from typing import Literal
import json

class Output(BaseModel):
    prompt: str = Field(description="The prompt given by the user")
    function_name: str = Field(description="The name of the function that is the best fit to answer the user's question.")
    arguments: list[str] = Field(description="List of arguments that should be used by the function.")

class SchemasBuilder:
  def __init__(self) -> None:
    pass

  @staticmethod
  def build_schema(func_path: str) -> None:
    # Load the functions in a dict
    dynamic_models = {}
    with open(func_path) as functions_definitions:
      functions_definitions = json.load(functions_definitions)
    for function in functions_definitions:
      fields = {
        "name":(Literal[function['fn_name']])
        # "name":(Literal[function['fn_name']], Field(...))
      }

      # print("Raw function ->", function)
      for param_name, param_type in function['args_types'].items():
        fields[param_name] = (param_type)
        # fields[param_name] = (param_type, Field(...))
      # fields['return_type'] = function['return_type']

      dynamic_models[function['fn_name']] = create_model(function['fn_name'], **fields)
      print(f"Model for {function['fn_name']}->", fields)
    # print("Dynamic ->", dynamic_models)
    return dynamic_models
