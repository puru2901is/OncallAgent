import re
import os
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()

# gemini_token = os.getenv("GOOGLE_API_KEY")

# genai.configure(api_key={gemini_token})
genai.configure(api_key=os.environ["GOOGLE_API_KEY"])


def read_log_file(file_path):
    """Reads the log file and returns its content."""
    with open(file_path, "r", encoding="utf-8") as file:
        return file.readlines()

def preprocess_logs(log_lines):
    """Extracts only error-related lines from logs."""
    error_patterns = [r"ERROR", r"FAILURE", r"Exception", r"Traceback"]  # Add more if needed
    filtered_logs = [line for line in log_lines if any(re.search(pattern, line, re.IGNORECASE) for pattern in error_patterns)]
    return "\n".join(filtered_logs)

def split_into_chunks(text, max_tokens=4000):
    """Splits text into chunks that fit within OpenAI's token limit."""
    words = text.split()
    chunks = []
    while words:
        chunk = words[:max_tokens]  # Take max allowed tokens
        chunks.append(" ".join(chunk))
        words = words[max_tokens:]
    return chunks

def analyze_errors_with_openai(error_log_chunk):
    """Sends log chunk to OpenAI API for error analysis."""
    prompt = f"""
    You are an expert DevOps AI assistant. Analyze the following Jenkins build error log and provide in the json
    1. The root cause of the failure.
    2. Possible solutions or debugging steps.

    Log:
    """
    
    prompt += "\n".join(error_log_chunk)
    
    payload = {"inputs": prompt}
    model = genai.GenerativeModel("gemini-1.5-flash")
    response = model.generate_content(contents={prompt})
    

    return response.text

def main():
    file_path = "./app.log"  # Replace with your actual log file path
    log_lines = read_log_file(file_path)
    
    preprocessed_logs = preprocess_logs(log_lines)
    
    if not preprocessed_logs.strip():
        print("No relevant error logs found.")
        return
    
    log_chunks = split_into_chunks(preprocessed_logs)

    print (log_chunks)
    
    print("Analyzing Errors...")
    for i, chunk in enumerate(log_chunks):
        print(f"\n--- Analysis for Chunk {i+1} ---")
        analysis = analyze_errors_with_openai(chunk)
        print(analysis)

if __name__ == "__main__":
    main()
