AI Error Handler
AI Error Handler is a Python package that uses AI (Llama 3) to automatically detect and provide explanations for errors in Python code. It enhances debugging by offering AI-generated suggestions directly in the terminal.

Features
🚀 AI-powered error explanations
🔥 No need for explicit try-except blocks
⚡ FastAPI-based web API support
🎯 Works seamlessly with llama-cpp-python
Installation
You can install the package via pip:

sh
Copy
Edit
pip install ai-error-handler
Usage
1. Using AI Error Handler in Python
python
Copy
Edit
from ai_error_handler import AIErrorHandler

AIErrorHandler.enable()  # Automatically detects and explains errors

# Example: This will trigger an error, and AI will suggest a fix
print(undefined_variable)
2. Running the Web API
If you want to use AI Error Handler as an API:

sh
Copy
Edit
uvicorn ai_error_handler.api:app --host 0.0.0.0 --port 8000
Then visit: http://127.0.0.1:8000/docs

Requirements
Python 3.8+
llama-cpp-python
fastapi
uvicorn
Contributing
Feel free to contribute by opening an issue or pull request on GitHub.

License
This project is licensed under the MIT License.

