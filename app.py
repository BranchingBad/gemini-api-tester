# app.py

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import sys
import os
import time
from google import genai
# Import types for configuration, and PIL for image processing
from google.genai import types 
from google.genai.errors import APIError 
from PIL import Image
from io import BytesIO
import base64


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


# Define the model ID for image generation (Updated to current standard)
IMAGE_MODEL_ID = "imagen-3.0-generate-002" 

@app.route('/', defaults={'path': ''})
def serve_static(path):
    """Serves the HTML frontend."""
    return send_from_directory(app.static_folder, 'gemini_frontend.html')

@app.route('/gemini_call', methods=['POST'])
def gemini_call():
    """Handles the API call to the Gemini service."""
    if GEMINI_CLIENT is None:
        return jsonify({"error": "Gemini client not initialized. Check GEMINI_API_KEY."}), 503

    try:
        data = request.get_json()
        prompt = data.get('prompt')
        model_name = data.get('model', 'gemini-2.5-flash')
        image_base64 = data.get('image_base64')

        if not prompt:
            return jsonify({"error": "Prompt is required."}), 400

        start_time = time.time()
        
        # --- Image Generation Logic ---
        if model_name == IMAGE_MODEL_ID:
            # Generate the image based on the prompt
            result = GEMINI_CLIENT.models.generate_images(
                model=IMAGE_MODEL_ID,
                prompt=prompt,
                config=dict(
                    number_of_images=1,
                    output_mime_type="image/jpeg",
                    aspect_ratio="1:1"
                )
            )

            end_time = time.time()
            duration = end_time - start_time

            img_bytes = result.generated_images[0].image.image_bytes
            img_base64 = base64.b64encode(img_bytes).decode('utf-8')
            
            return jsonify({
                "result_type": "image",
                "image_base64": img_base64,
                "duration": f"{duration:.2f}"
            })
        
        # --- Text/Multimodal Generation Logic ---
        else:
            contents = [prompt]
            if image_base64:
                # Decode base64 string back to bytes and load as PIL Image
                img_data = base64.b64decode(image_base64)
                img = Image.open(BytesIO(img_data))
                # Insert the image part at the beginning for multimodal models
                contents.insert(0, img)

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