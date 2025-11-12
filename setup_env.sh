#!/bin/bash
# ======================================================
# setup_env.sh — Setup automático do AutoAgro (Ubuntu/Linux)
# ======================================================

echo "🌿 Iniciando configuração do AutoAgro (modo local PlantXViT)..."

# === 1️⃣ Criar e ativar venv ===
if [ ! -d "venv" ]; then
    echo "📦 Criando ambiente virtual..."
    python3 -m venv venv
else
    echo "✅ Ambiente virtual já existe."
fi

echo "🔧 Ativando ambiente virtual..."
source venv/bin/activate

# === 2️⃣ Instalar dependências ===
echo "📦 Instalando dependências..."
pip install --upgrade pip
pip install -r requirements.txt
pip install -e .

# === 3️⃣ Verificar repositório PlantXViT ===
if [ ! -f "PlantXViT/src/model.py" ]; then
    echo "⬇️ Repositório PlantXViT não encontrado — clonando..."
    git clone https://github.com/sakanaowo/PlantXViT.git
else
    echo "✅ Repositório PlantXViT encontrado localmente."
fi

# === 4️⃣ Verificar modelo local ===
MODEL_PATH="PlantXViT/outputs/plantVillage/models/plantxvit_best_plantvillage.pth"

if [ ! -f "$MODEL_PATH" ]; then
    echo "❌ Modelo não encontrado em '$MODEL_PATH'"
    echo "   Verifique se o repositório PlantXViT contém o modelo exportado."
    exit 1
else
    echo "✅ Modelo local encontrado em '$MODEL_PATH'"
fi

# === 5️⃣ Iniciar servidor ===
echo ""
echo "🚀 Iniciando servidor local PlantXViT em http://127.0.0.1:8000 ..."
uvicorn autoagro.server_local:app --reload