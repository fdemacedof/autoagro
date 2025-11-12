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

# === 3️⃣ Verificar modelo PlantXViT ===
$MODEL_PATH = "models\plantxvit_best.pth"
$MODEL_DIR = "models"

Write-Host "🧠 Verificando modelo PlantXViT..."

if (-not (Test-Path $MODEL_PATH)) {
    Write-Host "⬇️ Modelo não encontrado — baixando pré-treinado do Hugging Face..."
    if (-not (Test-Path $MODEL_DIR)) {
        New-Item -ItemType Directory -Path $MODEL_DIR | Out-Null
    }

    $modelUrl = "https://huggingface.co/VishnuSivadasVS/plant-disease-classification/resolve/main/model.pth"
    try {
        Invoke-WebRequest -Uri $modelUrl -OutFile $MODEL_PATH -UseBasicParsing
        Write-Host "✅ Modelo baixado e salvo em '$MODEL_PATH'"
    } catch {
        Write-Host "❌ Falha ao baixar modelo automaticamente. Verifique sua conexão ou baixe manualmente:" -ForegroundColor Red
        Write-Host "   $modelUrl"
        exit 1
    }
} else {
    Write-Host "✅ Modelo local encontrado em '$MODEL_PATH'"
}

# === 4️⃣ Iniciar servidor ===
Write-Host ""
Write-Host "🚀 Iniciando servidor local PlantXViT em http://127.0.0.1:8000 ..." -ForegroundColor Green
uvicorn autoagro.server_local:app --reload
