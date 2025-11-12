"""
Treinamento escalável (CPU/GPU) com PlantVillage.
Usa MobileNetV3 pretreinada, barra de progresso e checkpoints automáticos.
"""

import os
import torch
from torch import nn, optim
from torchvision import models, transforms, datasets
from torch.utils.data import DataLoader
from datetime import datetime
from tqdm import tqdm

# ============================================================
# ⚙️ CONFIGURAÇÕES GERAIS
# ============================================================
DATA_DIR = "data"              # Pasta com /train e /val
EPOCHS = 10                    # Pode aumentar em GPU
BATCH_SIZE = 8                 # Ajuste conforme recurso
LR = 1e-3
CHECKPOINT_DIR = "checkpoints"
MODEL_PATH = os.path.join(CHECKPOINT_DIR, "plantvillage_best.pth")

# cria pasta de checkpoints
os.makedirs(CHECKPOINT_DIR, exist_ok=True)

# autodetecta GPU
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"🌿 Treinando em: {device}")

# ============================================================
# 📦 DATASET E TRANSFORMAÇÕES
# ============================================================
train_transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.RandomHorizontalFlip(),
    transforms.ToTensor(),
    transforms.Normalize([0.485, 0.456, 0.406],
                         [0.229, 0.224, 0.225])
])

val_transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize([0.485, 0.456, 0.406],
                         [0.229, 0.224, 0.225])
])

train_ds = datasets.ImageFolder(os.path.join(DATA_DIR, "train"), transform=train_transform)
val_ds = datasets.ImageFolder(os.path.join(DATA_DIR, "val"), transform=val_transform)

train_dl = DataLoader(train_ds, batch_size=BATCH_SIZE, shuffle=True)
val_dl = DataLoader(val_ds, batch_size=BATCH_SIZE)

print(f"📁 {len(train_ds)} imagens de treino | {len(val_ds)} de validação")
print(f"🔖 {len(train_ds.classes)} classes: {train_ds.classes}")

# ============================================================
# 🧠 MODELO PRETREINADO (TRANSFER LEARNING)
# ============================================================
from torchvision.models import mobilenet_v3_small, MobileNet_V3_Small_Weights
weights = MobileNet_V3_Small_Weights.IMAGENET1K_V1
model = mobilenet_v3_small(weights=weights)

# Congela a base convolucional
for param in model.features.parameters():
    param.requires_grad = False

# Substitui a camada final
num_ftrs = model.classifier[3].in_features
model.classifier[3] = nn.Linear(num_ftrs, len(train_ds.classes))
model = model.to(device)

criterion = nn.CrossEntropyLoss()
optimizer = optim.Adam(model.classifier.parameters(), lr=LR)

# ============================================================
# 🚀 LOOP DE TREINAMENTO
# ============================================================
best_acc = 0.0

for epoch in range(1, EPOCHS + 1):
    print(f"\n🌾 Epoch {epoch}/{EPOCHS}")
    model.train()
    train_loss = 0.0

    # --- Treino ---
    for imgs, labels in tqdm(train_dl, desc="Treinando", leave=False):
        imgs, labels = imgs.to(device), labels.to(device)
        optimizer.zero_grad()
        outputs = model(imgs)
        loss = criterion(outputs, labels)
        loss.backward()
        optimizer.step()
        train_loss += loss.item()

    avg_train_loss = train_loss / len(train_dl)

    # --- Validação ---
    model.eval()
    correct, total, val_loss = 0, 0, 0.0
    with torch.no_grad():
        for imgs, labels in tqdm(val_dl, desc="Validando", leave=False):
            imgs, labels = imgs.to(device), labels.to(device)
            outputs = model(imgs)
            loss = criterion(outputs, labels)
            val_loss += loss.item()
            _, preds = torch.max(outputs, 1)
            total += labels.size(0)
            correct += (preds == labels).sum().item()

    val_acc = correct / total
    avg_val_loss = val_loss / len(val_dl)

    print(f"📊 Loss treino: {avg_train_loss:.4f} | Loss val: {avg_val_loss:.4f} | Acc val: {val_acc:.4f}")

    # --- Salva melhor modelo ---
    if val_acc > best_acc:
        best_acc = val_acc
        torch.save(model.state_dict(), MODEL_PATH)
        print(f"💾 Novo melhor modelo salvo ({best_acc:.4f}) em {MODEL_PATH}")

print(f"\n✅ Treinamento concluído. Melhor acc: {best_acc:.4f}")
print(f"🕓 Finalizado em {datetime.now().strftime('%H:%M:%S')} com dispositivo: {device}")