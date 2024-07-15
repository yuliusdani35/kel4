from flask import Flask, request, render_template
import requests
import logging
from tensorflow.keras.models import load_model # type: ignore
from tensorflow.keras.layers import Dense # type: ignore
import os
import traceback
import tensorflow as tf
app = Flask(__name__)

# Set API key
WEATHERBIT_KEY = "0ba5e1009a124f4eb48828f9969bf40c"

MODEL_PATH = "Model/lstm_6_3_e50/my_model.h5"

# Menonaktifkan pesan oneDNN untuk menonaktifkan opsional oneDNN
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'

try:
    # Muat model LSTM dengan custom object scope
    with tf.keras.utils.custom_object_scope({'Dense': Dense}):
        lstm_model = load_model(MODEL_PATH, compile=False)
    lstm_model.compile(optimizer='adam', loss='mse', metrics=['mse'])
    logging.info("Model LSTM berhasil dimuat dan dikompilasi")
except Exception as e:
    logging.error(f"Error saat memuat model LSTM: {e}")
    traceback.print_exc()
    raise SystemExit("Aplikasi tidak dapat dijalankan karena model tidak dapat dimuat")

# Daftar koordinat kota
CITY_COORDINATES = {
    "jakarta": (-6.2088, 106.8456),
    "surabaya": (-7.2575, 112.7521),
    "semarang": (-6.9932, 110.4203),
    "serang": (-6.1104, 106.1639),
    "bengkulu": (-3.8006, 102.2561),
    "jambi": (-1.6108, 103.6131),
    "tanjungpinang": (0.9227, 104.4500),
    "pangkalpinang": (-2.1291, 106.1133),
    "banda aceh": (5.5466, 95.3191),
    "bandung": (-6.9175, 107.6191)
}



@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        if 'city' in request.form:
            city = request.form["city"].lower()
            return get_air_quality(city=city)
    # Jika metode GET atau saat pertama kali mengakses, render halaman utama
    return render_template('index.html')

@app.route("/air_quality", methods=["GET", "POST"])
def air_quality():
    if request.method == "POST":
        if 'city' in request.form:
            city = request.form["city"].lower()
            return get_air_quality(city=city)
    
    # Jika tidak ada input dari form POST, render halaman dengan prediksi untuk Surabaya
    return get_air_quality(city="surabaya")

def get_air_quality(city=None):
    try:
        if city:
            coordinates = CITY_COORDINATES.get(city)
            if coordinates:
                latitude, longitude = coordinates
            else:
                raise ValueError(f"Tidak dapat menemukan koordinat untuk kota: {city}")

            # Endpoint untuk mendapatkan kualitas udara saat ini
            url = f"https://api.weatherbit.io/v2.0/current/airquality?lat={latitude}&lon={longitude}&key={WEATHERBIT_KEY}"
            
            # Mengirimkan permintaan HTTP GET
            response = requests.get(url)
            
            # Memeriksa apakah permintaan berhasil (status code 200 adalah sukses)
            if response.status_code == 200:
                data = response.json()
                air_quality = data['data'][0]  # Asumsi API mengembalikan daftar dengan satu elemen
                city_name = city if city else "unknown location"
                # Render template dengan data air_quality
                return render_template('air_quality.html', air_quality=air_quality, city=city_name)
            else:
                logging.error(f"Gagal mendapatkan data kualitas udara: {response.status_code}")
                return render_template('air_quality.html', error="Gagal mendapatkan data kualitas udara")
        else:
            raise ValueError("Nama kota tidak boleh kosong")
    except Exception as e:
        logging.error(f"Error di endpoint get_air_quality: {e}")
        return render_template('air_quality.html', error=str(e))

@app.context_processor
def utility_processor():
    def get_quality_class(aqi):
        if aqi <= 50:
            return 'baik'
        elif aqi <= 100:
            return 'sedang'
        elif aqi <= 150:
            return 'tidak-sehat'
        else:
            return 'sangat-tidak-sehat'

    def get_quality_text(aqi):
        if aqi <= 50:
            return 'Baik'
        elif aqi <= 100:
            return 'Sedang'
        elif aqi <= 150:
            return 'Tidak Sehat'
        else:
            return 'Sangat Tidak Sehat'

    return dict(get_quality_class=get_quality_class, get_quality_text=get_quality_text)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
