import os
from fastapi.testclient import TestClient
from autoagro.server import app

def test_endpoint_analyze():
    """
    Testa o endpoint /analyze enviando uma imagem real.
    """
    client = TestClient(app)

    base_dir = os.path.dirname(__file__)
    img_path = os.path.join(base_dir, "dados", "acer-deshojo.jpg")

    if not os.path.exists(img_path):
        raise FileNotFoundError("Imagem de teste não encontrada em tests/dados/")

    with open(img_path, "rb") as f:
        files = {"file": ("acer-deshojo.jpg", f, "image/jpeg")}
        response = client.post("/analyze", files=files)

    assert response.status_code == 200, f"Erro na requisição: {response.text}"

    data = response.json()
    assert "species" in data
    assert "disease" in data

    print("✅ Endpoint respondeu corretamente!")
    print(data)