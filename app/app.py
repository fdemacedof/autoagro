import os
import time
import threading
import serial
import cv2
import numpy as np
import io
import json
import piexif
from flask import Flask, render_template, request, jsonify, Response
from flask_cors import CORS
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image
from PIL import Image, ImageOps

app = Flask(__name__)
CORS(app)

# ==========================================
# 1. CONFIGURAÇÕES GERAIS (HARDWARE E IA)
# ==========================================

# --- Hardware ---
PORTA_SERIAL = '/dev/ttyUSB0'
BAUD_RATE = 9600
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
    "umidade": "0", "temperatura": "0", "luminosidade": "0",
    "umidificador": "OFF", "ultimo_update": "--:--"
}
camera_lock = threading.Lock()
frame_atual = None

# --- Inteligência Artificial ---
TARGET_SIZE = (224, 224)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODELS_DIR = os.path.join(BASE_DIR, 'models')

CLASSES_ROUTER = ['Pepper', 'Potato', 'Tomato']
CLASSES_SAUDE_PIMENTA = ['Bacterial Spot', 'Cercospora Leaf Spot', 'Curl Virus', 'Healthy Leaf', 'Nutrition Deficiency', 'White spot']
CLASSES_CRESCIMENTO_PIMENTA = ['Dry chili', 'Flower', 'Green Chili', 'Red Chili', 'Rotten Chili']

print("\n🌱 Kampu: Carregando sistemas neurais...")
modelos = {}

def carregar_modelo_seguro(caminho_relativo):
    full_path = os.path.join(MODELS_DIR, caminho_relativo)
    if os.path.exists(full_path):
        print(f"   -> Carregando: {caminho_relativo}...")
        return load_model(full_path)
    else:
        print(f"   ❌ CRÍTICO: Modelo não encontrado em {full_path}")
        return None

modelos['router'] = carregar_modelo_seguro('router_species.keras')
modelos['pimenta_saude'] = carregar_modelo_seguro(os.path.join('pepper', 'health.keras'))
modelos['pimenta_crescimento'] = carregar_modelo_seguro(os.path.join('pepper', 'growth.keras'))
print("✅ Sistemas online!\n")

# ==========================================
# 2. FUNÇÕES DE SUPORTE (FOTOS EXIF E IA)
# ==========================================

def salvar_foto_com_metadados(frame, caminho):
    img_pil = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
    dados_sensor = {
        "temp": clima_atual["temperatura"],
        "humi": clima_atual["umidade"],
        "lux": clima_atual["luminosidade"],
        "timestamp": time.strftime("%Y:%m:%d %H:%M:%S")
    }
    comment_str = json.dumps(dados_sensor)
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
    img_pil.save(caminho, "jpeg", exif=exif_bytes)
    print(f"✅ Foto salva com metadados em: {caminho}")

def preparar_imagem(img_bytes):
    img = Image.open(io.BytesIO(img_bytes))
    if img.mode != "RGB": img = img.convert("RGB")
    img = ImageOps.fit(img, TARGET_SIZE, Image.Resampling.LANCZOS)
    img_array = image.img_to_array(img)
    return np.expand_dims(img_array, axis=0)

def consultar_modelo(modelo, img_array, lista_classes):
    if modelo is None: return "Modelo Off-line", 0.0
    predicao = modelo.predict(img_array, verbose=0)
    indice = np.argmax(predicao[0])
    confianca = float(np.max(predicao[0])) * 100
    classe = lista_classes[indice] if indice < len(lista_classes) else "Classe Desconhecida"
    return classe, confianca

# ==========================================
# 3. THREADS DE HARDWARE
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
            except: pass
        time.sleep(1)

def capturar_camera_continua():
    global frame_atual
    cam = cv2.VideoCapture(2)
    
    # Tenta setar a resolução máxima (Ex: 4K ou Full HD)
    cam.set(cv2.CAP_PROP_FRAME_WIDTH, 3840) 
    cam.set(cv2.CAP_PROP_FRAME_HEIGHT, 2160)
    # Ignora frames acumulados no buffer para pegar sempre o "agora"
    cam.set(cv2.CAP_PROP_BUFFERSIZE, 1)

    while True:
        ret, frame = cam.read()
        if ret:
            # Rotação se necessário (Ex: 90 graus)
            # frame = cv2.rotate(frame, cv2.ROTATE_90_CLOCKWISE)
            
            with camera_lock:
                frame_atual = frame.copy()
        time.sleep(0.01)

def rotina_fotos():
    time.sleep(5) 
    while True:
        with camera_lock:
            if frame_atual is not None:
                nome_arquivo = f"kampu_{int(time.time())}.jpg"
                salvar_foto_com_metadados(frame_atual, os.path.join(PASTA_ASSETS, nome_arquivo))
        time.sleep(600) 

def gerar_stream_web():
    global frame_atual
    while True:
        with camera_lock:
            if frame_atual is not None:
                ret, buffer = cv2.imencode('.jpg', frame_atual)
                if ret:
                    yield (b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')
        time.sleep(0.1)

threading.Thread(target=escutar_arduino, daemon=True).start()
threading.Thread(target=capturar_camera_continua, daemon=True).start()
threading.Thread(target=rotina_fotos, daemon=True).start()

# ==========================================
# 4. ROTAS (FRONTEND E API)
# ==========================================

# Nova Landing Page
@app.route('/')
def landing(): 
    return render_template('landing.html')

# Painel de Hardware Atual
@app.route('/dashboard')
def dashboard(): 
    return render_template('dashboard.html')

# App Legacy de IA
@app.route('/ml_vision')
def ia_legacy(): 
    return render_template('ml_vision.html') # Renomeie o index.html legado para ia.html

# APIs do Hardware
@app.route('/api/clima')
def get_clima(): 
    return jsonify(clima_atual)

@app.route('/video_feed')
def video_feed(): 
    return Response(gerar_stream_web(), mimetype='multipart/x-mixed-replace; boundary=frame')

# API da Inteligência Artificial
@app.route('/analisar_planta', methods=['POST'])
def analisar():
    inicio = time.time()
    if 'image' not in request.files:
        return jsonify({'erro': 'Nenhuma imagem enviada'}), 400
    
    img_array = preparar_imagem(request.files['image'].read())
    response = {"timestamp": time.strftime("%d/%m/%Y - %H:%M")}

    especie_raw, conf_esp = consultar_modelo(modelos.get('router'), img_array, CLASSES_ROUTER)
    
    nomes_exibicao = {'Adenium': 'Rosa do Deserto (Adenium)', 'Pepper': 'Pimenta (Capsicum)', 'Potato': 'Batata', 'Tomato': 'Tomate'}
    especie_exibicao = nomes_exibicao.get(especie_raw, especie_raw)
    
    response['especie'] = especie_exibicao
    response['confianca'] = f"{conf_esp:.1f}%"

    if especie_raw == 'Pepper':
        saude, conf_saude = consultar_modelo(modelos.get('pimenta_saude'), img_array, CLASSES_SAUDE_PIMENTA)
        estagio, conf_estagio = consultar_modelo(modelos.get('pimenta_crescimento'), img_array, CLASSES_CRESCIMENTO_PIMENTA)
        
        response['saude'] = saude
        response['estagio'] = estagio
        
        if saude != 'Healthy Leaf':
            response['alerta'], response['classe_alerta'] = f"⚠️ Saria detectou: {saude}.", "alert-danger"
        elif estagio == 'Rotten Chili':
            response['alerta'], response['classe_alerta'] = "⚠️ Saria detectou: Fruto Podre.", "alert-danger"
        else:
            response['alerta'], response['classe_alerta'] = "✅ Planta vigorosa.", "alert-success"
    else:
        response['saude'] = "Modelo Especialista não carregado"
        response['estagio'] = "Monitoramento Básico"
        response['alerta'] = f"ℹ️ Identificado {especie_exibicao}."
        response['classe_alerta'] = "alert-secondary"

    print(f"📸 Processado: {especie_exibicao} | Tempo: {time.time() - inicio:.2f}s")
    return jsonify(response)

if __name__ == '__main__':
    print("🚀 Kampu System Full Stack (Hardware + IA) iniciado!")
    app.run(host='0.0.0.0', port=5000, debug=True, use_reloader=False)