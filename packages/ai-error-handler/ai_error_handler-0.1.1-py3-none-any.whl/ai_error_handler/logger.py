import logging

# Configure logging
logging.basicConfig(
    filename="error_log.txt", 
    level=logging.ERROR, 
    format="%(asctime)s - %(levelname)s - %(message)s"
)

def log_error(error_message: str, ai_suggestion: str):
    """
    Logs the error and AI-generated explanation to a file.
    """
    logging.error(f"Error: {error_message}\nAI Suggestion: {ai_suggestion}\n")
