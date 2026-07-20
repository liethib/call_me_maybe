# from src import ModelOrchestrator, Wrapper, EngineConfig, flag_parser
from . import ModelOrchestrator, Wrapper, EngineConfig, flag_parser
from pydantic import ValidationError
import json
import sys


def main() -> None:
    input_path, output_path, functions_definition_path = flag_parser(sys.argv)
    with open(input_path) as prompts:
        # with open('./data/input/function_calling_tests.json') as prompts:
        formatted_prompts = json.load(prompts)

    # prompt = input("What do you want to get from the model ?")
    # config = EngineConfig("Say hello back", 50)
    try:
        model_wrapper = Wrapper()
        print("Current output file ->", output_path)
        with open(output_path, 'w') as file:
            file.write('[')
        with open(output_path, 'a') as file:
            for prompt in formatted_prompts:
                if prompt != formatted_prompts[0]:
                    file.write(',')
                config = EngineConfig(
                    prompt=prompt['prompt'],
                    max_tokens=100,
                    functions_path=functions_definition_path
                )
                new_model = ModelOrchestrator(config, model_wrapper)
                prompt_answer = new_model.answer_prompt()
                file.write(prompt_answer.strip())
            file.write(']')
    except ValidationError as e:
        print("Error with the configuration", e)
    except ValueError as e:
        print("Error calculating logits", e)
    except Exception as e:
        print("An unexpected error happened :", e)

    with open(output_path, "r") as file:
        data = json.load(file)
    with open(output_path, "w") as file:
        json.dump(data, file, indent=4)


if __name__ == '__main__':
    main()
