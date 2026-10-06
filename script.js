const imageInput = document.getElementById('imageInput');
const captureBtn = document.getElementById('captureBtn');
const resultDiv = document.getElementById('result');

// Fungsi untuk mengonversi gambar ke base64
function toBase64(file) {
    return new Promise((resolve, reject) => {
        const reader = new FileReader();
        reader.onloadend = () => resolve(reader.result);
        reader.onerror = reject;
        reader.readAsDataURL(file);
    });
}

// Event listener untuk tombol Capture
captureBtn.addEventListener('click', async () => {  
    if (imageInput.files.length === 0) {
        resultDiv.innerHTML = `<p style="color: red;">Please select an image first.</p>`;
        return;
    }

    const file = imageInput.files[0];
    const imageBase64 = await toBase64(file);

    try {
        // Kirimkan gambar ke backend
        const response = await fetch('http://127.0.0.1:5004/analyze/', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ image: imageBase64 })
        });

        const data = await response.json();

        if (data.error) {
            resultDiv.innerHTML = `<p style="color: red;">Error: ${data.error}</p>`;
        } else {
            resultDiv.innerHTML = `
            <h3>Hasil Analisis</h3>
            <p><strong>Kondisi:</strong> <span id="condition">${data.condition}</span></p>
            <p><strong>Kepercayaan:</strong> <span id="confidence">${data.confidence}</span>%</p>
            <p><strong>Rekomendasi:</strong> <span id="recommendation">${data.recommendation}</span></p>
        `;
        
        }
    } catch (error) {
        resultDiv.innerHTML = `<p style="color: red;">Error: ${error.message}</p>`;
    }
});
