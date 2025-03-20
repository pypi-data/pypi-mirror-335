# Define a function to combine and present results
from typing import List

from litegen import LLM
from pydantic import BaseModel
from wordllama import WordLlama


def get_query_relevant_chunks_list(query, text, num_variations=5, debug=False,
                                   api_key=None,base_url=None,
                                   model=None):
    llm = LLM(api_key=api_key,base_url=base_url)
    wllm = WordLlama.load()
    class QuestionGenerationList(BaseModel):
        questions: List[str]  # List of generated questions

    prompt = f"Generate {num_variations} variations of the following query in english: {query}"
    response = llm(prompt, response_format=QuestionGenerationList,
                   model=model).questions

    if debug:
        print("Generated Query Variations:")
        for i, variation in enumerate(response, 1):
            print(f"{i}. {variation}")

    combined_results = []
    chunks = wllm.split(text)
    for variation in response:
        relevant_chunks = wllm.topk(variation, chunks, 1)
        combined_results.extend(relevant_chunks)

    combined_results = list(set(combined_results))
    return combined_results

def relevant_chunk(query, context, num_variations=5, debug=False,
                       api_key="dsollama", base_url=None,
                       model=None
                       ):
    cs = get_query_relevant_chunks_list(query=query,
                                        text=context, num_variations=num_variations, debug=debug,
                                        api_key=api_key, base_url=base_url,
                                        model=model
                                        )
    return "\n".join(cs)