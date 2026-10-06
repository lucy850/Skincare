import os
import tensorflow as tf
from tensorflow.keras import layers, models
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint
import numpy as np
import matplotlib.pyplot as plt
from tensorflow.keras.preprocessing.image import load_img, img_to_array
import cv2
from sklearn.utils.class_weight import compute_class_weight


print("TensorFlow version:", tf.__version__)
print("Using GPU:", tf.config.list_physical_devices('GPU'))

train_dir = "data-set/latihan"
test_dir = "data-set/test"

if not os.path.exists(train_dir) or not os.path.exists(test_dir):
    raise FileNotFoundError("Dataset tidak ditemukan!")

train_datagen = ImageDataGenerator(
    rescale=1.0/255.0,
    shear_range=0.2,
    zoom_range=0.2,
    horizontal_flip=True,
    brightness_range=[0.5, 1.5],
    rotation_range=20,
    fill_mode='nearest'
)

test_datagen = ImageDataGenerator(rescale=1.0/255.0)

# Load data training
train_data = train_datagen.flow_from_directory(
    train_dir, target_size=(224, 224), batch_size=32, class_mode='categorical'
)

# Load data testing
test_data = test_datagen.flow_from_directory(
    test_dir, target_size=(224, 224), batch_size=32, class_mode='categorical'
)

# --- 3. Hitung Class Weights ---
class_weights = compute_class_weight(
    class_weight='balanced',
    classes=np.unique(train_data.classes),
    y=train_data.classes
)
class_weight_dict = {i: class_weights[i] for i in range(len(class_weights))}

# --- 4. Gunakan Model Transfer Learning MobileNetV2 ---
base_model = tf.keras.applications.MobileNetV2(
    input_shape=(224, 224, 3), include_top=False, weights='imagenet'
)
base_model.trainable = True  # Buka beberapa layer terakhir

for layer in base_model.layers[:-30]:  # Hanya latih ulang 30 layer terakhir
    layer.trainable = False

model = models.Sequential([
    base_model,
    layers.GlobalAveragePooling2D(),
    layers.Dense(128, activation='relu'),
    layers.Dropout(0.5),
    layers.Dense(train_data.num_classes, activation='softmax')
])

# --- 5. Compile Model ---
model.compile(
    optimizer=tf.keras.optimizers.Adam(learning_rate=0.0001),  # Kurangi LR agar stabil
    loss='categorical_crossentropy',
    metrics=['accuracy']
)

# --- 6. Tambahkan Callbacks ---
callbacks = [
    EarlyStopping(monitor='val_loss', patience=5, restore_best_weights=True),
    ModelCheckpoint('C:/Users/Andini/Documents/skin_analysis_model.keras', save_best_only=True)
]

# --- 7. Latih Model ---
history = model.fit(
    train_data, epochs=30, batch_size=32, validation_data=test_data,
    class_weight=class_weight_dict, callbacks=callbacks
)

# --- 8. Evaluasi Model ---
test_loss, test_accuracy = model.evaluate(test_data)
print(f"Test Loss: {test_loss:.4f}, Test Accuracy: {test_accuracy:.2%}")

# --- 9. Visualisasi Hasil Pelatihan ---
plt.figure(figsize=(12, 4))
plt.subplot(1, 2, 1)
plt.plot(history.history['accuracy'], label='Training Accuracy')
plt.plot(history.history['val_accuracy'], label='Validation Accuracy')
plt.xlabel('Epoch')
plt.ylabel('Accuracy')
plt.legend()
plt.title('Accuracy over Epochs')

plt.subplot(1, 2, 2)
plt.plot(history.history['loss'], label='Training Loss')
plt.plot(history.history['val_loss'], label='Validation Loss')
plt.xlabel('Epoch')
plt.ylabel('Loss')
plt.legend()
plt.title('Loss over Epochs')
plt.tight_layout()
plt.show()

# --- 10. Simpan Model ---
model.save('C:/Users/Andini/Documents/skin_analysis_model.keras')
print("Model berhasil disimpan!")

# --- 11. Fungsi Deteksi Kulit dengan Edge Detection ---
def preprocess_image(image_path):
    """Preprocessing gambar untuk meningkatkan deteksi jerawat."""
    try:
        img = load_img(image_path, target_size=(224, 224))
        img = img.convert('RGB')
        img_array = img_to_array(img) / 255.0

        # Edge detection untuk highlight jerawat
        gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
        edges = cv2.Canny(gray.astype('uint8'), 50, 150)

        # Tambahkan edge detection ke gambar RGB
        img_array[:, :, 0] += edges
        img_array[:, :, 1] += edges
        img_array[:, :, 2] += edges

        img_array = np.expand_dims(img_array, axis=0)  # Tambah batch dimension
        return img_array
    except Exception as e:
        print("Error dalam preprocessing:", str(e))
        return None

def predict_skin_condition(image_path):
    """Prediksi kondisi kulit dari gambar input."""
    img_array = preprocess_image(image_path)
    if img_array is None:
        return {'error': 'Gagal memproses gambar'}

    predictions = model.predict(img_array)
    predicted_class = np.argmax(predictions, axis=1)[0]
    confidence = predictions[0][predicted_class] * 100

    class_labels = list(train_data.class_indices.keys())
    detected_condition = class_labels[predicted_class]

    # Jika confidence rendah, label "Tidak Yakin"
    if confidence < 80:
        return {'condition': 'Tidak Yakin', 'confidence': round(confidence, 2)}
    else:
        return {'condition': detected_condition, 'confidence': round(confidence, 2)}

# --- 12. Contoh Pengujian dengan Gambar ---
test_image_path = "data-set/test/jerawat/jerajwt 2.jpg"  # Ganti dengan gambar uji
if os.path.exists(test_image_path):
    result = predict_skin_condition(test_image_path)
    print("Hasil Deteksi:", result)
else:
    print("Gambar uji tidak ditemukan.")
