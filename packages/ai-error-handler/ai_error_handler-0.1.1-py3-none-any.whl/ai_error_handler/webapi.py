import sys
import os

# Ensure the ai_error_handler package is discoverable
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from fastapi import FastAPI
from ai_error_handler.api import get_ai_suggestions  # Correct import path

app = FastAPI()

@app.get("/suggestions/")
def get_suggestions(error_message: str):
    suggestions = get_ai_suggestions(error_message)
    return {"suggestions": suggestions}
