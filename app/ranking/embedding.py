
import os
import logging
import numpy as np
from sentence_transformers import SentenceTransformer
from typing import List, Union

# Set up a logger for cleaner, more controllable status messages
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class EmbeddingModel:
    """
    A robust wrapper for SentenceTransformer models that includes lazy loading,
    type hinting, logging, and performance optimizations via normalization.
    """
    def __init__(self, model_path: str):
        """
        Initializes the EmbeddingModel.

        Args:
            model_path: The local file path to the sentence-transformer model directory.
        """
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Model directory not found at path: {model_path}")
        self.model_path = model_path
        self.model: SentenceTransformer = None # Model is loaded on first use (lazy loading)

    def _load_model(self):
        """
        Private method to load the SentenceTransformer model into memory.
        This is called automatically only when embeddings are first requested.
        """
        logging.info(f"Loading sentence-transformer model from '{self.model_path}' into memory...")
        try:
            self.model = SentenceTransformer(self.model_path)
            logging.info("Model loaded successfully.")
        except Exception as e:
            logging.error(f"Fatal: Error loading embedding model from {self.model_path}: {e}")
            raise

    def get_embeddings(self, texts: Union[str, List[str]]) -> np.ndarray:
        """
        Generates normalized embeddings for a list of texts.
        If the model is not loaded, it will be loaded automatically.

        Args:
            texts: A single string or a list of strings to embed.

        Returns:
            A numpy array of normalized embeddings (unit vectors).
        """
        # Lazy loading: the model is only loaded into memory when it's actually needed.
        if self.model is None:
            self._load_model()

        # Ensure input is always a list for the encoder
        if isinstance(texts, str):
            texts = [texts]
        
        if not texts:
            return np.array([])

        # Encode the texts. Normalizing embeddings to unit vectors is crucial.
        # It allows for using a faster dot product for cosine similarity calculations.
        embeddings = self.model.encode(
            texts,
            convert_to_numpy=True,
            show_progress_bar=False,
            normalize_embeddings=True 
        )
        return embeddings