import os
import time
import threading
import serial
import cv2
import numpy as np
import io
import json
import piexif # Para manipular os metadados EXIF
from flask import Flask, render_template, request, jsonify, Response
from flask_cors import CORS
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image
from PIL import Image, ImageOps

app = Flask(__name__)
CORS(app)

# ==========================================
# 1. CONFIGURAÇÕES DE HARDWARE E PASTAS
# ==========================================

PORTA_SERIAL = '/dev/ttyUSB0'
BAUD_RATE = 9600
# Nova pasta de destino conforme solicitado
PASTA_ASSETS = os.path.join("assets", "pictures")

if not os.path.exists(PASTA_ASSETS):
    os.makedirs(PASTA_ASSETS)

try:
    ser = serial.Serial(PORTA_SERIAL, BAUD_RATE, timeout=1)
    print(f"🔌 Conectado ao Arduino na porta {PORTA_SERIAL}")
except:
    ser = None
    print(f"⚠️ Arduino não detectado na porta {PORTA_SERIAL}.")

clima_atual = {
    "umidade": "0",
    "temperatura": "0",
    "luminosidade": "0",
    "umidificador": "OFF",
    "ultimo_update": "--:--"
}

camera_lock = threading.Lock()
frame_atual = None

# ==========================================
# 2. FUNÇÃO DE INJEÇÃO DE METADADOS
# ==========================================

def salvar_foto_com_metadados(frame, caminho):
    """Salva o frame em JPG e injeta os dados do sensor no EXIF."""
    # 1. Converte o frame do OpenCV para um formato que o PIL entenda
    img_pil = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
    
    # 2. Prepara os dados do sensor como uma string JSON para o UserComment
    # Isso facilita a leitura automatizada depois
    dados_sensor = {
        "temp": clima_atual["temperatura"],
        "humi": clima_atual["umidade"],
        "lux": clima_atual["luminosidade"],
        "timestamp": time.strftime("%Y:%m:%d %H:%M:%S")
    }
    comment_str = json.dumps(dados_sensor)

    # 3. Cria o dicionário EXIF
    # DateTimeOriginal é o padrão para data/hora
    # UserComment (tag 37510) é perfeito para dados customizados
    exif_dict = {
        "0th": {
            piexif.ImageIFD.DateTime: time.strftime("%Y:%m:%d %H:%M:%S"),
            piexif.ImageIFD.Software: u"Kampu System v2"
        },
        "Exif": {
            piexif.ExifIFD.DateTimeOriginal: time.strftime("%Y:%m:%d %H:%M:%S"),
            piexif.ExifIFD.UserComment: comment_str.encode('utf-8')
        }
    }
    
    exif_bytes = piexif.dump(exif_dict)
    
    # 4. Salva o arquivo final com o EXIF injetado
    img_pil.save(caminho, "jpeg", exif=exif_bytes)
    print(f"✅ Foto salva com metadados em: {caminho}")

# ==========================================
# 3. THREADS (ARDUINO, CÂMERA E FOTOS)
# ==========================================

def escutar_arduino():
    global clima_atual
    while True:
        if ser and ser.in_waiting > 0:
            try:
                linha = ser.readline().decode('utf-8').strip()
                if "|" in linha:
                    partes = linha.split("|")
                    clima_atual["umidade"] = partes[0].split(":")[1]
                    clima_atual["temperatura"] = partes[1].split(":")[1]
                    clima_atual["luminosidade"] = partes[2].split(":")[1]
                    clima_atual["umidificador"] = partes[3].split(":")[1]
                    clima_atual["ultimo_update"] = time.strftime("%H:%M:%S")
            except:
                pass
        time.sleep(1)

def capturar_camera_continua():
    global frame_atual
    cam = cv2.VideoCapture(1)
    while True:
        ret, frame = cam.read()
        if ret:
            with camera_lock:
                frame_atual = frame.copy()
        time.sleep(0.1)

def rotina_fotos():
    time.sleep(5) # Delay inicial para estabilização
    while True:
        with camera_lock:
            if frame_atual is not None:
                nome_arquivo = f"kampu_{int(time.time())}.jpg"
                caminho_completo = os.path.join(PASTA_ASSETS, nome_arquivo)
                
                # Chama a nova função de salvamento inteligente
                salvar_foto_com_metadados(frame_atual, caminho_completo)
            else:
                print("⚠️ Câmera ainda não gerou frames.")
        
        time.sleep(600) # 10 minutos

threading.Thread(target=escutar_arduino, daemon=True).start()
threading.Thread(target=capturar_camera_continua, daemon=True).start()
threading.Thread(target=rotina_fotos, daemon=True).start()

# --- STREAM E IA (Mantidos como estavam) ---

def gerar_stream_web():
    global frame_atual
    while True:
        with camera_lock:
            if frame_atual is not None:
                ret, buffer = cv2.imencode('.jpg', frame_atual)
                if ret:
                    yield (b'--frame\r\n'
                           b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')
        time.sleep(0.1)

# [Abaixo continuam as rotas /, /ia, /api/clima, /video_feed e /analisar_planta]

@app.route('/')
def dashboard(): return render_template('dashboard.html')

@app.route('/api/clima')
def get_clima(): return jsonify(clima_atual)

@app.route('/video_feed')
def video_feed(): return Response(gerar_stream_web(), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    print("🚀 Orion: Kampu subindo com registro de metadados EXIF ativo.")
    app.run(host='0.0.0.0', port=5000, debug=True, use_reloader=False)