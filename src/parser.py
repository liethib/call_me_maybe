import numpy as np
import re
from typing import Any
from .types_handlers import (StringHandler,
                             IntHandler,
                             FloatHandler,
                             BoolHandler)


class DataParser:
    def __init__(self, models: dict, vocab: np.ndarray, prompt: str) -> None:
        self.models = models
        self.available_functions = list(self.models.keys())
        self.prompt = prompt
        self.state_queue = ['{', '"name":"',
                            self.available_functions, '",', '"parameters":{']
        self.current_buffer = ''
        self.double_quotes_counter = 0
        self.vocab: np.ndarray = vocab
        self.types: dict[str, Any] = {
            "string": StringHandler(self.vocab),
            "integer": IntHandler(self.vocab),
            "float": FloatHandler(self.vocab),
            "number": FloatHandler(self.vocab),
            "boolean": BoolHandler(self.vocab),
        }

    def _get_string_mask(self,
                         expected_string: str, buffer: str) -> np.ndarray:
        """Mini helper function that masks the logits which are not
        contributing to building the currently expected string."""
        remaining = expected_string[len(buffer):]
        if not remaining:
            return np.zeros(len(self.vocab), dtype=bool)

        mask = np.char.equal(self.vocab, remaining)

        possible_prefixes = [remaining[:i] for i in range(1, len(remaining))]
        if possible_prefixes:
            mask |= np.isin(self.vocab, possible_prefixes)

        return mask

    def get_valid_tokens(self, next_logits: np.ndarray) -> np.ndarray:
        """Method that allows us to select how we get our mask,
        based on the type of the expected state_queue element."""
        current_req = self.state_queue[0]
        mask = np.zeros(len(self.vocab), dtype=bool)

        if isinstance(current_req, tuple):
            req_type, is_last = current_req
            if req_type in self.types:
                mask = self.types[req_type].get_valid_tokens(
                    self.vocab, self.current_buffer, is_last=is_last)

        if isinstance(current_req, str):
            if current_req in self.types:
                mask = self.types[current_req].get_valid_tokens(
                    self.vocab, self.current_buffer)
            else:
                mask = self._get_string_mask(current_req, self.current_buffer)

        elif isinstance(current_req, list):
            self.available_functions = [function for
                                        function in self.available_functions if
                                        function.startswith(self.current_buffer
                                                            )]

            for function in self.available_functions:
                mask |= self._get_string_mask(function, self.current_buffer)

        next_logits[~mask] = -np.inf
        return next_logits

    def advance_state(self, token_string: str) -> None:
        """Checks whether the current state has been fullfiled, and moves
        to the next element."""
        current_req = self.state_queue[0]
        # fix for double backslash to test
        # fixed_string = re.sub(r'\\(?!["\\/bfnrtu])', r'\\\\', token_string)
        self.current_buffer += token_string
        for character in token_string:
            if character == '"':
                self.double_quotes_counter += 1
        print("Current char ->", token_string, "required ->", current_req)
        if isinstance(current_req, list):
            if self.current_buffer in current_req:
                self.state_queue.pop(0)
                self._get_params_from_function(self.current_buffer)
                self.current_buffer = ""

        elif isinstance(current_req, tuple):
            # parameter placeholder
            req_type, is_last = current_req
            if req_type in self.types:
                if self.types[req_type].is_complete(self.current_buffer,
                                                    is_last=is_last):
                    if req_type == 'string':
                        trailing = self.current_buffer.find('"') + 1
                    elif req_type in ['integer', 'float', 'number']:
                        for i in range(len(self.current_buffer) - 1, -1, -1):
                            if self.current_buffer[i].isnumeric():
                                trailing = i + 1
                                break
                    elif req_type == 'boolean':
                        trailing = self.current_buffer.rfind('e') + 1
                    while trailing < len(self.current_buffer) \
                            and self.current_buffer[trailing] \
                            in (',', '}', '"') and len(self.state_queue) > 1 \
                            and isinstance(self.state_queue[1], str):

                        inspected_char = self.current_buffer[trailing]
                        next_req = self.state_queue[1].strip()
                        if next_req.startswith(inspected_char):
                            self.state_queue.pop(1)
                        trailing += 1
                    self.state_queue.pop(0)
                    self.current_buffer = ""

        elif isinstance(current_req, str):
            if current_req in self.types:
                if self.types[current_req].is_complete(self.current_buffer):
                    self.state_queue.pop(0)
                    self.current_buffer = ""
            else:
                if self.current_buffer == current_req:
                    self.state_queue.pop(0)
                    self.current_buffer = ""

    def _get_params_from_function(self, fn_name: str) -> None:
        """Based on the function name, gets the parameters and builds the
        following elements of the state queue"""
        schema = self.models[fn_name]
        for i, (key, param_type) in enumerate(schema.items()):
            prefix = "," if i > 0 else ""
            is_last = (i == len(schema) - 1)

            if param_type == 'string':
                # this is amazing
                if prefix != "":
                    self.state_queue.append(f'{prefix}')
                self.state_queue.append('"')
                self.state_queue.append(f'{key}')
                self.state_queue.append('"')
                self.state_queue.append(':')
                self.state_queue.append('"')
                self.state_queue.append(('string', is_last))
            else:
                if prefix != "":
                    self.state_queue.append(f'{prefix}')
                self.state_queue.append('"')
                self.state_queue.append(f'{key}')
                self.state_queue.append('"')
                self.state_queue.append(':')
                self.state_queue.append((param_type, is_last))
        self.state_queue.append('}')
        self.state_queue.append('}')
