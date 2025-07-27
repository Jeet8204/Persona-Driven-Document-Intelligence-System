import os

# Base directory for models
MODEL_BASE_DIR = "models"

# Path to the Sentence Transformer model
SENTENCE_TRANSFORMER_MODEL_PATH = os.path.join(MODEL_BASE_DIR, "sentence_transformers", "all-MiniLM-L6-v2")

# Thresholds and parameters for PDF parsing
MIN_WORDS_FOR_SUBSECTION = 10
MIN_HEADING_FONT_SIZE = 12
HEADING_MAX_WORDS = 20
OCR_RESOLUTION_DPI = 300

# Default Persona and Job-to-be-done for testing
DEFAULT_PERSONA_ROLE = "Financial Analyst"
DEFAULT_JOB_TASK = "Extract key financial indicators and market trends."

# Default output filename
DEFAULT_OUTPUT_FILENAME = "analysis_output.json"