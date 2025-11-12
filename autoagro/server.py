from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
import torch
from torchvision import transforms
from PIL import Image
import io

# se o PlantXViT estiver no mesmo repositório:
# from plantxvit import PlantXViT
# caso contrário, substitua pela importação do modelo que você escolher
from torchvision.models import efficientnet_b0

app = FastAPI(title="PlantXViT Local Backend")

# ======================================
# 🔧 Configuração do modelo
# ======================================
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

# exemplo: usando EfficientNet pré-treinado (pode trocar pelo PlantXViT)
model = efficientnet_b0(weights="IMAGENET1K_V1")
num_classes = 38  # ajuste conforme dataset
model.classifier[1] = torch.nn.Linear(model.classifier[1].in_features, num_classes)

# carregue pesos se tiver (fine-tuned)
# model.load_state_dict(torch.load("plantxvit_finetuned.pth", map_location=DEVICE))

model.to(DEVICE)
model.eval()

# classes do PlantVillage (exemplo simplificado)
CLASSES = [
    "Apple___Black_rot", "Apple___healthy", "Pepper__bell___Bacterial_spot",
    "Pepper__bell___healthy", "Tomato___Late_blight", "Tomato___healthy"
]

# transformações de pré-processamento
transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
])


# ======================================
# 🌿 Endpoint principal
# ======================================
@app.post("/analyze")
async def analyze_image(file: UploadFile = File(...)):
    """Recebe uma imagem e retorna espécie/doença usando modelo local."""
    try:
        contents = await file.read()
        img = Image.open(io.BytesIO(contents)).convert("RGB")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Erro ao ler imagem: {e}")

    # preparar imagem
    x = transform(img).unsqueeze(0).to(DEVICE)

    # inferência
    with torch.no_grad():
        logits = model(x)
        probs = torch.softmax(logits, dim=1)
        top_prob, top_idx = torch.topk(probs, 3)

    # montar resposta JSON
    predictions = [
        {"label": CLASSES[i] if i < len(CLASSES) else f"class_{i}",
         "probability": float(top_prob[0][j])}
        for j, i in enumerate(top_idx[0])
    ]

    return JSONResponse(content={"predictions": predictions})


# ======================================
# ▶️ Execução direta
# ======================================
if __name__ == "__main__":
    import uvicorn
    print("🚀 Iniciando servidor local PlantXViT...")
    uvicorn.run(app, host="0.0.0.0", port=8000)