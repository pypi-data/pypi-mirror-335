from llama_cpp import Llama

# Initialize the Llama model
llama = Llama(model_path=r"C:\Users\unela\OneDrive\Desktop\ai_error_handler\meta-llama-3-8b_q8_0.gguf")

def get_ai_suggestions(error_message: str):
    # Use Llama to generate a suggestion for an error message
    prompt = f"Error: {error_message}\n\nProvide suggestions for fixing this error."
    response = llama(prompt)
    suggestions = response['choices'][0]['text'].strip()
    return suggestions

