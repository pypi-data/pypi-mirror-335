import json

from deepeval import evaluate
from deepeval.metrics import AnswerRelevancyMetric
from deepeval.metrics.answer_relevancy.schema import Statements, Verdicts, AnswerRelvancyVerdict, Reason
from deepeval.test_case import LLMTestCase
from pydantic import BaseModel
from typing import Optional, List, Union, Type

from deepeval.models import DeepEvalBaseLLM
from litegen import completion
from litegen import ModelType


class Steps(BaseModel):
    steps: List[str]


class ReasonScore(BaseModel):
    reason: str
    score: int


class EvalLiteModel(DeepEvalBaseLLM):
    def __init__(
        self,
        model: Optional[ModelType] = None,
        *args,
        **kwargs,
    ):
        self.model_kwargs = kwargs
        self.model_name = model if model else "default"
        self.args = args
        self.kwargs = kwargs
        self.evaluation_cost = 0  # Initialize evaluation cost
        self._llm_func = kwargs.get("llm_func", None)
        super().__init__(self.model_name)

    def load_model(self):
        return self.model_name

    def llm_func(self, prompt, model) -> str:
        if self._llm_func:
            return self._llm_func(prompt=prompt,
                                  model=model,
                                  **self.model_kwargs)
        result = completion(model=model,
                            prompt=prompt,
                            **self.model_kwargs).choices[0].message.content
        return result

    def _parse_ai_response(self, response: str) -> dict:
        """Convert AI response to JSON format with better error handling"""
        try:
            # Remove markdown code block if present
            response = response.replace('```json', '').replace('```', '').strip()
            return json.loads(response)
        except json.JSONDecodeError:
            try:
                import re
                json_match = re.search(r'\{.*\}', response, re.DOTALL)
                if json_match:
                    return json.loads(json_match.group())
                return self._create_structured_response(response)
            except:
                return self._create_structured_response(response)

    def _create_structured_response(self, response: str) -> dict:
        """Create structured response based on content type"""
        lines = [line.strip() for line in response.split('\n') if line.strip()]

        # Try to identify steps format
        if any(line.startswith(str(i) + '.') for i in range(1, 10) for line in lines):
            steps = [line for line in lines if any(line.startswith(str(i) + '.') for i in range(1, 10))]
            return {"steps": steps}

        # Try to identify score/reason format
        import re
        score_match = re.search(r'\b([0-9]|10)\b', response)
        if score_match:
            score = int(score_match.group())
            reason = response.replace(score_match.group(), '').strip()
            return {"score": score, "reason": reason}

        return {"content": response}

    def _process_response(self, response: str, schema: Optional[Type[BaseModel]] = None) -> Union[BaseModel, str]:
        """Process response according to schema with improved handling"""
        if not schema:
            return response


        parsed_response = self._parse_ai_response(response)

        if schema.__name__ == 'Reason':
            return Reason(reason=parsed_response["reason"])
        elif schema.__name__ == 'Verdicts':
            verdicsts = [AnswerRelvancyVerdict(
                verdict=v,
                reason=r
            ) for v,r in parsed_response['verdicts']]
            return Verdicts(verdicts=verdicsts)
        elif schema.__name__ == 'Statements':
            return Statements(statements=parsed_response['statements'])

        elif schema.__name__ == 'Steps':
            if isinstance(parsed_response, dict) and 'steps' in parsed_response:
                return Steps(steps=parsed_response['steps'])
            return Steps(steps=[str(response)])

        elif schema.__name__ == 'ReasonScore':
            if isinstance(parsed_response, dict) and 'score' in parsed_response and 'reason' in parsed_response:
                return ReasonScore(score=parsed_response['score'], reason=parsed_response['reason'])
            # Handle non-standard response format
            score = parsed_response.get('score', 5)
            reason = parsed_response.get('reason', str(response))
            return ReasonScore(score=score, reason=reason)

        return response

    def generate(self, prompt: str, schema: Optional[Type[BaseModel]] = None, **kwargs) -> Union[BaseModel, str]:
        """Synchronous generation with schema support"""
        response = self.llm_func(prompt=prompt, model=self.model_name)
        processed_response = self._process_response(response, schema)
        return processed_response

    async def a_generate(self, prompt: str, schema: Optional[Type[BaseModel]] = None, **kwargs) -> Union[
        BaseModel, str]:
        """Asynchronous generation"""
        response = self.llm_func(prompt=prompt, model=self.model_name)
        processed_response = self._process_response(response, schema)
        return processed_response

    def get_model_name(self):
        return self.model_name

if __name__ == '__main__':

    # Initialize metric with a specific model
    answer_relevancy_metric = AnswerRelevancyMetric(
        threshold=0.7,
        model=EvalLiteModel(model='qwen2.5-coder:7b-instruct',
                            gpu=True)
    )

    # Create a test case
    test_case = LLMTestCase(
        input="What if these shoes don't fit?",
        actual_output="We offer a 30-day full refund at no extra costs.",
        retrieval_context=["All customers are eligible for a 30 day full refund at no extra costs."]
    )

    # Run evaluation
    evaluate([test_case], [answer_relevancy_metric])