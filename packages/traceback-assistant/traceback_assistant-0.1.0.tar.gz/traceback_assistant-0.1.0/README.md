# Traceback Assistant

A Python package that explains tracebacks using OpenAI's API.

## Installation

```bash
pip install traceback_assistant
```

## Usage

### Set Open AI Key in environmental variable
export OPENAI_API_KEY="your_openai_api_key"
### Or pass as parameter 
from traceback_assistant import TracebackAssistant

assistant = TracebackAssistant(openai_api_key="your_openai_api_key")



from traceback_assistant import TracebackAssistant, explain_errors

@explain_errors
def faulty_function():
    return 1 / 0

faulty_function()

# Build Package:
python setup.py sdist bdist_wheel
# Publish to PyPI
twine upload dist/*
# Install package
pip install traceback_assistant


