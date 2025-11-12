import requests
import json
import os

# === Configurações ===
SERVER_URL = "http://127.0.0.1:8000/analyze"
IMAGE_PATH = "autoagro/tests/data/acer-deshojo.jpg"  # altere se necessário

def test_plantxvit_server():
    """Envia uma imagem para o servidor e exibe o resultado formatado."""
    if not os.path.exists(IMAGE_PATH):
        print(f"❌ Arquivo não encontrado: {IMAGE_PATH}")
        return

    with open(IMAGE_PATH, "rb") as img:
        files = {"file": (os.path.basename(IMAGE_PATH), img, "image/jpeg")}
        print(f"📤 Enviando {os.path.basename(IMAGE_PATH)} para {SERVER_URL}...")
        res = requests.post(SERVER_URL, files=files)

    if res.status_code != 200:
        print(f"❌ Erro {res.status_code}: {res.text}")
        return

    try:
        data = res.json()
    except json.JSONDecodeError:
        print("❌ Resposta inválida do servidor.")
        return

    print("\n✅ Resultado:")
    print(json.dumps(data, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    test_plantxvit_server()
