import numpy as np

class DataParser:
    def __init__(self, models: dict, vocab: list) -> None:
    # def __init__(self, models: dict, pydantic_schema: dict, vocab: list[str]) -> None:
        self.state_id = 0
        # Same as index 0, but using a linked list like style of dict
        self.current_node = "START"
        # schema should be the json object containing the various states
        # self.schema = schema
        self.models = models
        self.available_functions = list(self.models.keys())
        self.state_queue = ['{"fn":', '"', self.available_functions]
        self.current_buffer = ''
        self.final: list[str | list[str]] = []
        self.vocab: list[str] = vocab
        self.index = 0

    def get_valid_tokens(self, next_logits) -> np.ndarray:
        # find the greatest match, if not reduce. or do char by char
        if type(self.state_queue[0]) == str:
            print("Expected : ->", self.state_queue[0][self.index], "<-")
            bool_array = np.char.equal(self.vocab, self.state_queue[0][self.index])
            self.index += 1
            next_logits[~bool_array] = -np.inf
        elif type(self.state_queue[0]) == list:
            bool_array = np.char.equal(self.vocab, self.state_queue[0][1][self.index])
            self.index += 1
            next_logits[~bool_array] = -np.inf
            # bool_array = {}
            # for i, available_function in enumerate(self.available_functions):
            #     # enable all of the available functions
            #     # for other iterations, remove the one not available anymore
            #     bool_array[available_function] = np.char.equal(self.vocab, available_function[:self.index])
            #     if i == 0:
            #         mask = bool_array[available_function] 
            #
            #     mask = np.ma.mask_or(mask, bool_array[available_function])
            #     print("Expected ->", self)
            # self.index += 1
            # next_logits[~mask] = -np.inf


        # for tensor in past_tensor:
        #   array[tensor] *= (-1.2 if array[tensor] > 0 else 1.2)
        return next_logits
              # if not advance_state:
              #     return filtered_array, True

    def advance_state(self, token_string: str) -> None:
        # need to check if the current string completes the state. need to store the current string until state is completed.
        # print(self.state_queue)
        current_requirement = self.state_queue[0]
        self.current_buffer += token_string
        # Maybe additional check here ?
        print("Current buffer ->", self.current_buffer, "required ->", current_requirement)
        if isinstance(current_requirement, list):
            if self.current_buffer in current_requirement:
                self.index = 0
                self.state_queue.pop(0)
                self.final.append(self.current_buffer)
                if isinstance(current_requirement, list):
                  self._get_params_from_function(self.current_buffer)
                self.current_buffer = ""
        elif isinstance(current_requirement, str):
            if self.current_buffer == current_requirement:
                self.index = 0
                self.state_queue.pop(0)
                self.final.append(self.current_buffer)
                self.current_buffer = ""
        #   return False
        # return True

    def _get_params_from_function(self, fn_name: str):
      schema = self.models[fn_name].model_json_schema()
      
      params = [k for k in schema.get("properties", {}).keys() if k != "fn"]
      # print("Params ->", schema)
      
      test_dicto = {}
      for i, param in enumerate(params):
          prefix = '","' if i == 0 else ',"'
          
          self.state_queue.append(f'{prefix}{param}":"')
          
          param_type = schema['properties'][param]['type']
          test_dicto[param] = param_type
          self.state_queue.append(param_type) 
          
      print(test_dicto)
      self.state_queue.append('"}')
