from resources.llm_sdk import Small_LLM_Model as llm 

def main():
    print("Hello")
    llm_i = llm()
    encoded = llm_i._encode("HELLO")
    print("ENCODED STR ->", encoded)

if __name__ == '__main__':
    main()
