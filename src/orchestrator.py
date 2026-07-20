from .schema import SchemasBuilder
from .vocabulary import VocabularyLoader
from .parser import DataParser
from .wrapper import Small_LLM_Model

from typing import Any
import numpy as np
import json
from pathlib import Path
from pydantic import (BaseModel, Field, field_validator,
                      create_model, ValidationError)


class EngineConfig(BaseModel):
    prompt: str = Field(..., min_length=1,
                        description="The prompt provided by the user.")
    max_tokens: int = Field(default=50, ge=1, le=500)
    functions_path: str = Field(min_length=1)

    @field_validator('functions_path')
    @classmethod
    def path_must_exist(cls, v: str) -> str:
        file = Path(v)
        if not file.is_file():
            raise ValueError(f"functions_path does not exist: {v}")
        return v


def build_verifier(fn_name: str, params: dict[str, str]) -> type[BaseModel]:
    """Checks the types of the functions
    to check that the signatures are correct."""
    type_map = {'string': str, 'integer': int, 'number': float, 'float': float, 'boolean': bool}
    field_defs: dict[str, Any] = {name: (type_map[ptype], ...)
                                  for name, ptype in params.items()}
    return create_model(fn_name, **field_defs)


class ModelOrchestrator:
    def __init__(self, config: EngineConfig,
                 instance: Small_LLM_Model) -> None:
        # def __init__(self, prompt, instance, max_tokens) -> None:
        self.prompt = config.prompt
        self.model_wrapper = instance
        self.max_tokens = config.max_tokens
        self.functions_path = config.functions_path
        self.system_prompt = ""

    def process_prompt(self) -> None:
        """Creates the token history for the user and system prompt,
        creating the initial token list."""
        self.prompt += '\nAnswer :'
        encoded_initial_prompt = self.model_wrapper._encode(self.prompt)
        print("Current path for functions =>", self.functions_path)
        if len(self.system_prompt) == 0:
            self.models, self.system_prompt = SchemasBuilder.build_schema(
                self.functions_path)
            self.encoded_system_prompt = self.model_wrapper._encode(
                "System: " + self.system_prompt)
        self.token_history: list[int] = list(self.encoded_system_prompt[0])

        for token in encoded_initial_prompt[0]:
            self.token_history.append(token)

    def generate(self) -> int:
        """Use the current token history to generate the next token's logits
        then select the highest token (with softmax) and append it."""
        # print("Current tokens ->", self.token_history)
        if self.max_tokens <= 0:
            raise ValueError(
                "All the tokens have been exhausted. "
                "Set a higher max token for each function call.")
        self.max_tokens -= 1
        next_logits = np.array(
            self.model_wrapper.get_logits_from_input_ids(self.token_history))
        filtered_tokens = self.parser.get_valid_tokens(next_logits)
        selected_token = self.calc_softmax(filtered_tokens)
        self.token_history.append(selected_token)
        return selected_token

    def calc_softmax(self, filtered_tokens: np.ndarray) -> int:
        """Using exponent, we convert each logit (which is not inf or -inf)
        into a number between 0 and 1, matching their probability."""
        softmax_array = np.exp(filtered_tokens)/sum(np.exp(filtered_tokens))
        return int(np.argmax(softmax_array))

    def answer_prompt(self) -> str:
        """Once all states has been completed, we consider the prompt answered
        and return the string, JSON formatted."""
        self.process_prompt()
        vocabulary = VocabularyLoader(self.model_wrapper)
        vocabulary.load_vocab()
        self.vocab_list = vocabulary.get_vocab_array()
        self.parser = DataParser(self.models, self.vocab_list, self.prompt)
        while len(self.parser.state_queue) > 0:
            current_token = self.generate()
            decoded = self.model_wrapper._decode(current_token)
            self.parser.advance_state(decoded)
        decoded_str = self.model_wrapper._decode(
            self.token_history[len(self.encoded_system_prompt[0]):])
            # self.token_history)
        print("Full system prompt :", self.model_wrapper._decode(
            self.token_history))
        fixed_string = decoded_str[len(self.prompt):]
        # fixed_string = fixed_string.replace('\\', '\\\\')
        # print("Fixed str ->", fixed_string)
        parsed = json.loads(fixed_string)
        ordered = {
            "prompt": self.prompt[:len(self.prompt) - 9],
            "name": parsed["name"],
            "parameters": parsed["parameters"],
        }
        print("Ordered ->", ordered)
        final_output = json.dumps(ordered)
        print("Final ->", final_output)
        Verifier = build_verifier(parsed["name"], self.models[parsed["name"]])
        try:
            Verifier(**parsed["parameters"])
            print("Output is valid JSON ✅ "
                  "(emoji not generated by AI, or is it ?)")
        except ValidationError as e:
            print("Decoder output doesn't match its own schema:", e)
        return final_output
