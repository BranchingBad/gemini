#!/usr/bin/env python
"""
A command-line tool for testing the Gemini API.
"""

import argparse
import base64
import os
import sys
import time
from io import BytesIO

from google import genai
from google.genai.errors import APIError
from google.genai.types import GenerateContentConfig, Modality
from PIL import Image

# --- Constants ---
DEFAULT_MODEL = "gemini-pro"
IMAGE_MODEL_ID = os.environ.get("IMAGE_MODEL_ID", "gemini-pro-vision")


def _get_gemini_client() -> genai.Client:
    """
    Initializes and returns a Gemini client.

    Raises:
        ValueError: If the GEMINI_API_KEY environment variable is not set.

    Returns:
        A Gemini client instance.
    """
    if not os.getenv("GEMINI_API_KEY"):
        raise ValueError("GEMINI_API_KEY environment variable not set.")
    return genai.Client()


def _generate_image(client: genai.Client, prompt: str, output_path: str):
    """
    Generates an image using the Gemini API and saves it to a file.

    Args:
        client: The Gemini client.
        prompt: The text prompt for image generation.
        output_path: The path to save the generated image.
    """
    print(f"Generating image for prompt: '{prompt}'...")
    config = GenerateContentConfig(response_modalities=[Modality.TEXT, Modality.IMAGE])
    try:
        response = client.models.generate_content(
            model=IMAGE_MODEL_ID, contents=[prompt], config=config
        )
        generated_image_base64 = None
        for part in response.candidates[0].content.parts:
            if part.inline_data:
                generated_image_base64 = part.inline_data.data
                break
        if generated_image_base64:
            image_data = base64.b64decode(generated_image_base64)
            image = Image.open(BytesIO(image_data))
            image.save(output_path)
            print(f"Image saved to {output_path}")
        else:
            print("Image generation failed. Model returned no image data.")
    except APIError as e:
        print(f"Gemini API Error: {e}")
        sys.exit(1)


def _generate_text(client: genai.Client, model: str, prompt: str):
    """
    Generates text using the Gemini API.

    Args:
        client: The Gemini client.
        model: The name of the Gemini model to use.
        prompt: The text prompt.
    """
    print(f"Generating text for prompt: '{prompt}' using model '{model}'...")
    try:
        response = client.models.generate_content(model=model, contents=prompt)
        print(response.text)
    except APIError as e:
        print(f"Gemini API Error: {e}")
        sys.exit(1)


def main():
    """
    The main function of the script.
    """
    parser = argparse.ArgumentParser(description="Test the Gemini API.")
    parser.add_argument("prompt", type=str, help="The prompt to send to the model.")
    parser.add_argument(
        "--model",
        type=str,
        default=DEFAULT_MODEL,
        help=f"The model to use. Defaults to {DEFAULT_MODEL}.",
    )
    parser.add_argument(
        "--image", action="store_true", help="Generate an image instead of text."
    )
    parser.add_argument(
        "--output",
        type=str,
        default="generated_image.png",
        help="The output file for the generated image.",
    )
    args = parser.parse_args()

    try:
        client = _get_gemini_client()
    except ValueError as e:
        print(f"Error: {e}")
        sys.exit(1)

    start_time = time.time()

    if args.image:
        _generate_image(client, args.prompt, args.output)
    else:
        _generate_text(client, args.model, args.prompt)

    end_time = time.time()
    duration = end_time - start_time
    print(f"\nRequest took {duration:.2f} seconds.")


if __name__ == "__main__":
    main()
