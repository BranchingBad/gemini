"""
Flask application for interacting with the Gemini API.
"""

import base64
import logging
import os
import sys
import time
from io import BytesIO

# Import SDK components
import google.generativeai as genai
from flask import Flask, jsonify, render_template, request
from flask_cors import CORS
from google.api_core import exceptions as google_exceptions

# Import for image handling
from PIL import Image

# --- Constants ---
IMAGE_MODEL_ID = os.environ.get("IMAGE_MODEL_ID", "gemini-1.5-flash")

# --- Logging Configuration ---
logging.basicConfig(level=logging.INFO, stream=sys.stderr)


def _configure_gemini():
    """
    Configures the Gemini API with the API key.

    Raises:
        ValueError: If the GEMINI_API_KEY environment variable is not set.
    """
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY environment variable not set.")
    genai.configure(api_key=api_key)


# --- Flask Application Setup ---
app = Flask(
    __name__,
    template_folder=os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "templates"
    ),
    static_folder=os.path.join(os.path.dirname(os.path.abspath(__file__)), "static"),
)
CORS(app)


@app.route("/")
def serve_static():
    """Serves the HTML frontend."""
    return render_template("gemini_frontend.html")


@app.route("/api/models", methods=["GET"])
def get_models():
    """
    Returns a list of available Gemini models.

    Returns:
        A JSON list of model names or an error message.
    """
    try:
        _configure_gemini()
        models = [
            m.name
            for m in genai.list_models()
            if "generateContent" in m.supported_generation_methods
        ]
        return jsonify(models)
    except ValueError as e:
        logging.error(f"Error initializing Gemini client: {e}")
        return (
            jsonify({"error": "GEMINI_API_KEY environment variable not set."}),
            401,
        )
    except google_exceptions.GoogleAPICallError as e:
        logging.error(f"Gemini API Error fetching models: {e}")
        return (
            jsonify(
                {
                    "error": f"An error occurred while fetching models from the Gemini API: {e}"
                }
            ),
            502,
        )
    except Exception as e:
        logging.error(f"Error fetching models: {e}")
        return (
            jsonify(
                {"error": f"An unexpected error occurred while fetching models: {e}"}
            ),
            500,
        )


@app.route("/api/image_models", methods=["GET"])
def get_image_models():
    """
    Returns a list of available Gemini image models.

    Returns:
        A JSON list of image model names or an error message.
    """
    try:
        _configure_gemini()
        models = [
            m.name
            for m in genai.list_models()
            if "generateContent" in m.supported_generation_methods
            and "vision" in m.name.lower()
        ]
        return jsonify(models)
    except ValueError as e:
        logging.error(f"Error initializing Gemini client: {e}")
        return (
            jsonify({"error": "GEMINI_API_KEY environment variable not set."}),
            401,
        )
    except google_exceptions.GoogleAPICallError as e:
        logging.error(f"Gemini API Error fetching models: {e}")
        return (
            jsonify(
                {
                    "error": f"An error occurred while fetching models from the Gemini API: {e}"
                }
            ),
            502,
        )
    except Exception as e:
        logging.error(f"Error fetching models: {e}")
        return (
            jsonify(
                {"error": f"An unexpected error occurred while fetching models: {e}"}
            ),
            500,
        )


def _generate_image(prompt: str) -> dict:
    """
    Generates an image using the Gemini API.

    Args:
        prompt: The text prompt for image generation.

    Returns:
        A dictionary containing the generated image data or an error message.
    """
    model = genai.GenerativeModel(IMAGE_MODEL_ID)
    response = model.generate_content(prompt)

    generated_image_base64 = None
    mime_type = "image/png"

    for part in response.candidates[0].content.parts:
        if hasattr(part, "inline_data") and part.inline_data:
            generated_image_base64 = base64.b64encode(part.inline_data.data).decode(
                "utf-8"
            )
            mime_type = part.inline_data.mime_type
            break

    if generated_image_base64:
        return {
            "result_type": "image",
            "result": generated_image_base64,
            "mime_type": mime_type,
            "text_response": response.text if hasattr(response, "text") else "",
        }
    else:
        return {
            "result_type": "text",
            "result": (
                response.text
                if hasattr(response, "text") and response.text
                else "Image generation failed. Model returned no image data."
            ),
            "warning": "Model did not return image data, returning text response instead.",
        }


def _generate_text(model_name: str, prompt: str, image_base64: str | None) -> dict:
    """
    Generates text using the Gemini API, optionally with an image.

    Args:
        model_name: The name of the Gemini model to use.
        prompt: The text prompt.
        image_base64: Optional base64-encoded image data.

    Returns:
        A dictionary containing the generated text or an error message.
    """
    model = genai.GenerativeModel(model_name)
    contents = []

    if image_base64:
        img_data = base64.b64decode(image_base64)
        img = Image.open(BytesIO(img_data))
        contents.append(img)

    contents.append(prompt)
    response = model.generate_content(contents)

    return {"result_type": "text", "result": response.text}


@app.route("/gemini_call", methods=["POST"])
def gemini_call():
    """
    Handles the API call to the Gemini service.

    Returns:
        A JSON response with the generated content or an error message.
    """
    try:
        _configure_gemini()
    except ValueError as e:
        logging.error(f"Error initializing Gemini client: {e}")
        return (
            jsonify({"error": "GEMINI_API_KEY environment variable not set."}),
            401,
        )

    try:
        data = request.json
        model_name = data.get("model", "gemini-1.5-flash")
        prompt = data.get("prompt", "")
        image_base64 = data.get("image_data")

        if not prompt:
            return jsonify({"error": "Prompt cannot be empty."}), 400

        # Validate model name
        available_models = [
            m.name
            for m in genai.list_models()
            if "generateContent" in m.supported_generation_methods
        ]
        if model_name not in available_models:
            return jsonify({"error": f"Invalid model name: {model_name}"}), 400

        start_time = time.time()

        # Check if this is an image generation request
        if model_name == IMAGE_MODEL_ID and not image_base64:
            result = _generate_image(prompt)
        else:
            result = _generate_text(model_name, prompt, image_base64)

        end_time = time.time()
        duration = end_time - start_time
        result["duration"] = f"{duration:.2f}"

        return jsonify(result)

    except google_exceptions.GoogleAPICallError as e:
        logging.error(f"Gemini API Error: {e}")
        return jsonify({"error": f"Gemini API Error: {e}"}), 502
    except Exception as e:
        logging.error(f"Internal server error: {e}")
        return jsonify({"error": f"An internal server error occurred: {e}"}), 500


if __name__ == "__main__":
    app.run(debug=True)
