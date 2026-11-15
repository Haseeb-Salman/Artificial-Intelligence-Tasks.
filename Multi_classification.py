# =========================================================
#        MULTI-CLASS IMAGE CLASSIFICATION GRADIO APP
# =========================================================

import numpy as np
import gradio as gr
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image

# =========================================================
# LOAD TRAINED MODEL
# =========================================================

model = load_model(
    r"D:\Artificial Intelligence\Deep Learning\Models\resnet.keras"
)

print("Model Loaded Successfully!")

# =========================================================
# CLASS NAMES
# IMPORTANT:
# Write classes in SAME ORDER as training dataset
# =========================================================

class_names = [
    "apple",
    "banana",
    "carrot",
    "capsicum",
    "orange",
    "potato",
    "tomato"
]

# =========================================================
# PREDICTION FUNCTION
# =========================================================

def predict(img):

    # Resize image
    img = img.resize((224, 224))

    # Convert image to array
    img_array = image.img_to_array(img) / 255.0
    img_array = np.expand_dims(img_array, axis=0)

    # Predict probabilities
    predictions = model.predict(img_array)[0]

    # Highest probability index
    predicted_index = np.argmax(predictions)

    # Predicted class name
    predicted_class = class_names[predicted_index]

    # Confidence
    confidence = float(predictions[predicted_index]) * 100

    # Create result dictionary
    results = {}

    for i, class_name in enumerate(class_names):
        results[class_name] = f"{predictions[i] * 100:.2f}%"

    # Final prediction
    results["Prediction"] = predicted_class
    results["Confidence"] = f"{confidence:.2f}%"

    return results

# =========================================================
# GRADIO INTERFACE
# =========================================================

app = gr.Interface(
    fn=predict,
    inputs=gr.Image(type="pil"),
    outputs="json",
    title="Multi-Class Fruit & Vegetable Classifier",
    description="Upload an image to classify fruits and vegetables using ResNet50"
)

# =========================================================
# LAUNCH APP
# =========================================================

app.launch()# =========================================================
#        MULTI-CLASS IMAGE CLASSIFICATION GRADIO APP
# =========================================================

import numpy as np
import gradio as gr
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image

# =========================================================
# LOAD TRAINED MODEL
# =========================================================

model = load_model(
    r"D:\Artificial Intelligence\Deep Learning\Models\resnet.keras"
)

print("Model Loaded Successfully!")

# =========================================================
# CLASS NAMES
# IMPORTANT:
# Write classes in SAME ORDER as training dataset
# =========================================================

class_names = [
    "apple",
    "banana",
    "carrot",
    "capsicum",
    "orange",
    "potato",
    "tomato"
]

# =========================================================
# PREDICTION FUNCTION
# =========================================================

def predict(img):

    # Resize image
    img = img.resize((224, 224))

    # Convert image to array
    img_array = image.img_to_array(img) / 255.0
    img_array = np.expand_dims(img_array, axis=0)

    # Predict probabilities
    predictions = model.predict(img_array)[0]

    # Highest probability index
    predicted_index = np.argmax(predictions)

    # Predicted class name
    predicted_class = class_names[predicted_index]

    # Confidence
    confidence = float(predictions[predicted_index]) * 100

    # Create result dictionary
    results = {}

    for i, class_name in enumerate(class_names):
        results[class_name] = f"{predictions[i] * 100:.2f}%"

    # Final prediction
    results["Prediction"] = predicted_class
    results["Confidence"] = f"{confidence:.2f}%"

    return results

# =========================================================
# GRADIO INTERFACE
# =========================================================

app = gr.Interface(
    fn=predict,
    inputs=gr.Image(type="pil"),
    outputs="json",
    title="Multi-Class Fruit & Vegetable Classifier",
    description="Upload an image to classify fruits and vegetables using ResNet50"
)

# =========================================================
# LAUNCH APP
# =========================================================

app.launch()