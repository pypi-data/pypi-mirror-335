# EvalLite 🚀

[![PyPI version](https://badge.fury.io/py/evallite.svg)](https://badge.fury.io/py/evallite)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python Versions](https://img.shields.io/pypi/pyversions/evallite.svg)](https://pypi.org/project/evallite/)

An efficient, zero-cost LLM evaluation framework combining the simplicity of [DeepEval](https://github.com/confident-ai/deepeval) with the power of free Hugging Face models through [AILite](https://github.com/yourusername/ailite).

[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE)

## 🌟 Key Features

- **Zero-Cost Evaluation**: Leverage free Hugging Face models for LLM evaluation
- **Simple Integration**: Drop-in replacement for DeepEval's evaluation capabilities
- **Extensive Model Support**: Access to leading open-source models including:
  - Meta Llama 3.1 70B Instruct
  - Qwen 2.5 72B Instruct
  - Mistral Nemo Instruct
  - Phi-3.5 Mini Instruct
  - And more!
- **Comprehensive Metrics**: Full compatibility with DeepEval's evaluation metrics
- **Async Support**: Built-in asynchronous evaluation capabilities

## 📥 Installation

```bash
pip install evallite
```

## 🚀 Quick Start

Here's a simple example to get you started with EvalLite:

```python
from evallite import (
    assert_test,
    EvalLiteModel,
    LLMTestCase,
    evaluate,
    AnswerRelevancyMetric
)

# Initialize metric with a specific model
answer_relevancy_metric = AnswerRelevancyMetric(
    threshold=0.7,
    model=EvalLiteModel(model="microsoft/Phi-3.5-mini-instruct")
)

# Create a test case
test_case = LLMTestCase(
    input="What if these shoes don't fit?",
    actual_output="We offer a 30-day full refund at no extra costs.",
    retrieval_context=["All customers are eligible for a 30 day full refund at no extra costs."]
)

# Run evaluation
evaluate([test_case], [answer_relevancy_metric])
```


## 📊 Advanced Usage

### Custom Schema Support

EvalLite supports custom response schemas using Pydantic models:

```python
from pydantic import BaseModel
from typing import List

class Statements(BaseModel):
    statements: List[str]

# Use with schema
result = evaluator.generate(
    prompt="List three facts about climate change",
    schema=Statements
)
```

### Async Evaluation

```python
async def evaluate_async():
    response = await evaluator.a_generate(
        prompt="What is the capital of France?",
        schema=Statements
    )
    return response
```

### Batch Evaluation

```python
from evallite import EvaluationDataset

# Create multiple test cases
test_cases = [
    LLMTestCase(
        input="Question 1",
        actual_output="Answer 1",
        retrieval_context=["Context 1"]
    ),
    LLMTestCase(
        input="Question 2",
        actual_output="Answer 2",
        retrieval_context=["Context 2"]
    )
]

# Create dataset
dataset = EvaluationDataset(test_cases=test_cases)

# Evaluate all at once
evaluate(dataset, [answer_relevancy_metric])
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the Apache 2.0 License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [DeepEval](https://github.com/confident-ai/deepeval) for the evaluation framework
- [AILite](https://github.com/yourusername/ailite) for providing free model access
- The open-source community for making powerful language models accessible
