from litegen import completion
from litegen.model._types import ModelType
import concurrent.futures

from .visionlite.prompts import SEARCH_QUERY_VARATIONS_GEN_PROMPT


def generate_k(query, k: int, **kwargs) -> list:
    def fetch_completion(q):
        return completion(prompt=q, **kwargs)

    with concurrent.futures.ThreadPoolExecutor() as executor:
        results = list(executor.map(fetch_completion, [query] * k))

    return [r.choices[0].message.content for r in results]


from dataclasses import dataclass


@dataclass
class Config:
    model: ModelType = "qwen2.5-coder:7b-instruct"
    temperature: float = 0.8
    max_tokens: int = 100
    gpu: bool = True


class TestTimeCompute:
    def __init__(self, config):
        self.gen_queries_prompt = SEARCH_QUERY_VARATIONS_GEN_PROMPT
        self.config = config

    def generate_queries(self, user_query, k=5) -> list:
        kwargs = {'model': self.config.model,
                  'temperature': self.config.temperature, 'max_tokens': self.config.max_tokens,
                  'gpu': self.config.gpu}
        return generate_k(query=user_query, k=k, system_prompt=self.gen_queries_prompt, **kwargs)


if __name__ == '__main__':
    ttc = TestTimeCompute(Config())
    n = ttc.generate_queries('how ai agents learn in environment, '
                             'i want to knwo learning agents concept and algorithms', k=10)
    print(n)
