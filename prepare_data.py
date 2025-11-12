"""
Script para dividir o dataset PlantVillage do Kaggle em treino e validação.
Cria as pastas:
  data/train/
  data/val/
com 80% / 20% das imagens de cada classe.
"""

import os
import shutil
import glob
from sklearn.model_selection import train_test_split

SRC_DIR = "data/PlantVillage"  # pasta original do Kaggle
TRAIN_DIR = "data/train"
VAL_DIR = "data/val"
SPLIT_RATIO = 0.2

def prepare_dataset():
    if not os.path.exists(SRC_DIR):
        raise FileNotFoundError(
            f"❌ Pasta '{SRC_DIR}' não encontrada.\n"
            "Baixe e extraia o dataset Kaggle em data/PlantVillage primeiro."
        )

    os.makedirs(TRAIN_DIR, exist_ok=True)
    os.makedirs(VAL_DIR, exist_ok=True)

    classes = [d for d in os.listdir(SRC_DIR) if os.path.isdir(os.path.join(SRC_DIR, d))]
    print(f"🌿 {len(classes)} classes encontradas.")

    for cls in classes:
        src_path = os.path.join(SRC_DIR, cls)
        train_path = os.path.join(TRAIN_DIR, cls)
        val_path = os.path.join(VAL_DIR, cls)
        os.makedirs(train_path, exist_ok=True)
        os.makedirs(val_path, exist_ok=True)

        imgs = glob.glob(os.path.join(src_path, "*.jpg"))
        if len(imgs) == 0:
            print(f"⚠️ Nenhuma imagem encontrada em {cls}, pulando.")
            continue

        train_imgs, val_imgs = train_test_split(imgs, test_size=SPLIT_RATIO, random_state=42)

        for img in train_imgs:
            shutil.copy(img, train_path)
        for img in val_imgs:
            shutil.copy(img, val_path)

        print(f"📁 {cls}: {len(train_imgs)} treino | {len(val_imgs)} val")

    print("\n✅ Divisão concluída com sucesso!")
    print(f"Treino: {TRAIN_DIR}")
    print(f"Validação: {VAL_DIR}")

if __name__ == "__main__":
    prepare_dataset()
