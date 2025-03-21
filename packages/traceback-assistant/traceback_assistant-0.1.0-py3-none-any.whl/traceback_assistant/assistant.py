import traceback
import openai
import os

class TracebackAssistant:
    def __init__(self, openai_api_key=None):
        # Check if the API key is provided either as an argument or in environment variables
        self.api_key = openai_api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError(
                "OpenAI API key is missing. Please set the API key by:\n"
                "- Passing it as an argument to TracebackAssistant.\n"
                "- Or, setting it as an environment variable 'OPENAI_API_KEY'."
            )
        openai.api_key = self.api_key

    @staticmethod
    def explain_exception(e: Exception) -> str:
        """Explain the given exception by fetching insights from OpenAI."""
        tb = "".join(traceback.format_exception(type(e), e, e.__traceback__))
        prompt = (
            f"The following Python traceback occurred:\n\n{tb}\n\n"
            "Explain the reason for this error and provide potential solutions. "
            "Respond concisely and in bullet points."
        )
        try:
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a Python debugging assistant."},
                    {"role": "user", "content": prompt},
                ],
            )
            return response.choices[0].message["content"]
        except Exception as api_error:
            return f"Error contacting OpenAI API: {api_error}"

def explain_errors(func):
    """A decorator to catch and explain exceptions using TracebackAssistant."""
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            try:
                assistant = TracebackAssistant()
                explanation = assistant.explain_exception(e)
                print("\n--- Traceback Assistant Suggestions ---\n")
                print(explanation)
                print("\n---------------------------------------\n")
            except ValueError as ve:
                print("\n--- Traceback Assistant Error ---\n")
                print(str(ve))
                print("\n-----------------------------------\n")
            raise
    return wrapper
