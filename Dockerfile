# Use a slim Python base image
FROM python:3.9-slim-bullseye

# Set the working directory in the container
WORKDIR /app

# Install system dependencies required for Tesseract OCR and PyMuPDF
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        tesseract-ocr \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements file and install Python packages
# This layer is cached to speed up subsequent builds
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files into the container
COPY . .

# Set PYTHONPATH to include the app directory
ENV PYTHONPATH=/app

# Define the entry point for the container
ENTRYPOINT ["python", "run.py"]

# Example default command (can be overridden at runtime)
CMD ["--help"]