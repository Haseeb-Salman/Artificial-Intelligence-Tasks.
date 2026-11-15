# import numpy as np
# from tensorflow.keras.models import load_model
# from tensorflow.keras.preprocessing import image

# # Load trained model
# model_path = r"Icream_pizza.model.h5"
# model = load_model(model_path)

# print("Model Loaded Successfully!")

# # Image path
# img_path = r"test_digit.png"

# # Load image
# img = image.load_img(img_path, target_size=(150, 150))
# img_array = image.img_to_array(img) / 255.0
# img_array = np.expand_dims(img_array, axis=0)

# # Predict
# prediction = model.predict(img_array)[0][0]

# # Binary class probabilities
# class_1_prob = float(prediction)          # sigmoid output
# class_0_prob = 1 - class_1_prob

# print("\nBoth Class Probabilities:\n")
# print(f"Class 0 Probability: {class_0_prob * 100:.2f}%")
# print(f"Class 1 Probability: {class_1_prob * 100:.2f}%")

# # Final predicted class
# if prediction >= 0.5:
#     print("\nPredicted Class: 1")
#     print(f"Confidence: {class_1_prob * 100:.2f}%")
# else:
#     print("\nPredicted Class: 0")
#     print(f"Confidence: {class_0_prob * 100:.2f}%")


# gradio app
import numpy as np
import gradio as gr
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image

# Load model once
model = load_model("D:\Artificial Intelligence\Deep Learning\Models\Icream_pizza.model.h5")


def predict(img):
    # Resize to model input size
    img = img.resize((150, 150))
    
    # Convert to array
    img_array = image.img_to_array(img) / 255.0
    img_array = np.expand_dims(img_array, axis=0)

    # Prediction
    pred = model.predict(img_array)[0][0]

    class_1_prob = float(pred)
    class_0_prob = 1 - class_1_prob

    if pred >= 0.5:
        label = "Pizza"
    else:
        label = "No Pizza"

    return {
        "No Pizza": f"{class_0_prob * 100:.2f}%",
        "Pizza": f"{class_1_prob * 100:.2f}%",
        "Prediction": label
    }


# Gradio UI
app = gr.Interface(
    fn=predict,
    inputs=gr.Image(type="pil"),
    outputs="json",
    title="Binary Image Classifier Pizza",
    description="Upload an image to classify between 2 classes using CNN model"
)

app.launch(True)