# Face.ra — Analisis Wajah dan Rekomendasi Skincare

Face.ra adalah proyek web sederhana untuk mengklasifikasikan kondisi kulit dari gambar. Pengguna memilih gambar pada halaman web, lalu frontend mengirimkannya sebagai Base64 ke API Flask. API menjalankan model TensorFlow dan mengembalikan kelas kondisi kulit serta rekomendasi singkat.

> Hasil klasifikasi adalah perkiraan dari model dan bukan diagnosis medis atau pengganti konsultasi dengan tenaga kesehatan.

## Kategori yang dikenali

- `berminyak`
- `jerawat`
- `kulit kering`
- `kulit sehat`

Dataset disusun dalam folder `data-set/latihan` dan `data-set/test`, masing-masing dengan subfolder untuk keempat kategori. Setiap kategori saat ini berisi 3–7 gambar pada masing-masing bagian.

## Struktur proyek

```text
.
├── app.py                           # API Flask untuk inferensi
├── skincare.py                      # Skrip pelatihan/evaluasi model
├── skincare.html                    # Antarmuka unggah gambar
├── script.js                        # Mengirim gambar ke API dan menampilkan hasil
├── style.css                        # Gaya halaman
├── requirements.txt                 # Dependensi Python
├── dockerfile                       # Konfigurasi container
├── skin_analysis_model.keras        # Model Keras
├── skin_analysis_model_mobilenet.keras
└── data-set/
    ├── latihan/<kategori>/          # Data pelatihan
    └── test/<kategori>/              # Data evaluasi
```

`percobaan.py` adalah skrip utilitas lama untuk memindahkan folder dataset dengan path khusus Windows; skrip ini tidak diperlukan untuk menjalankan aplikasi.

## Menjalankan aplikasi lokal

### 1. Siapkan Python dan dependensi

Gunakan lingkungan virtual agar dependensi proyek terisolasi.

```bash
python -m venv .venv
```

Aktifkan lingkungan virtual:

```powershell
# Windows PowerShell
.venv\Scripts\Activate.ps1
```

```bash
# macOS/Linux
source .venv/bin/activate
```

Instal dependensi:

```bash
pip install -r requirements.txt
```

### 2. Atur lokasi model

Backend `app.py` saat ini mencari model di `C:/Users/Andini/Documents/skin_analysis_model.keras`. Ubah nilai `MODEL_PATH` di `app.py` agar mengarah ke file model yang tersedia di proyek, misalnya `skin_analysis_model.keras`.

### 3. Jalankan backend

```bash
python app.py
```

API berjalan pada `http://127.0.0.1:5004`.

### 4. Buka frontend

Buka `skincare.html` di browser, pilih gambar, kemudian tekan **Capture Image**. Frontend mengirim permintaan ke `http://127.0.0.1:5004/analyze/`.

## API

### `POST /analyze/`

Kirim JSON dengan properti `image` berisi gambar Base64. Data URL seperti `data:image/jpeg;base64,...` juga diterima.

Contoh bentuk permintaan:

```json
{
  "image": "data:image/jpeg;base64,..."
}
```

Respons berhasil berisi:

```json
{
  "condition": "kulit sehat",
  "confidence": 92.4,
  "recommendation": "Kulit anda sehat, tetap jaga kebersihannya.",
  "average_rgb": {
    "red": 150.2,
    "green": 120.1,
    "blue": 110.7
  }
}
```

Jika gambar tidak disertakan atau tidak dapat dibaca, API mengembalikan JSON berisi `error`.

## Pelatihan model

`skincare.py` memuat dataset dari `data-set/latihan` dan `data-set/test`, mengubah ukuran gambar ke 224×224, melakukan augmentasi pada data latihan, lalu melatih MobileNetV2 dengan bobot ImageNet. Model disimpan sebagai `skin_analysis_model.keras` sesuai konfigurasi path di skrip.

Skrip pelatihan juga memakai `opencv-python` (`cv2`), `scikit-learn`, dan `matplotlib`, yang belum semuanya dicantumkan pada `requirements.txt`. Tambahkan dependensi tersebut sebelum menjalankan pelatihan. Perhatikan pula bahwa path simpan model di skrip masih mengarah ke lokasi khusus `C:/Users/Andini/Documents` dan sebaiknya disesuaikan.

## Catatan konfigurasi

- `requirements.txt` memasang Flask, tetapi `dockerfile` menjalankan `uvicorn app:app`; modul `app.py` menyediakan aplikasi Flask, bukan aplikasi ASGI yang langsung dapat dijalankan oleh Uvicorn. Untuk container, sesuaikan perintah startup agar menjalankan Flask/Gunicorn, atau ubah backend menjadi aplikasi ASGI.
- Dockerfile menyalin `requirements.txt` dan `app.py`, tetapi tidak menyalin file model. Agar inferensi di container berhasil, tambahkan model ke image atau pasangkan model ke container, lalu pastikan `MODEL_PATH` menunjuk ke lokasinya.
- Halaman memakai URL API lokal `127.0.0.1:5004`. Ubah URL tersebut jika frontend dan backend dijalankan pada host atau port yang berbeda.
- `app.py` mengasumsikan urutan keluaran model sama dengan `class_labels`. Pastikan urutan kelas saat model dilatih memang `berminyak`, `jerawat`, `kulit kering`, `kulit sehat`.
- Ukuran dataset yang tersedia sangat kecil, sehingga hasil klasifikasi dapat kurang akurat pada gambar baru.
