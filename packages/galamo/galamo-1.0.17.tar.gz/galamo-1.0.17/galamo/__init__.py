import os
import tensorflow as tf
from .model import predict_and_display, preprocess_image

# Define the model path relative to the package
MODEL_PATH = os.path.join(os.path.dirname(__file__), "model.keras")

# Load the model globally so users don't need to load it manually
model = tf.keras.models.load_model(MODEL_PATH)

# Expose the key functions and model for easy import
__all__ = ["predict_and_display", "preprocess_image", "model"]
