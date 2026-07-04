from wrapper import Small_LLM_Model as llm
import numpy as np
import json

def boolean_filter(array, vocab_list, past_tensor) -> list[float]:
  print("Iteration")
  bool_array = np.char.startswith(vocab_list, "s")
  bool_array_s = np.char.startswith(vocab_list, " s")
  mask = bool_array | bool_array_s
  array[~mask] = -np.inf
  for tensor in past_tensor:
    array[tensor] *= (-1.2 if array[tensor] > 0 else 1.2)
  return array

# def main() -> None:
#   prompt = input("Please enter your prompt :")
#   model = ModelOrchestrator(prompt)
#   model.answer()

def main():
    prompt = '''Among these functions, which should I choose to have the sum of 3 and 2, and with what arguments should I call it ?
[
  {
    "fn_name": "fn_add_numbers",
    "args_names": [
      "a",
      "b"
    ],
    "args_types": {
      "a": "float",
      "b": "float"
    },
    "return_type": "float"
  },
  {
    "fn_name": "fn_get_square_root",
    "args_names": [
      "a"
    ],
    "args_types": {
      "a": "float"
    },
    "return_type": "float"
  },
  {
    "fn_name": "fn_greet",
    "args_names": [
      "name"
    ],
    "args_types": {
      "name": "str"
    },
    "return_type": "str"
  },
  {
    "fn_name": "fn_is_even",
    "args_names": [
      "n"
    ],
    "args_types": {
      "n": "int"
    },
    "return_type": "bool"
  },
  {
    "fn_name": "fn_multiply_numbers",
    "args_names": [
      "a",
      "b"
    ],
    "args_types": {
      "a": "float",
      "b": "float"
    },
    "return_type": "float"
  },
  {
    "fn_name": "fn_reverse_string",
    "args_names": [
      "s"
    ],
    "args_types": {
      "s": "str"
    },
    "return_type": "str"
  },
  {
    "fn_name": "fn_substitute_string_with_regex",
    "args_names": [
      "source_string",
      "regex",
      "replacement"
    ],
    "args_types": {
      "source_string": "str",
      "regex": "str",
      "replacement": "str"
    },
    "return_type": "str"
  }
]'''
    llm_i = llm()
    print(type(llm_i))
    encoded = llm_i._encode(prompt)
    # print("Encoded =", encoded)
    tensor_list = []
    with open(llm_i.get_path_to_vocabulary_json(), 'r') as vocab_file:
      vocab_dict = json.load(vocab_file)

    vocab_strings_list = sorted(vocab_dict, key=vocab_dict.get)
    

    for token in encoded[0]:
      tensor_list.append(token)

    tensor_size = len(llm_i.get_logits_from_input_ids(tensor_list))
    padding_needed = tensor_size - len(vocab_strings_list)
    # More elegant : since we already know how much padding is needed, we can use this one liner instead of iterating
    vocab_strings_list.extend([""] * padding_needed)
    vocab_strings = np.array(vocab_strings_list)
      
    # for _ in range(35):
    while True:
      logits = np.array(llm_i.get_logits_from_input_ids(tensor_list))
      # while len(vocab_strings_list) < len(logits):
      #   vocab_strings_list.append("")
      #   if len(vocab_strings_list) == len(logits):
      # should return a tensor, but only returns the logits from the last token ! No need to slice
      # new_logits = np.array(boolean_filter(logits, vocab_strings, tensor_list))
      argumaxu = int(np.argmax(logits))
      print("Token ->", argumaxu, "EOS ->", llm_i._tokenizer.eos_token_id)
      if argumaxu == llm_i._tokenizer.eos_token_id:
        break
      tensor_list.append(argumaxu)
      
    print("Decoded ->")
    for token in tensor_list:
      decoded = llm_i._decode(token)
      print(decoded, end="")
    

if __name__ == '__main__':
    main()
