import sys
import os
import io
import time
import torch
import logging
from PIL import Image
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
from torchvision import transforms

# ======================================================
# 🧭 Ajusta o caminho para o repositório PlantXViT
# ======================================================
PLANTXVIT_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "../PlantXViT/src"))
if PLANTXVIT_PATH not in sys.path:
    sys.path.append(PLANTXVIT_PATH)

try:
    from model import PlantXViT
except ModuleNotFoundError as e:
    raise ImportError(
        f"❌ Não foi possível importar PlantXViT de {PLANTXVIT_PATH}.\n"
        "Verifique se o repositório foi clonado corretamente:\n"
        "   git clone https://github.com/sakanaowo/PlantXViT.git\n"
        "E que o arquivo 'PlantXViT/src/model.py' existe."
    ) from e

# ======================================================
# ⚙️ Configuração geral
# ======================================================
app = FastAPI(title="AutoAgro - PlantXViT Backend (Offline)")
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
MODEL_PATH = "models/plantxvit_best.pth"
MIN_PROB = 0.7

# logging bonito
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    datefmt="%H:%M:%S"
)
logger = logging.getLogger(__name__)

# ======================================================
# 🧠 Função para baixar e carregar o modelo
# ======================================================
def download_model_if_needed():
    """Baixa automaticamente o modelo pré-treinado do Hugging Face se não existir."""
    os.makedirs("models", exist_ok=True)
    if os.path.exists(MODEL_PATH):
        logger.info("📦 Modelo local encontrado, sem necessidade de download.")
        return

    url = "https://huggingface.co/VishnuSivadasVS/plant-disease-classification/resolve/main/model.pth"
    logger.info(f"⬇️ Baixando modelo pré-treinado de {url} ...")
    import urllib.request
    try:
        urllib.request.urlretrieve(url, MODEL_PATH)
        logger.info(f"✅ Download concluído e salvo em '{MODEL_PATH}'.")
    except Exception as e:
        raise RuntimeError(f"Falha ao baixar o modelo: {e}")

def load_model():
    """Carrega o modelo PlantXViT local."""
    logger.info("🌿 Inicializando modelo PlantXViT...")
    model = PlantXViT(pretrained=False)

    download_model_if_needed()

    try:
        state_dict = torch.load(MODEL_PATH, map_location=DEVICE)
        model.load_state_dict(state_dict)
    except Exception as e:
        raise RuntimeError(f"Erro ao carregar pesos do modelo: {e}")

    model.to(DEVICE)
    model.eval()
    logger.info(f"✅ Modelo carregado e pronto ({'GPU' if DEVICE == 'cuda' else 'CPU'}).")
    return model

try:
    model = load_model()
except Exception as e:
    logger.error(str(e))
    model = None

# ======================================================
# 🧩 Classes PlantVillage (38 classes)
# ======================================================
CLASSES = [
    'Apple___Apple_scab', 'Apple___Black_rot', 'Apple___Cedar_apple_rust', 'Apple___healthy',
    'Blueberry___healthy', 'Cherry_(including_sour)___Powdery_mildew', 'Cherry_(including_sour)___healthy',
    'Corn_(maize)___Cercospora_leaf_spot Gray_leaf_spot', 'Corn_(maize)___Common_rust_', 
    'Corn_(maize)___Northern_Leaf_Blight', 'Corn_(maize)___healthy', 'Grape___Black_rot', 
    'Grape___Esca_(Black_Measles)', 'Grape___Leaf_blight_(Isariopsis_Leaf_Spot)', 'Grape___healthy',
    'Orange___Haunglongbing_(Citrus_greening)', 'Peach___Bacterial_spot', 'Peach___healthy',
    'Pepper,_bell___Bacterial_spot', 'Pepper,_bell___healthy', 'Potato___Early_blight', 
    'Potato___Late_blight', 'Potato___healthy', 'Raspberry___healthy', 'Soybean___healthy',
    'Squash___Powdery_mildew', 'Strawberry___Leaf_scorch', 'Strawberry___healthy',
    'Tomato___Bacterial_spot', 'Tomato___Early_blight', 'Tomato___Late_blight',
    'Tomato___Leaf_Mold', 'Tomato___Septoria_leaf_spot', 'Tomato___Spider_mites Two-spotted_spider_mite',
    'Tomato___Target_Spot', 'Tomato___Tomato_Yellow_Leaf_Curl_Virus',
    'Tomato___Tomato_mosaic_virus', 'Tomato___healthy'
]

# ======================================================
# 🔄 Pré-processamento da imagem
# ======================================================
transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
])

# ======================================================
# 🌿 Endpoint principal
# ======================================================
@app.post("/analyze")
async def analyze_image(file: UploadFile = File(...)):
    """Recebe uma imagem e retorna as classes mais prováveis (espécie + doença)."""
    if model is None:
        raise HTTPException(status_code=500, detail="Modelo não carregado. Verifique logs.")

    start_time = time.time()

    try:
        contents = await file.read()
        img = Image.open(io.BytesIO(contents)).convert("RGB")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Erro ao abrir imagem: {e}")

    x = transform(img).unsqueeze(0).to(DEVICE)

    with torch.no_grad():
        logits = model(x)
        probs = torch.softmax(logits, dim=1)
        top_prob, top_idx = torch.topk(probs, 3)

    elapsed = round(time.time() - start_time, 3)

    results = []
    for j, idx in enumerate(top_idx[0]):
        label = CLASSES[idx] if idx < len(CLASSES) else f"class_{idx}"
        prob = float(top_prob[0][j])
        if prob >= MIN_PROB:
            results.append({"label": label, "probability": round(prob, 4)})

    if not results:
        raise HTTPException(status_code=422, detail="Nenhuma classe com probabilidade suficiente encontrada.")

    logger.info(f"🖼️ '{file.filename}' processada em {elapsed}s — Top: {results[0]['label']} ({results[0]['probability']:.2f})")

    return JSONResponse(content={
        "predictions": results,
        "device": DEVICE,
        "inference_time": elapsed,
        "image_name": file.filename
    })

# ======================================================
# ▶️ Execução direta
# ======================================================
if __name__ == "__main__":
    import uvicorn
    logger.info("🚀 Iniciando servidor local PlantXViT...")
    uvicorn.run(app, host="0.0.0.0", port=8000)

