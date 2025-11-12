import os
import torch
from plantxvit import PlantXViT

DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
MODEL_PATH = os.path.join(os.path.dirname(__file__), "plantxvit_best.pth")

def load_local_model(model_path: str = MODEL_PATH):
    """Carrega o modelo PlantXViT salvo localmente."""
    print("🌿 Carregando modelo PlantXViT local...")

    model = PlantXViT(pretrained=False)

    if not os.path.exists(model_path):
        raise FileNotFoundError(
            f"❌ Arquivo de modelo não encontrado em '{model_path}'. "
            "Treine ou baixe o modelo antes de iniciar o servidor."
        )

    state_dict = torch.load(model_path, map_location=DEVICE)
    model.load_state_dict(state_dict)
    model.to(DEVICE)
    model.eval()

    print(f"✅ Modelo carregado ({'GPU' if DEVICE == 'cuda' else 'CPU'}) e pronto para inferência.")
    return model
