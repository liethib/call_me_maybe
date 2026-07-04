import numpy as np

class DataParser:
    def __init__(self, models: dict) -> None:
    # def __init__(self, models: dict, pydantic_schema: dict, vocab: list[str]) -> None:
        self.state_id = 0
        # Same as index 0, but using a linked list like style of dict
        self.current_node = "START"
        # schema should be the json object containing the various states
        # self.schema = schema
        self.models = models
        self.available_functions = list(self.models.keys())
        self.state_queue = ['{"fn": "', self.available_functions]
        self.current_buffer = ''
        self.final = []

    def get_valid_tokens(self, next_logits, schema) -> tuple[np.array, bool]:
        if not advance_state:
            return filtered_array, True

    def advance_state(self, token_string: str) -> None:
        # need to check if the current string completes the state. need to store the current string until state is completed.
        # print(self.state_queue)
        current_requirement = self.state_queue[0]
        self.current_buffer += token_string
        # Maybe additional check here ?
        if self.current_buffer in current_requirement:
          self.final.append(self.state_queue.pop(0))
          if isinstance(current_requirement, list):
            self._get_params_from_function(self.current_buffer)
          self.current_buffer = ""
        #   return False
        # return True

    def _get_params_from_function(self, fn_name: str):
      schema = self.models[fn_name].model_json_schema()
      
      params = [k for k in schema.get("properties", {}).keys() if k != "fn"]
      # print("Params ->", schema)
      
      test_dicto = {}
      for i, param in enumerate(params):
          prefix = '", "' if i == 0 else ', "'
          
          self.state_queue.append(f'{prefix}{param}": "')
          
          param_type = schema['properties'][param]['type']
          test_dicto[param] = param_type
          self.state_queue.append(param_type) 
          
      print(test_dicto)
      self.state_queue.append('"}')
