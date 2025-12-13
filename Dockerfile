# Dockerfile

# Stage 1: Build the Python application
FROM python:3.9-slim AS build

WORKDIR /app

# COPY requirements first to leverage Docker's layer caching
COPY requirements.txt .
# Install dependencies (will now include Pillow)
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire src directory
COPY src/ .

# Stage 2: Serve the front end and run the backend
FROM python:3.9-slim

WORKDIR /app

# Create a non-root user
RUN useradd --create-home appuser
USER appuser

# Copy dependencies from the build stage
COPY --from=build /usr/local/lib/python3.9/site-packages /usr/local/lib/python3.9/site-packages

# Copy the application code
COPY --from=build /app/gemini_project/ /app/gemini_project/

# Set the working directory to the project folder
WORKDIR /app/gemini_project

EXPOSE 5000

ENV FLASK_APP=main.py

# Use waitress to run the application
CMD ["waitress-serve", "--host=0.0.0.0", "--port=5000", "main:app"]
