import numpy as np
import json

class VocabularyLoader:
    def __init__(self, vocab_path: str) -> None:
        self.vocab_path = vocab_path

    def load_vocab(self, wrapper_instance) -> None:
        with open(wrapper_instance.get_path_to_vocabulary_json(), 'r') as vocab_file:
          vocab_dict = json.load(vocab_file)

        vocab_strings_list = sorted(vocab_dict, key=vocab_dict.get)
        for token in encoded[0]:
          tensor_list.append(token)

        tensor_size = len(wrapper_instance.get_logits_from_input_ids(tensor_list))
        padding_needed = tensor_size - len(vocab_strings_list)
        vocab_strings_list.extend([""] * padding_needed)
        self._vocab_array = np.array(vocab_strings_list)
    
    def get_vocab_array(self) -> np.array :
      return self._vocab_array

    def get_vocab_entry(self, id: int) -> str:
      return self._vocab_array[id]
