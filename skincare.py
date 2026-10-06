import os
import tensorflow as tf
from tensorflow.keras.preprocessing.image import img_to_array
from flask import Flask, request, jsonify
from PIL import Image
import numpy as np
import base64
import io
from flask_cors import CORS  

# 🔥 Inisialisasi Flask
app = Flask(__name__)
CORS(app)

# Load model
MODEL_PATH = 'C:/Users/Andini/Documents/skin_analysis_model.keras'
try:
    model = tf.keras.models.load_model(MODEL_PATH)
    print("Model loaded successfully!")
except Exception as e:
    print(f"Error loading model: {e}")
    model = None

class_labels = ['berminyak', 'jerawat', 'kulit kering', 'kulit sehat']

def decode_image(base64_image):
    try:
        if base64_image.startswith('data:image'):
            base64_image = base64_image.split(',')[1]
        img_data = base64.b64decode(base64_image)
        img = Image.open(io.BytesIO(img_data))
        img = img.resize((224, 224))  
        img_array = np.array(img) / 255.0  

        # 🔥 Hitung rata-rata warna RGB
        avg_color = np.mean(img_array, axis=(0, 1))  # Rata-rata di seluruh gambar
        print("Average RGB:", avg_color)

        return np.expand_dims(img_array, axis=0), avg_color
    except Exception as e:
        raise ValueError(f"Invalid image data: {e}")

@app.route('/analyze/', methods=['POST'])
def analyze():
    if model is None:
        return jsonify({'error': 'Model gagal dimuat'}), 500
    
    try:
        data = request.get_json()
        imageBase64 = data.get('image')
        if not imageBase64:
            return jsonify({'error': 'Gambar tidak ditemukan'}), 400

        img_array, avg_color = decode_image(imageBase64)

        # 🔥 Debugging
        print("Image shape:", img_array.shape)

        predictions = model.predict(img_array)
        print("Raw predictions:", predictions)

        predicted_class = np.argmax(predictions, axis=1)[0]
        confidence = predictions[0][predicted_class] * 100
        detected_condition = class_labels[predicted_class]

        recommendations = {
            'berminyak': "Gunakan pembersih wajah yang mengontrol minyak.",
            'jerawat': "Gunakan produk dengan salicylic acid.",
            'kulit kering': "Gunakan pelembap untuk kulit kering.",
            'kulit sehat': "Kulit anda sehat, tetap jaga kebersihannya."
        }
        recommendation = recommendations.get(detected_condition, "Tidak ada rekomendasi.")

        return jsonify({
            'condition': detected_condition,
            'confidence': round(confidence, 2),
            'recommendation': recommendation,
            'average_rgb': {
                'red': round(avg_color[0] * 255, 2),
                'green': round(avg_color[1] * 255, 2),
                'blue': round(avg_color[2] * 255, 2)
            }
        })

    except ValueError as ve:
        return jsonify({'error': str(ve)}), 400
    except Exception as e:
        return jsonify({'error': f'Terjadi kesalahan: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5004)
