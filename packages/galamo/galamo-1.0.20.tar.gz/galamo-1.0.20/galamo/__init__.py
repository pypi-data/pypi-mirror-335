import os
import tensorflow as tf
from .model import predict_and_display, preprocess_image

# Get the absolute model path inside the package
MODEL_PATH = os.path.join(os.path.dirname(__file__), "model.keras")

# Load the model globally
if os.path.exists(MODEL_PATH):
    model = tf.keras.models.load_model(MODEL_PATH)
else:
    raise FileNotFoundError(f"Model file not found at {MODEL_PATH}")

# Expose key functions
__all__ = ["predict_and_display", "preprocess_image", "model"]
