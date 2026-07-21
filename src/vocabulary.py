import numpy as np
import json
from .wrapper import Small_LLM_Model


class VocabularyLoader:
    def __init__(self, wrapper_instance: Small_LLM_Model) -> None:
        self.wrapper_instance = wrapper_instance
        self.vocab_path = ""

    def load_vocab(self) -> None:
        with open(self.wrapper_instance.get_path_to_vocab_file(),
                  'r') as vocab_file:
            vocab_dict = json.load(vocab_file)

        vocab_strings_list = sorted(vocab_dict, key=vocab_dict.get)
        encoded = self.wrapper_instance.encode("Test")
        tensor_list = []
        for token in encoded[0]:
            tensor_list.append(token)

        tensor_size = len(
            self.wrapper_instance.get_logits_from_input_ids(tensor_list))
        padding_needed = tensor_size - len(vocab_strings_list)
        vocab_strings_list.extend([""] * padding_needed)
        self._vocab_array = np.array(vocab_strings_list)

    def get_vocab_array(self) -> np.ndarray:
        return self._vocab_array
