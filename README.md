# Gemini API Flask Project

This project provides a simple web interface and a command-line tool to interact with the Google Gemini API. It's designed to be a starting point for building more complex applications with Gemini.

## Project Structure

```
.
├── .dockerignore
├── Dockerfile
├── LICENSE
├── README.md
├── requirements.txt
├── scripts
│   └── gemini-test.py
└── src
    └── gemini_project
        ├── __init__.py
        ├── main.py
        ├── static
        │   ├── styles.css
        │   └── scripts.js
        └── templates
            └── gemini_frontend.html
```

-   `Dockerfile`: Defines the Docker image for the application.
-   `requirements.txt`: Lists the Python dependencies for the project.
-   `scripts/gemini-test.py`: A command-line tool for testing the Gemini API.
-   `src/gemini_project/main.py`: The main Flask application file.
-   `src/gemini_project/static`: Contains the static files for the web interface (CSS and JavaScript).
-   `src/gemini_project/templates`: Contains the HTML templates for the web interface.

## Getting Started

### Prerequisites

-   Python 3.9+
-   Docker (optional, for running in a container)
-   A Google Gemini API key

### Setting up the Environment

1.  **Clone the repository:**

    ```bash
    git clone https://github.com/google/generative-ai-docs
    cd generative-ai-docs/gemini/quickstart/python
    ```

2.  **Set up your Gemini API key:**

    You need to set the `GEMINI_API_KEY` environment variable. You can get an API key from the [Google AI Studio](https://aistudio.google.com/app/apikey).

    **Linux/macOS:**

    ```bash
    export GEMINI_API_KEY="YOUR_API_KEY"
    ```

    **Windows:**

    ```bash
    set GEMINI_API_KEY="YOUR_API_KEY"
    ```

3.  **Install the dependencies:**

    ```bash
    pip install -r requirements.txt
    ```

### Running the Application

You can run the application using Flask's built-in development server or by using Docker.

**Running with Flask:**

```bash
flask --app src/gemini_project/main.py run
```

The application will be available at `http://127.0.0.1:5000`.

**Running with Docker:**

1.  **Build the Docker image:**

    ```bash
    docker build -t gemini-flask-app .
    ```

2.  **Run the Docker container:**

    ```bash
    docker run -p 5000:5000 -e GEMINI_API_KEY="YOUR_API_KEY" gemini-flask-app
    ```

    The application will be available at `http://localhost:5000`.

## Using the Test Script

The `scripts/gemini-test.py` script provides a command-line interface to the Gemini API.

**Usage:**

```bash
python scripts/gemini-test.py "Your prompt" [options]
```

**Options:**

-   `--model`: The model to use (e.g., `gemini-pro`). Defaults to `gemini-pro`.
-   `--image`: Generate an image instead of text.
-   `--output`: The output file for the generated image (e.g., `my-image.png`). Defaults to `generated_image.png`.

**Examples:**

-   **Generate text:**

    ```bash
    python scripts/gemini-test.py "What is the meaning of life?"
    ```

-   **Generate an image:**

    ```bash
    python scripts/gemini-test.py "A picture of a cat playing a guitar" --image
    ```

-   **Generate an image with a specific output file:**

    ```bash
    python scripts/gemini-test.py "A picture of a dog on a skateboard" --image --output my_dog.png
    ```

## License

This project is licensed under the Apache 2.0 License. See the `LICENSE` file for details.


## 1. Prerequisites

You must have the following installed:

* **Python 3.9+** (For running the `gemini-test.py` script locally).
* **Docker or Podman** (For running the web application).
* **A Gemini API Key** (Set as an environment variable).

### Setting the GEMINI_API_KEY

The backend and CLI script both require the `GEMINI_API_KEY` environment variable to be set. The API key is stored as an enviroment variable for security.
More information can be found at https://ai.google.dev/gemini-api/docs/api-key

**Linux/macOS (For current session):**
```bash
export GEMINI_API_KEY="YOUR_API_KEY_HERE"
Windows (Command Prompt):
Bash

set GEMINI_API_KEY="YOUR_API_KEY_HERE"
2. Using the CLI Script (scripts/gemini-test.py)
The standalone Python script is useful for quick, command-line testing.

Usage:

Bash

# Default model (gemini-2.5-flash)
python scripts/gemini-test.py "Explain why the sky is blue."

# Specify a different model
python scripts/gemini-test.py --model gemini-2.5-pro "Write a full whitepaper on the future of AI."

# Image Generation Example (will save a .png file)
python scripts/gemini-test.py --model gemini-2.5-flash-image-preview "A photorealistic image of a futuristic castle on a moonlit ocean."
3. Running the Web UI with Podman/Docker
The web application is containerized using the provided Dockerfile and is designed to run on port 5000 inside the container.

Step 1: Build the Container Image
This command builds the image, tags it as gemini-frontend, and passes your local GEMINI_API_KEY environment variable into the image using a build argument.

Bash

podman build -t gemini-frontend --build-arg GEMINI_API_KEY=$GEMINI_API_KEY .
# OR (for Docker)
# docker build -t gemini-frontend --build-arg GEMINI_API_KEY=$GEMINI_API_KEY .
Step 2: Run the Container
Run the image, mapping the container's internal port 5000 to an external port (e.g., 8080) on your host machine. You can manually replace $GEMINI_API_KEY with your API key if you wish. It is recomened to use an enviroment variable (attackers can check command line history for previously used keys. Ask Gemini why this is best practice if you need).

Bash

podman run -d -p 8080:5000 --name gemini-app -e GEMINI_API_KEY=$GEMINI_API_KEY gemini-frontend
# OR (for Docker)
# docker run -d -p 8080:5000 --name gemini-app gemini-frontend
Step 3: Access the Application
Open your web browser and navigate to:

http://localhost:8080

You can now use the interface to test multimodal (image + text) and text-only models, as well as the new image generation model.
