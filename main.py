from src.call_me_maybe import ModelOrchestrator, Wrapper, EngineConfig, SchemasBuilder, DataParser, VocabularyLoader

def main():
    prompt = input("What do you want to get from the model ?")
    # config = EngineConfig("Say hello back", 50)
    model_wrapper = Wrapper()
    new_model = ModelOrchestrator(prompt, model_wrapper, 50)
    print(new_model.answer_prompt())

if __name__ == '__main__':
    main()


    # print(parser.state_queue)
