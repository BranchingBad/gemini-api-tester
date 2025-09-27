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
        print("    (Note: You must open a new terminal window for this to take effect)")
    
    sys.exit(1)


# --- 2. Command Line Argument Parsing ---

# Check if model flag is present
if MODEL_ARG_FLAG in sys.argv:
    try:
        # Get the index of the flag
        model_flag_index = sys.argv.index(MODEL_ARG_FLAG)
        # The model name should be the argument immediately following the flag
        model_name = sys.argv[model_flag_index + 1]
        # Set the starting index for the prompt content (after the model name)
        i = model_flag_index + 2
    except (ValueError, IndexError):
        print(f"Error: Missing model name after {MODEL_ARG_FLAG} flag.")
        print(f"Usage: python gemini-test.py {MODEL_ARG_FLAG} <MODEL_NAME> \"<YOUR_PROMPT_HERE>\"")
        print(f"Available models: {DEFAULT_MODEL}, gemini-2.5-pro, gemini-2.5-flash-lite")
        sys.exit(1)

# Check if only the prompt is present.
elif len(sys.argv) >= 2:
    # Example: python gemini-test.py "Hello"
    model_name = DEFAULT_MODEL
    i = 1 # Prompt starts at index 1 (after script name)
else:
    # This covers len(sys.argv) == 1 (only the script name)
    print("Error: No prompt provided.")
    print(f"Usage: python gemini-test.py \"<YOUR_PROMPT_HERE>\"")
    print(f"Optional: python gemini-test.py {MODEL_ARG_FLAG} <MODEL_NAME> \"<YOUR_PROMPT_HERE>\"")
    print(f"Available models: {DEFAULT_MODEL}, gemini-2.5-pro, gemini-2.5-flash-lite")
    sys.exit(1)

# Collect all remaining arguments as the prompt content
prompt_content = " ".join(sys.argv[i:])

if not prompt_content:
    print("Error: No prompt provided.")
    print(f"Usage: python gemini-test.py \"<YOUR_PROMPT_HERE>\"")
    print(f"Optional: python gemini-test.py {MODEL_ARG_FLAG} <MODEL_NAME> \"<YOUR_PROMPT_HERE>\"")
    print(f"Available models: {DEFAULT_MODEL}, gemini-2.5-pro, gemini-2.5-flash-lite")
    sys.exit(1)

# --- 3. Run Gemini Client with Timer (Unchanged) ---
client = genai.Client()

print(f"Sending request to '{model_name}' for: '{prompt_content[:50]}...'\n")
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
print(f"Model: {model_name}")
print(f"Tokens Used: {response.usage_metadata.prompt_token_count} (In), {response.usage_metadata.candidates_token_count} (Out)")
print(f"Total Tokens: {response.usage_metadata.total_token_count}")
print(f"API Call Duration: {duration:.2f} seconds")