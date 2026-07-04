from pydantic import BaseModel, Field
from .wrapper import Small_LLM_Model
from .parser import DataParser
from .vocabulary import VocabularyLoader
from .schema import SchemasBuilder
import numpy as np

class EngineConfig(BaseModel):
    prompt: str = Field(..., description="The prompt provided by the user.") 
    max_tokens: int = Field(default=50, ge=1, le=500)

class ModelOrchestrator:
  # def __init__(self, instance, config: EngineConfig) -> None:
  def __init__(self, prompt, instance, max_tokens) -> None:
    self.prompt = prompt
    self.model_wrapper = instance
    self.max_tokens = max_tokens

  def process_prompt(self) -> None:
    encoded_initial_prompt = self.model_wrapper._encode(self.prompt)
    self.token_history: list[int] = []

    for token in encoded_initial_prompt[0]:
        self.token_history.append(token)

  def create_schema(self, expected_output):
    #first, I need to create a json schema from a json dummy file
    # the dummy file would be the expected format, literally. I'd then need to convert it to pydantic to then convert it to json format ? Am a bit lost
    # this would then create self.schema
      pass

  def create_functions_schemas(self, functions_path: str):
    # here functions_path is a path that holds the json file containing the available functions
    # using these functions, we create a pydantic model. Is this possible ? supposing the funcions are in a list in this format : 
    #  {
  #   "fn_name": "fn_add_numbers",
  #   "description": "Adds the value of a to the value of b, returns the result"
  #   "args_names": [
  #     "a",
  #     "b"
  #   ],
  #   "args_types": {
  #     "a": "float",
  #     "b": "float"
  #   },
  #   "return_type": "float"
  # },
    # else, I need to figure out a way to create the expected schema
    # im STILL unsure of the usage of pydantic regarding this
      pass

  def generate(self) -> int:
    # print("Current tokens ->", self.token_history)
    next_logits = np.array(self.model_wrapper.get_logits_from_input_ids(self.token_history))
    filtered_tokens = self.parser.get_valid_tokens(next_logits)
    selected_token = np.argmax(filtered_tokens)
    print("Selected token", selected_token)
    self.token_history.append(selected_token)
    return selected_token
    # return is_last_char

  def answer_prompt(self) -> str:
        self.process_prompt()
        vocabulary = VocabularyLoader(self.model_wrapper)
        vocabulary.load_vocab()
        vocab_list = vocabulary.get_vocab_array()
        models = SchemasBuilder.build_schema('./data/input/functions_definition.json')
        self.parser = DataParser(models, vocab_list)
        # parser.advance_state('{"fn": "')
        # parser.advance_state('fn_substitute_string_with_regex')
    # data_parser = DataParser(self.schema)

        # while len(self.parser.state_queue) > 0:
        #     current_token = self.generate()
        #     self.parser.advance_state(self.model_wrapper._decode(current_token))
        # decoded_str = self.model_wrapper._decode(self.token_history) 
        # return decoded_str
