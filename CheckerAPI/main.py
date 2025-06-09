from flask import Flask, request, jsonify
import keras
import numpy as np
import cv2
from PIL import Image
import io

app = Flask(__name__)

# Loading BoneX model
model = keras.models.load_model('BoneX_Final_ModelV4.h5')


# Preprocessing function (same as used in your model pipeline)
def preprocess(image):
    # Convert to grayscale
    image = image.convert("L")

    # Resize to match model input shape
    image = image.resize((224, 224))

    # Convert to NumPy array
    image = np.array(image, dtype=np.uint8)

    # Apply CLAHE
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    image = clahe.apply(image)

    # Normalize to [0, 1]
    image = (image - image.min()) / (image.max() - image.min())

    # Expand dimensions for model input compatibility
    image = np.expand_dims(image, axis=-1)  # Add channel dimension
    image = np.expand_dims(image, axis=0)  # Add batch dimension
    return image


# API route to receive image and predict
@app.route('/predict', methods=['POST'])
def predict():
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400

    file = request.files['file']
    image = Image.open(io.BytesIO(file.read()))  # Read image from request

    # Preprocess and predict
    processed_image = preprocess(image)
    prediction = model.predict(processed_image)
    result = int(prediction[0][0] > 0.5)  # Convert to 0 or 1
    result_text = "there's a fracture!" if result == 0 else "there's no fracture!"

    return jsonify({'prediction': result_text})


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True, port=5000)
