# Galamo - Galaxy Morphology Predictor

**Galamo** is a Python package that utilizes deep learning to classify galaxy morphologies based on input images. It is designed for astronomers, researchers, and space enthusiasts who want an easy-to-use tool for automatic galaxy classification.

## Features

- Pre-trained deep learning model for galaxy morphology classification.
- Automatic image preprocessing (resizing, normalization, and format conversion).
- Simple and intuitive API requiring only an image file as input.
- Supports multiple galaxy morphology types.
- Compatible with Python 3.6+.

## Installation

### Install from PyPI

To install the package using pip:

```bash
pip install galamo
```

### Install from Source

Alternatively, if you want to install from the source:

```bash
git clone https://github.com/jsdingra11/galamo.git
cd galamo
pip install .
```

## Usage Guide

### Import and Initialize the Model

```python
from galamo import GalaxyMorph

# Initialize the model
model = GalaxyMorph()
```

### Predict Galaxy Morphology from an Image

```python
result = model.predict("galaxy.jpg")
print(f"Predicted Morphology: {result}")
```

### Example Output

```
Predicted Morphology: Spiral Galaxy
```

## How It Works

1. The model loads a pre-trained deep learning model for galaxy classification.
2. It preprocesses the input image (resizing, RGB conversion, and normalization).
3. The processed image is passed through the neural network to generate a prediction.
4. The predicted class index is converted to its corresponding galaxy morphology name using a label encoder.

## Requirements

To ensure smooth operation, make sure you have the following dependencies installed:

- Python 3.6+
- TensorFlow
- NumPy
- OpenCV
- Joblib

## Model Details

- The model was trained on a dataset of galaxy images labeled with different morphology types.
- It employs a Convolutional Neural Network (CNN) to extract features and classify images.
- The label encoder maps numerical predictions to meaningful class names (e.g., Spiral, Elliptical, Irregular, and further subclassifications).

## Contributing

We welcome contributions! If you want to improve the model or add new features:

1. Fork the repository.
2. Create a feature branch (`git checkout -b feature-name`).
3. Commit your changes (`git commit -m 'Added new feature'`).
4. Push the branch (`git push origin feature-name`).
5. Create a pull request.

## License

This project is licensed under the MIT License – see the LICENSE file for details.

## Contact & Support

- **Author:** Jashanpreet Singh Dingra
- **Email:** [astrodingra@gmail.com](mailto\:astrodingra@gmail.com)
- **GitHub:**  [https://github.com/jsdingra11](https://github.com/jsdingra11)

For any issues or feature requests, please open an issue on GitHub.

