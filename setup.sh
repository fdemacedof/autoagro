#!/bin/bash

# Cores para o terminal (pra ficar bonitão)
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}🌿 Iniciando Setup do KAMPU...${NC}"

# 1. Verifica se Python 3 está instalado
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Erro: Python 3 não encontrado. Instale o Python antes de continuar.${NC}"
    exit 1
fi

# 2. Criação do Ambiente Virtual (VENV)
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}Criando ambiente virtual (venv)...${NC}"
    python3 -m venv venv
else
    echo -e "${GREEN}Ambiente virtual já existe.${NC}"
fi

# 3. Ativação e Instalação de Dependências
echo -e "${YELLOW}Instalando dependências...${NC}"
source venv/bin/activate

if [ -f "requirements.txt" ]; then
    pip install --upgrade pip
    pip install -r requirements.txt
    echo -e "${GREEN}Dependências instaladas com sucesso!${NC}"
else
    echo -e "${RED}Erro: Arquivo requirements.txt não encontrado.${NC}"
    exit 1
fi

# 4. Criação da Estrutura de Pastas (Garantia)
echo -e "${YELLOW}Verificando estrutura de pastas...${NC}"
mkdir -p vision_app/templates
mkdir -p vision_app/models/pepper
mkdir -p vision_app/models/adenium
mkdir -p vision_app/models/tomato
mkdir -p vision_app/models/potato

# 5. Verificação/Download de Modelos (Lógica Futura)
echo -e "${YELLOW}Verificando modelos de IA...${NC}"

# Função placeholder para baixar modelos (Exemplo com wget ou gdown)
baixar_modelo_se_nao_existir() {
    local caminho_arquivo=$1
    local url_download=$2 # Futuramente você coloca o link do S3/Drive aqui

    if [ ! -f "$caminho_arquivo" ]; then
        echo -e "${RED}⚠️  Modelo ausente: $caminho_arquivo${NC}"
        # echo "Baixando de $url_download..."
        # wget -O "$caminho_arquivo" "$url_download"
        echo -e "   -> Por favor, copie o arquivo manualmente para esta pasta por enquanto."
    else
        echo -e "${GREEN}✅ Modelo encontrado: $caminho_arquivo${NC}"
    fi
}

# Verifica os 3 principais
baixar_modelo_se_nao_existir "vision_app/models/router_species.keras" "LINK_DO_ROUTER"
baixar_modelo_se_nao_existir "vision_app/models/pepper/health.keras" "LINK_HEALTH"
baixar_modelo_se_nao_existir "vision_app/models/pepper/growth.keras" "LINK_GROWTH"

# 6. Finalização
echo -e "\n${BLUE}=========================================${NC}"
echo -e "${GREEN}SETUP CONCLUÍDO COM SUCESSO! 🚀${NC}"
echo -e "${BLUE}=========================================${NC}"
echo -e "Para iniciar o servidor, execute:"
echo -e "  ${YELLOW}source venv/bin/activate${NC}"
echo -e "  ${YELLOW}python vision_app/app.py${NC}"
echo -e ""