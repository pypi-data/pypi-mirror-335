import sys
import requests

def ai_error_handler(exc_type, exc_value, exc_traceback):
    """Automatically send uncaught errors to the AI error-handling API."""
    url = "http://your-api-url.com/suggestions/"  # Replace with your actual API URL
    params = {"error_message": str(exc_value)}
    
    try:
        response = requests.get(url, params=params)
        suggestion = response.json().get("suggestions", "No suggestion available.")
        print(f"\n💡 AI Suggestion: {suggestion}\n")
    except Exception as e:
        print(f"Error communicating with AI API: {e}")

# Set sys.excepthook to our AI error handler
sys.excepthook = ai_error_handler
