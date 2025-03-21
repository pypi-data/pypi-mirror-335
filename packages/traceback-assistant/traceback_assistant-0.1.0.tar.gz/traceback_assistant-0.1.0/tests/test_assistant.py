import pytest
from traceback_assistant.assistant import explain_errors

def test_explain_errors():
    @explain_errors
    def faulty_function():
        return 1 / 0  # Division by zero error

    with pytest.raises(ZeroDivisionError):
        faulty_function()
