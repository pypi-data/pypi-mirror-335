from setuptools import setup, find_packages

# Read the requirements from the requirements.txt file
with open("requirements.txt") as f:
    requirements = f.read().splitlines()

setup(
    name="traceback_assistant",
    version="0.1.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="A package to explain Python tracebacks using OpenAI.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/traceback_assistant",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "traceback-assistant=traceback_assistant.assistant:TracebackAssistant",
        ],
    },
)
