<#
  setup_env.ps1 — Setup automático do AutoAgro (Windows)
#>

Write-Host "🌿 Iniciando configuração do AutoAgro..." -ForegroundColor Green

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
pip install -r requirements.txt
pip install -e .

# === 3️⃣ Verificar ou gerar chave ===
$encPath = "plantid_key.enc"
if (-not (Test-Path $encPath)) {
    Write-Host "🔐 Nenhum arquivo '$encPath' encontrado."
    Write-Host "→ Gerando chave criptografada..."
    python -m autoagro.secure_key_utils encrypt
} else {
    Write-Host "✅ Arquivo de chave criptografada encontrado."
}

# === 4️⃣ Solicitar passphrase ===
if (-not $env:PLANT_ID_PASSPHRASE -or $env:PLANT_ID_PASSPHRASE.Trim() -eq "") {
    Write-Host "🔑 Digite a passphrase usada para criptografar a chave:"
    $sec = Read-Host -AsSecureString
    $bstr = [Runtime.InteropServices.Marshal]::SecureStringToBSTR($sec)
    $plain = [Runtime.InteropServices.Marshal]::PtrToStringBSTR($bstr)
    [Runtime.InteropServices.Marshal]::ZeroFreeBSTR($bstr)
    $env:PLANT_ID_PASSPHRASE = $plain
    Write-Host "✅ Passphrase definida na sessão atual."
} else {
    Write-Host "🔁 Usando passphrase já definida em \$env:PLANT_ID_PASSPHRASE."
}

# === 5️⃣ Validar passphrase (versão compatível com PowerShell) ===
Write-Host "🧪 Validando passphrase..."

$pyCode = 'from autoagro.secure_key_utils import decrypt_api_key; import os,sys; ' +
          'print("OK" if decrypt_api_key("plantid_key.enc", os.environ["PLANT_ID_PASSPHRASE"]) else "ERR")'

$val = python -c $pyCode 2>&1

if ($LASTEXITCODE -ne 0 -or -not $val.Contains("OK")) {
    Write-Host "❌ Passphrase inválida ou arquivo incorreto." -ForegroundColor Red
    exit 1
} else {
    Write-Host "✅ Passphrase validada com sucesso."
}

# === 6️⃣ Iniciar servidor ===
Write-Host "🚀 Iniciando servidor em http://127.0.0.1:8000 ..." -ForegroundColor Green
uvicorn autoagro.server:app --reload