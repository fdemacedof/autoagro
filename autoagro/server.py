from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
import os
import base64
import json
import requests
from getpass import getpass
from utils.secure_key_utils import decrypt_api_key # importa função criada antes

app = FastAPI(title="PlantID Backend")
MIN_PROB = 0.7
ENC_KEY_PATH = "plantid_key.enc"

# ======================================================
# 🔑 Função auxiliar para carregar e descriptografar a API key
# ======================================================
def load_api_key_interactive() -> str:
    """Verifica se a chave criptografada existe e solicita a senha."""
    if not os.path.exists(ENC_KEY_PATH):
        msg = (
            f"❌ Arquivo '{ENC_KEY_PATH}' não encontrado.\n"
            "Crie sua chave criptografada executando:\n"
            "    python secure_key_utils.py encrypt\n"
        )
        raise FileNotFoundError(msg)

    # tenta pegar senha de variável de ambiente ou input seguro
    passphrase = os.getenv("PLANT_ID_PASSPHRASE")
    if not passphrase:
        print("🔐 Digite a senha (passphrase) usada para criptografar sua chave:")
        passphrase = getpass("Passphrase: ")

    try:
        api_key = decrypt_api_key(ENC_KEY_PATH, passphrase)
        print("✅ Chave descriptografada com sucesso.")
        return api_key
    except Exception as e:
        raise ValueError(f"Falha ao descriptografar a chave: {e}")


# ======================================================
# 🌿 Endpoint principal
# ======================================================
@app.post("/analyze")
async def analyze_image(file: UploadFile = File(...)):
    """
    Recebe uma imagem (upload) e retorna espécies e doenças detectadas.
    """
    try:
        api_key = load_api_key_interactive()
    except FileNotFoundError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))

    # lê bytes da imagem enviada
    img_bytes = await file.read()
    img_b64 = base64.b64encode(img_bytes).decode("utf-8")

    payload = {
        "api_key": api_key,
        "images": [img_b64],
        "classification_level": "all",
        "health": "all",
    }

    res = requests.post("https://api.plant.id/v3/identification", json=payload)
    if res.status_code not in (200, 201):
        raise HTTPException(status_code=res.status_code, detail=res.text)

    result = res.json()

    # filtra resultados por probabilidade mínima
    species = [
        {"name": s["name"], "probability": round(s["probability"], 4)}
        for s in result.get("result", {}).get("classification", {}).get("suggestions", [])
        if s["probability"] >= MIN_PROB
    ]

    diseases = [
        {"name": d["name"], "probability": round(d["probability"], 4)}
        for d in result.get("result", {}).get("disease", {}).get("suggestions", [])
        if d["probability"] >= MIN_PROB
    ]

    return JSONResponse(content={"species": species, "disease": diseases})


# ======================================================
# ▶️ Execução direta (modo standalone)
# ======================================================
if __name__ == "__main__":
    import uvicorn

    print("🚀 Iniciando servidor PlantID Backend...")
    if not os.path.exists(ENC_KEY_PATH):
        print(
            f"\n⚠️ Nenhum arquivo '{ENC_KEY_PATH}' encontrado.\n"
            "Antes de rodar o servidor, crie sua chave com:\n"
            "    python secure_key_utils.py encrypt\n"
        )
    else:
        print("🔎 Arquivo de chave encontrado. O servidor solicitará a senha no primeiro uso.\n")

    uvicorn.run(app, host="0.0.0.0", port=8000)