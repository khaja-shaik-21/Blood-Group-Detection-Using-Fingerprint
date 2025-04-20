from django.shortcuts import render
from django.core.files.storage import FileSystemStorage
import os
from tensorflow.keras.models import load_model
import numpy as np
from PIL import Image, UnidentifiedImageError
import base64
from io import BytesIO
import requests

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

MODEL_PATH = os.path.join('detector', 'static', 'detector', 'models', 'blood_group_model.h5')
model = None

def load_model_if_needed():
    global model
    if model is None:
        if not os.path.exists(MODEL_PATH):
            raise FileNotFoundError(f"Model file not found at {MODEL_PATH}")
        model = load_model(MODEL_PATH)
        print(model.summary())  # Debug: Print model architecture

def preprocess_image(image_data):
    """Preprocess image from either BytesIO (file upload) or Base64 string."""
    print(f"Type of image_data: {type(image_data)}")  # Debug
    try:
        if isinstance(image_data, str):  # Base64 string
            base64_string = image_data.split(',')[1] if ',' in image_data else image_data
            img_data = base64.b64decode(base64_string)
            img = Image.open(BytesIO(img_data)).convert('L')
        else:  # BytesIO from file upload
            img = Image.open(image_data).convert('L')
        # Resize to match model input: 224x224
        img = img.resize((224, 224))  # Width, Height in PIL for model
        img_array = np.array(img) / 255.0
        img_array = np.expand_dims(img_array, axis=0)  # Shape: (1, 224, 224)
        img_array = np.expand_dims(img_array, axis=-1)  # Shape: (1, 224, 224, 1)
        # Resize for display to match fixed preview size
        img_for_display = img.resize((300, 200), Image.LANCZOS)  # Fixed display size
        buffered = BytesIO()
        img_for_display.save(buffered, format="PNG")
        base64_img = f"data:image/png;base64,{base64.b64encode(buffered.getvalue()).decode('utf-8')}"
        print(f"Processed image shape: {img_array.shape}")  # Debug
        return img_array, base64_img
    except UnidentifiedImageError as e:
        raise Exception(f"PIL cannot identify image: {str(e)}")

def predict_blood_group(request):
    if request.method == 'POST':
        try:
            load_model_if_needed()
            fingerprint_base64 = None
            if 'fingerprint' in request.FILES:
                fingerprint = request.FILES['fingerprint']
                if not fingerprint.content_type.startswith('image/'):
                    return render(request, 'detector/index.html', {'error': 'Please upload an image file.'})
                file_content = fingerprint.read()
                file_io = BytesIO(file_content)
                print(f"File content length: {len(file_content)}")  # Debug
                img_array, fingerprint_base64 = preprocess_image(file_io)
            elif 'fingerprint_base64' in request.POST and request.POST['fingerprint_base64']:
                img_array, fingerprint_base64 = preprocess_image(request.POST['fingerprint_base64'])
            else:
                return render(request, 'detector/index.html', {'error': 'No fingerprint provided.'})

            print(f"Input shape to model: {img_array.shape}")  # Debug
            prediction = model.predict(img_array)
            blood_group = decode_prediction(prediction)
            return render(request, 'detector/index.html', {
                'blood_group': blood_group,
                'fingerprint_base64': fingerprint_base64
            })
        except Exception as e:
            return render(request, 'detector/index.html', {'error': str(e)})
    return render(request, 'detector/index.html')

def capture_fingerprint(request):
    return render(request, 'detector/index.html')

def decode_prediction(prediction):
    blood_groups = ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-']
    return blood_groups[np.argmax(prediction)]