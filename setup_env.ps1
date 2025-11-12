<#
  setup_env.ps1 — Setup automático do AutoAgro (modo local PlantXViT)
#>

Write-Host "🌿 Iniciando configuração do AutoAgro (modo local)..." -ForegroundColor Green

# === 1️⃣ Criar e ativar venv ===
if (-not (Test-Path ".\venv")) {
    Write-Host "📦 Criando ambiente virtual..."
    python -m venv venv
} else {
    Write-Host "✅ Ambiente virtual já existe."
}

Write-Host "🔧 Ativando ambiente virtual..."
& .\venv\Scripts\activate

# === 2️⃣ Instalar dependências ===
Write-Host "📦 Instalando dependências..."
pip install --upgrade pip
pip install -r requirements.txt
pip install -e .

# === 3️⃣ Verificar ou clonar o repositório PlantXViT ===
$plantPath = "PlantXViT"
if (-not (Test-Path "$plantPath\src\model.py")) {
    Write-Host "⬇️ Repositório PlantXViT não encontrado — clonando do GitHub..."
    try {
        git clone https://github.com/sakanaowo/PlantXViT.git
        Write-Host "✅ Repositório PlantXViT clonado com sucesso."
    } catch {
        Write-Host "❌ Falha ao clonar o repositório PlantXViT. Verifique sua conexão com a internet." -ForegroundColor Red
        exit 1
    }
} else {
    Write-Host "✅ Repositório PlantXViT já encontrado localmente."
}

# === 4️⃣ Verificar e baixar modelo pré-treinado ===
$MODEL_PATH = "models\plantxvit_best.pth"
$MODEL_DIR = "models"

Write-Host "🧠 Verificando modelo PlantXViT..."
if (-not (Test-Path $MODEL_PATH)) {
    Write-Host "⬇️ Modelo não encontrado — baixando do Hugging Face..."
    if (-not (Test-Path $MODEL_DIR)) {
        New-Item -ItemType Directory -Path $MODEL_DIR | Out-Null
    }

    $modelUrl = "https://huggingface.co/VishnuSivadasVS/plant-disease-classification/resolve/main/model.pth"
    try {
        Invoke-WebRequest -Uri $modelUrl -OutFile $MODEL_PATH -UseBasicParsing
        Write-Host "✅ Modelo baixado e salvo em '$MODEL_PATH'"
    } catch {
        Write-Host "❌ Falha ao baixar modelo automaticamente. Baixe manualmente em:" -ForegroundColor Red
        Write-Host "   $modelUrl"
        exit 1
    }
} else {
    Write-Host "✅ Modelo local encontrado em '$MODEL_PATH'"
}

# === 5️⃣ Iniciar servidor ===
Write-Host ""
Write-Host "🚀 Iniciando servidor local PlantXViT em http://127.0.0.1:8000 ..." -ForegroundColor Green
uvicorn autoagro.server_local:app --reload

