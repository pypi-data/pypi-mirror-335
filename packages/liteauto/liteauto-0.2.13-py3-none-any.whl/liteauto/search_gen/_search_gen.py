import datetime
import time
from typing import Optional, List

from langchain_core.messages import SystemMessage, HumanMessage
from langchain_ollama import ChatOllama
from langchain_openai import ChatOpenAI


class SearchGen:
    """A class to generate search queries using ChatOllama"""

    def __init__(self, model: str = "llama3.2:3b-instruct-q4_K_M",
                 temperature: float = 0.1,
                 max_retries: int = 3, base_url="http://localhost:11434",
                 num_queries: Optional[int] = 5,
                 api_key="",
                 llm=None):
        """
        Initialize QueryGenerator.

        Args:
            model_name: Name of the Ollama model to use
            max_retries: Maximum number of retry attempts
        """
        self.n = num_queries
        self.chat_model = ChatOllama(model=model, temperature=temperature,
                                             base_url=base_url) if 'api' not in base_url else ChatOpenAI(
            model=model, temperature=temperature, base_url=base_url, openai_api_key=api_key
        )
        self.max_retries = max_retries

    def _get_system_prompt(self, n: int) -> str:
        """Get the system prompt for query generation"""
        return f'''Generate exactly {n} simple Google search queries based on the user query.
            today date is {datetime.datetime.now().strftime('%Y-%m-%d')}.
            Format the output as follows:

            Examples:
            <query>what is capital of france</query>
            1. capital of france
            2. paris france capital
            3. france capital city
            4. what is france capital city
            5. capital city of france

            <query>how to sum two arrays in python</query>
            1. python sum two arrays
            2. how to add arrays python
            3. python array addition code
            4. combine two arrays python
            5. python merge arrays tutorial'''

    def _parse_response(self, response: str, n: int) -> List[str]:
        """Parse the response into a list of queries"""
        queries = []
        for line in response.split('\n'):
            line = line.strip()
            if line and any(line.startswith(f"{i}.") for i in range(1, n + 1)):
                query = line.split('.', 1)[1].strip()
                queries.append(query.strip('"'))
        return queries

    def __call__(self, query: str, n: Optional[int] = None, ctx: str = "") -> List[str]:
        """
        Generate search queries with retry mechanism.

        Args:
            query: Input query string
            n: Number of queries to generate (default: 5)

        Returns:
            List of generated queries

        Raises:
            Exception: If generation fails after max retries
        """
        if n is None:
            n = self.n
        query = f'<query>{(ctx if ctx else "") + query}</query>'
        messages = [
            SystemMessage(content=self._get_system_prompt(n)),
            HumanMessage(content=query)
        ]

        retry_count = 0
        backoff_time = 1

        while retry_count < self.max_retries:
            try:
                if retry_count > 0:
                    print(f"\nRetry attempt {retry_count} of {self.max_retries}...")
                    time.sleep(backoff_time)
                    backoff_time *= 2

                response = self.chat_model.invoke(messages)
                queries = self._parse_response(response.content, n)

                if len(queries) == n:
                    if retry_count > 0:
                        print("Retry successful!")
                    return queries

                raise ValueError(f"Expected {n} queries, got {len(queries)}")

            except Exception as e:
                retry_count += 1
                if retry_count == self.max_retries:
                    print(f"\nFailed after {self.max_retries} attempts. Last error: {str(e)}")
                    return []
                print(f"Error occurred: {str(e)}")
