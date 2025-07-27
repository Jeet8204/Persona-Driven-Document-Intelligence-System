from sentence_transformers import SentenceTransformer
import os

# The model to download
MODEL_NAME = 'all-MiniLM-L6-v2'
# The destination path
MODEL_PATH = os.path.join('models', 'sentence_transformers', MODEL_NAME)

def download_model():
    """
    Downloads the sentence-transformer model to the specified path.
    """
    print(f"Downloading model: {MODEL_NAME}")
    print(f"Destination: {MODEL_PATH}")

    if os.path.exists(MODEL_PATH):
        print("Model directory already exists. Skipping download.")
        return

    try:
        # This will download and save the model to the cache directory first,
        # then we can save it to our local directory.
        model = SentenceTransformer(MODEL_NAME)
        
        os.makedirs(MODEL_PATH, exist_ok=True)
        model.save(MODEL_PATH)
        print("✅ Model downloaded and saved successfully.")

    except Exception as e:
        print(f"❌ Error downloading model: {e}")

if __name__ == "__main__":
    download_model()