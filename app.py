# app.py

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import sys
import os
import time
import base64
from io import BytesIO

# Import SDK components
from google import genai
from google.genai import types 
from google.genai.errors import APIError 

# Import for image handling
from PIL import Image 
from google.genai.types import GenerateContentConfig, Modality # Explicitly import for clarity


# --- Flask Application Setup ---

# The application loads the client from the environment variable GEMINI_API_KEY.
app = Flask(__name__, static_folder='static_html') 
CORS(app) 

# --- Gemini API Client Initialization ---
# Initialize GEMINI_CLIENT to None.
GEMINI_CLIENT = None 
try:
    # The client automatically uses the GEMINI_API_KEY environment variable.
    GEMINI_CLIENT = genai.Client()
    print("Gemini client initialized successfully.")
except Exception as e:
    # Print error but allow the application to start.
    print(f"Error initializing Gemini client: {e}", file=sys.stderr)


# Define the model ID for image generation (Updated)
IMAGE_MODEL_ID = "gemini-2.5-flash-image-preview" 

@app.route('/', defaults={'path': ''})
def serve_static(path):
    """Serves the HTML frontend."""
    # The file path is gemini_frontend.html inside the static_html directory
    return send_from_directory(app.static_folder, 'gemini_frontend.html')

@app.route('/gemini_call', methods=['POST'])
def gemini_call():
    """Handles the API call to the Gemini service."""
    if GEMINI_CLIENT is None:
        return jsonify({"error": "Gemini client is not initialized. Check server logs."}), 500

    try:
        data = request.json
        model_name = data.get('model', 'gemini-2.5-flash')
        prompt = data.get('prompt', '')
        image_base64 = data.get('image_data') # Base64 image data for multimodal input

        # A prompt is required for all calls
        if not prompt:
            return jsonify({"error": "Prompt cannot be empty."}), 400

        start_time = time.time()
        
        # --- Image Generation Logic (New) ---
        if model_name == IMAGE_MODEL_ID:
            # Configuration must explicitly request an image output
            config = GenerateContentConfig(
                response_modalities=[Modality.TEXT, Modality.IMAGE]
            )
            
            # Image generation models primarily use the text prompt
            response = GEMINI_CLIENT.models.generate_content(
                model=model_name,
                contents=[prompt],
                config=config
            )

            # Look for the generated image data in the response parts
            generated_image_base64 = None
            mime_type = 'image/png' # Default MIME type
            
            for part in response.candidates[0].content.parts:
                if part.inline_data:
                    # Found the image data
                    generated_image_base64 = part.inline_data.data
                    mime_type = part.inline_data.mime_type
                    break
            
            end_time = time.time()
            duration = end_time - start_time
            
            if generated_image_base64:
                return jsonify({
                    "result_type": "image",
                    "result": generated_image_base64, # Base64 string of the image
                    "mime_type": mime_type,
                    "duration": f"{duration:.2f}",
                    "text_response": response.text # Text description from the model
                })
            else:
                # If no image is generated, return text response or an error
                return jsonify({
                    "result_type": "text",
                    "result": response.text if response.text else "Image generation failed. Model returned no image data.",
                    "duration": f"{duration:.2f}",
                    "warning": "Model did not return image data, returning text response instead."
                })


        # --- Text/Multimodal Generation Logic ---
        else:
            contents = []
            
            # 1. Handle Multimodal Input (Image + Text)
            if image_base64:
                # Decode base64 string back to bytes and load as PIL Image
                img_data = base64.b64decode(image_base64)
                img = Image.open(BytesIO(img_data))
                # Insert the image part at the beginning
                contents.append(img)
                contents.append(prompt)
            else:
                 contents.append(prompt)
            
            # For standard text or multimodal input (image+text)
            response = GEMINI_CLIENT.models.generate_content(
                model=model_name,
                contents=contents
            )

            end_time = time.time()
            duration = end_time - start_time
            
            response_text = response.text
            
            return jsonify({
                "result_type": "text",
                "result": response_text,
                "duration": f"{duration:.2f}"
            })

    except APIError as e:
        print(f"Gemini API Error: {e}", file=sys.stderr)
        return jsonify({"error": f"Gemini API Error: {e}"}), 502
    except Exception as e:
        print(f"Internal server error: {e}", file=sys.stderr)
        return jsonify({"error": f"An internal server error occurred: {e}"}), 500


if __name__ == '__main__':
    # Ensure static_html directory exists for serving frontend
    if not os.path.exists('static_html'):
        os.makedirs('static_html')
    app.run(debug=True, host='0.0.0.0', port=5000)