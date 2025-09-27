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
import base64 # <--- NEW: For encoding images to send to frontend


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


# Define the model ID for image generation
IMAGE_MODEL_ID = "imagen-4.0-generate-001" 
# NOTE: "gemini-2.5-flash-image-preview" is another option.

@app.route('/', defaults={'path': ''})
def serve_static(path):
    """Serves the HTML frontend."""
    # This serves the frontend file 'gemini_frontend.html'
    return send_from_directory(app.static_folder, 'gemini_frontend.html')

                                                                                                                                                                            
@app.route('/gemini_call', methods=['POST'])
def gemini_call():
    """API endpoint to handle Gemini API calls (Text and Image)."""
    data = request.get_json()
    prompt = data.get('prompt', '')
    model_name = data.get('model', 'gemini-2.5-flash')
    
    if not prompt:
        return jsonify({"error": "Prompt cannot be empty."}), 400
    
    if GEMINI_CLIENT is None or not os.getenv("GEMINI_API_KEY"):
        return jsonify({
            "error": "GEMINI_API_KEY environment variable is not set on the server."
        }), 500

    try:
        start_time = time.time()
        
        # --- NEW: Image Generation Logic ---
        if model_name == IMAGE_MODEL_ID:
            # For image generation, use generate_images
            image_config = types.GenerateImagesConfig(
                number_of_images=1,
                aspect_ratio="1:1" # Use 1:1, 4:3, 16:9, etc.
            )

            response = GEMINI_CLIENT.models.generate_images(
                model=IMAGE_MODEL_ID,
                prompt=prompt,
                config=image_config
            )
            
            # Process the generated image
            generated_image = response.generated_images[0]
            # Open the image data from bytes
            img = Image.open(BytesIO(generated_image.image.image_bytes))
            
            # Save the image to a bytes buffer
            buffered = BytesIO()
            img.save(buffered, format="PNG") # Use PNG or JPEG
            
            # Encode the image bytes to base64
            img_base64 = base64.b64encode(buffered.getvalue()).decode('utf-8')

            end_time = time.time()
            duration = end_time - start_time

            # Return a response containing the image data
            return jsonify({
                "result_type": "image", # <--- NEW KEY to tell frontend what to expect
                "image_base64": img_base64,
                "duration": f"{duration:.2f}"
            })
        
        # --- Existing Text Generation Logic ---
        else:
            # Use the initialized client for text generation
            response = GEMINI_CLIENT.models.generate_content(
                model=model_name,
                contents=prompt
            )

            end_time = time.time()
            duration = end_time - start_time
            
            response_text = response.text
            
            return jsonify({
                "result_type": "text", # <--- NEW KEY
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
    # Run the application
    # Note: Flask's default development server is not suitable for production.
    # For containerization, it's run via gunicorn/waitress or similar in a...
    app.run(debug=True, host='0.0.0.0', port=5000)