Multiple parts:

# Tokenize
Split the prompt into tokens.

# Tokens to ID
Convert the tokens to numerical ID.

# Token selection
Using logits (the probability of the relevancy of the token), this is how/where we chose which token we want to use. By default, we tend to use the most probable token. But here, we use constrained decoding to alter the selection process.
## Constrained Decoding
The process of, when looking at the next token, only select those who respect the given conditions.
Here, the conditions are :
- Respecting the structure
- Respecting the expected schema

Filter those who do not fit.

What does that mean here ? We created a Pydantic model, that describes how our output should look (ie, prompt, then function name, then function arguments), and use it as an output indication. In other LLMs, we can simply use the `output_type` and pass the model, I'm unsure this works in our case.

# Questions
Is structured output the same as constrained decoding, but at a higher level ? How to implement constrained decoding with the given LLM ?

# 
