# gemini-test.py

from google import genai
import os
import sys
import time

# Define the default model
DEFAULT_MODEL = "gemini-2.5-flash"
MODEL_ARG_FLAG = "--model" # Flag to look for the model name

# --- 1. API Key Check (Unchanged) ---
if not os.getenv("GEMINI_API_KEY"):
    print("Error: The GEMINI_API_KEY environment variable is not set.")
    print("To set it for the current terminal session (variable will be lost on closing):")
    
    # Check if the OS is POSIX (Linux, macOS, etc.)
    if os.name == 'posix':
        print("    export GEMINI_API_KEY=\"YOUR_API_KEY\"")
        print("\nTo set it permanently (for new terminal sessions) on Linux/macOS:")
        print("    1. Run this command (replace YOUR_API_KEY):")
        print("       echo 'export GEMINI_API_KEY=\"YOUR_API_KEY\"' >> ~/.bashrc")
        print("    2. Then run: source ~/.bashrc")

    # Check if the OS is NT (Windows)
    elif os.name == 'nt':
        print("    set GEMINI_API_KEY=\"YOUR_API_KEY\"")
        print("\nTo set it permanently (for new terminal sessions) on Windows:")
        print("    Run this command in Command Prompt or PowerShell (replace YOUR_API_KEY):")
        print("    setx GEMINI_API_KEY \"YOUR_API_KEY\"")
        print("    (Note: You must open a new terminal window for this to take effect.)")
    
    sys.exit(1)


# --- 2. Argument Parsing (Updated model list in usage messages) ---
model_name = DEFAULT_MODEL
prompt_start_index = 1

# Check for model flag and extract model name if present
if len(sys.argv) > 2 and sys.argv[1].lower() == MODEL_ARG_FLAG:
    model_name = sys.argv[2]
    prompt_start_index = 3 # Prompt content starts after --model <MODEL_NAME>
elif len(sys.argv) < 2 or sys.argv[1].lower() == MODEL_ARG_FLAG:
    # Handle cases where only the script name is provided, or just --model
    print("Error: No prompt provided.")
    print(f"Usage: python gemini-test.py \"<YOUR_PROMPT_HERE>\"")
    print(f"Optional: python gemini-test.py {MODEL_ARG_FLAG} <MODEL_NAME> \"<YOUR_PROMPT_HERE>\"")
    print(f"Available models: {DEFAULT_MODEL}, gemini-2.5-flash-lite, gemini-2.0-flash, gemini-2.0-flash-lite")
    sys.exit(1)

# Collect all remaining arguments as the prompt content
prompt_content = " ".join(sys.argv[prompt_start_index:])

if not prompt_content:
    print("Error: No prompt provided.")
    print(f"Usage: python gemini-test.py \"<YOUR_PROMPT_HERE>\"")
    print(f"Optional: python gemini-test.py {MODEL_ARG_FLAG} <MODEL_NAME> \"<YOUR_PROMPT_HERE>\"")
    print(f"Available models: {DEFAULT_MODEL}, gemini-2.5-flash-lite, gemini-2.0-flash, gemini-2.0-flash-lite")
    sys.exit(1)

# --- 3. Run Gemini Client with Timer (Unchanged) ---
client = genai.Client()

print(f"Sending request to '{model_name}' for: '{prompt_content[:50]}...'")
print("-" * 20)

# Start the timer
start_time = time.time()

# Make the API call
response = client.models.generate_content(
    model=model_name, # Use the dynamic model_name
    contents=prompt_content
)

# Stop the timer
end_time = time.time()
duration = end_time - start_time

# --- 4. Print Results (Unchanged) ---
print(response.text)
print("-" * 20)
print(f"Request successful. Model: {model_name}. Time taken: {duration:.2f} seconds.")