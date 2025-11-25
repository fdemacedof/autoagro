#!/bin/bash

# Cores para o terminal
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}🌿 Iniciando Setup do KAMPU...${NC}"

# 1. Verifica Python
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Erro: Python 3 não encontrado.${NC}"
    echo "Instale o Python 3 antes de continuar."
    exit 1
fi

# 2. Cria VENV
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}Criando ambiente virtual (venv)...${NC}"
    python3 -m venv venv
else
    echo -e "${GREEN}Ambiente virtual já existe.${NC}"
fi

# 3. Ativa e Instala Dependências
echo -e "${YELLOW}Instalando dependências...${NC}"
source venv/bin/activate

if [ -f "requirements.txt" ]; then
    pip install --upgrade pip
    pip install -r requirements.txt
    echo -e "${GREEN}Dependências instaladas!${NC}"
else
    echo -e "${RED}Erro: arquivo requirements.txt não encontrado.${NC}"
    exit 1
fi

# 4. Cria Estrutura de Pastas Local
echo -e "${YELLOW}Garantindo estrutura de pastas...${NC}"
mkdir -p vision_app/templates
mkdir -p vision_app/models/pepper
mkdir -p vision_app/models/adenium
mkdir -p vision_app/models/tomato
mkdir -p vision_app/models/potato
mkdir -p vision_app/test/data

# 5. Função de Download do Drive
baixar_do_drive() {
    local caminho_local=$1
    local file_id=$2

    # Verifica se o arquivo já existe
    if [ ! -f "$caminho_local" ]; then
        echo -e "${BLUE}⬇️  Baixando modelo para: $caminho_local ...${NC}"
        
        # O gdown baixa direto pelo ID
        # --fuzzy ajuda a achar o arquivo mesmo se o drive mudar algo na URL
        gdown "$file_id" -O "$caminho_local" --fuzzy
        
        if [ $? -eq 0 ]; then
            echo -e "${GREEN}✅ Download concluído!${NC}"
        else
            echo -e "${RED}❌ Falha ao baixar. Verifique se o link é público.${NC}"
        fi
    else
        echo -e "${GREEN}✅ Arquivo já existe: $caminho_local${NC}"
    fi
}

# --- DOWNLOAD DOS MODELOS (SEUS IDs REAIS) ---
echo -e "${YELLOW}Verificando modelos de IA no Google Drive...${NC}"

# 1. ROUTER (Modelo Geral) -> Vai para a raiz de models/
# ID extraído: 1OXytjhOl36avg7LBgSaGwD17XU-HhgkK
baixar_do_drive "vision_app/models/router_species.keras" "1OXytjhOl36avg7LBgSaGwD17XU-HhgkK"

# 2. PIMENTA SAÚDE (Modelo de Doenças) -> Vai para models/pepper/
# ID extraído: 15mDkmiwMyNvhThztWjGcwhWv40a-n7y7
baixar_do_drive "vision_app/models/pepper/health.keras" "15mDkmiwMyNvhThztWjGcwhWv40a-n7y7"

# 3. PIMENTA CRESCIMENTO (Modelo de Estágio) -> Vai para models/pepper/
# ID extraído: 1ELTvb-2X9bWVDX4EAGa2qipU0iFK0nj6
baixar_do_drive "vision_app/models/pepper/growth.keras" "1ELTvb-2X9bWVDX4EAGa2qipU0iFK0nj6"

# 6. Finalização
echo -e "\n${BLUE}=========================================${NC}"
echo -e "${GREEN}SETUP KAMPU FINALIZADO! 🚀${NC}"
echo -e "${BLUE}=========================================${NC}"
echo -e "Para rodar o servidor:"
echo -e "  ${YELLOW}source venv/bin/activate${NC}"
echo -e "  ${YELLOW}python vision_app/app.py${NC}"