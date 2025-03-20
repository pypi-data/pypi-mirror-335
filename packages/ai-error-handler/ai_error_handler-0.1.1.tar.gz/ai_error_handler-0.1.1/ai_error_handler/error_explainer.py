import sys
import subprocess
import traceback 


def explain_error(error_message: str) -> str:
    """
    Uses Llama 3 (via Ollama) to explain an error message and suggest a fix.
    """
    try:
        prompt = f"Explain this programming error and suggest a fix:\n{error_message}"
        
        # Run Llama 3 model using Ollama's CLI
        result = subprocess.run(
            ["ollama", "run", "llama3", prompt],
            capture_output=True,
            text=True
        )
        
        return result.stdout.strip()
    
    except Exception as e:
        return f"⚠️ AI Suggestion Unavailable: {str(e)}"

def handle_uncaught_exception(exc_type, exc_value, exc_traceback):
    """Handles uncaught exceptions and provides AI-generated suggestions."""
    print("\n⚠️ ERROR DETECTED! ⚠️\n")
    
    # Correct way to format the traceback
    error_trace = "".join(traceback.format_exception(exc_type, exc_value, exc_traceback))
    print(error_trace)  # Print the full traceback

    # Call AI-powered error explanation (modify based on your Llama 3 setup)
    explanation = explain_error(str(exc_value))
    
    print("\n💡 AI Suggestion:")
    print(explanation)

# Override Python's default exception handler
sys.excepthook = handle_uncaught_exception
