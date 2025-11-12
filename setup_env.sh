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
# shellcheck disable=SC1091
source venv/bin/activate

# === 2️⃣ Instalar dependências ===
echo "📦 Instalando dependências..."
pip install --upgrade pip
pip install -r requirements.txt
pip install -e .

# === 3️⃣ Verificar ou clonar o repositório PlantXViT ===
PLANT_PATH="PlantXViT/src/model.py"
if [ ! -f "$PLANT_PATH" ]; then
    echo "⬇️ Repositório PlantXViT não encontrado — clonando do GitHub..."
    if ! git clone https://github.com/sakanaowo/PlantXViT.git; then
        echo "❌ Falha ao clonar o repositório PlantXViT. Verifique sua conexão."
        exit 1
    fi
    echo "✅ Repositório PlantXViT clonado com sucesso."
else
    echo "✅ Repositório PlantXViT já encontrado localmente."
fi

# === 4️⃣ Verificar e baixar modelo pré-treinado ===
MODEL_DIR="models"
MODEL_PATH="$MODEL_DIR/plantxvit_best.pth"
MODEL_URL="https://huggingface.co/VishnuSivadasVS/plant-disease-classification/resolve/main/model.pth"

echo "🧠 Verificando modelo PlantXViT..."
if [ ! -f "$MODEL_PATH" ]; then
    echo "⬇️ Modelo não encontrado — baixando do Hugging Face..."
    mkdir -p "$MODEL_DIR"
    if ! wget -O "$MODEL_PATH" "$MODEL_URL"; then
        echo "❌ Falha ao baixar modelo. Baixe manualmente em:"
        echo "   $MODEL_URL"
        exit 1
    fi
    echo "✅ Modelo baixado e salvo em '$MODEL_PATH'"
else
    echo "✅ Modelo local encontrado em '$MODEL_PATH'"
fi

# === 5️⃣ Iniciar servidor ===
echo ""
echo "🚀 Iniciando servidor local PlantXViT em http://127.0.0.1:8000 ..."
uvicorn autoagro.server_local:app --reload

