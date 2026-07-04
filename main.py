from src.call_me_maybe import ModelOrchestrator, Wrapper, EngineConfig, SchemasBuilder, DataParser

def main():
  model_wrapper = Wrapper()
  prompt = input("What do you want to get from the model ?")
  # config = EngineConfig("Say hello back", 50)
  new_model = ModelOrchestrator(prompt, model_wrapper, 50)
  print(new_model.answer_prompt())

if __name__ == '__main__':
  models = SchemasBuilder.build_schema('./data/input/functions_definition.json')
  parser = DataParser(models)
  parser.advance_state('{"fn": "')
  parser.advance_state('fn_substitute_string_with_regex')
  # print(parser.state_queue)
  # main()
