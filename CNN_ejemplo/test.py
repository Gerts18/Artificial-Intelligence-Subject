import cv2
import numpy as np
from keras.models import load_model
import matplotlib.pyplot as plt

# Load trained model
model = load_model("animal_classifier_optimized.h5")  # Cambiar extensión

# Labels (classes in the same order you trained them)
labels = ["catarina", "gato", "hormiga","perro","tortuga"] 

# Target CNN input size
target_w = 128
target_h = 128

def preprocess_image(img_path):
    img = cv2.imread(img_path)

    if img is None:
        raise ValueError("Image not found:", img_path)

    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    # Resize with padding to 21x28
    old_h, old_w = img.shape[:2]
    scale = min(target_w / old_w, target_h / old_h)
    new_w = int(old_w * scale)
    new_h = int(old_h * scale)
    resized = cv2.resize(img, (new_w, new_h))

    padded = np.zeros((target_h, target_w, 3), dtype=np.uint8)
    x_offset = (target_w - new_w) // 2
    y_offset = (target_h - new_h) // 2
    padded[y_offset:y_offset+new_h, x_offset:x_offset+new_w] = resized

    # Normalize for the CNN (0–1)
    padded = padded.astype("float32") / 255.0

    # Add batch dimension → (1, 21, 28, 3)
    padded = np.expand_dims(padded, axis=0)

    return padded

# ---- Test ----
img_path = "CNN_ejemplo\\test-animals\\hormiga3.jpg"

X = preprocess_image(img_path)

prediction = model.predict(X)
predicted_class = np.argmax(prediction)
accuracy = prediction[0][predicted_class] * 100

print(f"Predicted class: {labels[predicted_class]}")
print(f"Prediction vector: {prediction}")
print(f"Accuracy: {accuracy:.2f}%")

# Show the image
img_display = cv2.cvtColor(cv2.imread(img_path), cv2.COLOR_BGR2RGB)
plt.imshow(img_display)
plt.text(img_display.shape[1] - 10, 30, labels[predicted_class], 
         fontsize=14, color='white', ha='right', va='top',
         bbox=dict(boxstyle='round', facecolor='black', alpha=0.7))
plt.axis("off")
plt.show()
