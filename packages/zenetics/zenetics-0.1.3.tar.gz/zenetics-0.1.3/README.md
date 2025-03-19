# Zenetics SDK

Zenetics SDK is a Python library that provides a simple interface to interact with Zenetics API.

### Installation

```commandline
pip install zenetics
```

### Usage

Define the following environment variables: `ZENETICS_API_KEY`, `ZENETICS_APP_ID`.

```python
from zenetics import TestSuiteRunner


def generate(input: str) -> str:
    # Call your LLM model here and return the generated output.
    return "Generated output from LLM model."


runner = TestSuiteRunner(["smoke"])
runner.run(generate)
```
