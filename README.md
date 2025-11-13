# Autoagro: Plataforma de Diagnóstico Visual Agrícola com PlantXViT

O **Autoagro** é um backend de inferência de Deep Learning (DL) que fornece diagnóstico rápido de saúde de plantas e identificação de espécies através da análise de imagens.  
A plataforma utiliza um modelo avançado **PlantXViT (Vision Transformer)** treinado no dataset **PlantVillage** para a classificação de **38 combinações de Espécie___Doença**.

Este repositório contém a lógica central da **API em FastAPI** para servir o modelo pré-treinado de forma eficiente.

---

## 1. Visão Geral e Capacidades Centrais

A arquitetura está otimizada para a classificação visual.  
O diagnóstico é limitado às *38 classes de cultura/doença* presentes no conjunto de dados **PlantVillage**.

### 1.1 Modelos de Deep Learning (DL)

#### **PlantXViT (Modelo Principal)**  
- **Arquitetura:** Vision Transformer (ViT-based)  
- **Tarefa:** Classificação de Espécie e Doença  
- **Desempenho:** *F1-Score > 99%*  
- **Função:** Modelo principal para diagnóstico das 38 classes do PlantVillage  

#### **ResNet-50 (Modelo de Referência)**  
- **Tarefa:** Classificação Genérica de Doenças  
- **Desempenho:** *93.3% – 99.54% F1-Score*  
- **Função:** Referência para pipeline de fine-tuning  

---

## 1.2 Escopo Operacional

O sistema Autoagro entrega duas funções principais via análise de imagem:

1. **Identificação de Espécies + Diagnóstico:**  
   Classificação em uma das 38 combinações *Espécie___Doença*.

2. **Serviço de API de Baixa Latência:**  
   FastAPI para servir inferência do PlantXViT em produção.

---

## 2. Configuração Técnica e Instalação

O ambiente requer Python, FastAPI e bibliotecas de Deep Learning (PyTorch).

### 2.1 Dependências Principais

As dependências são geridas via `requirements.txt`.

#### Categoria: Servidor API
- `fastapi`, `uvicorn[standard]`  
→ Backend de alta performance para servir a inferência

#### Categoria: Deep Learning
- `torch`, `torchvision`, `Pillow`  
→ Núcleo para manipulação e inferência dos modelos

#### Categoria: Utilidades
- `tqdm`, `requests`, `rich`  
→ Logging, utilidades e comunicação HTTP

---

## 2.2 Instruções de Configuração

Execute os passos (baseados em `setup_env.sh`):

```bash
# 1. Cria e ativa o ambiente virtual Python
python3 -m venv venv
source venv/bin/activate

# 2. Atualiza o pip e instala dependências
pip install --upgrade pip
pip install -r requirements.txt

# 3. Instala o pacote local (modo editável)
pip install -e .

# 4. Requisito crítico: Clonar o repositório PlantXViT
git clone https://github.com/sakanaowo/PlantXViT.git
```

**Qualidade de Código:**  
Recomenda-se o uso de Black para manter padrão PEP8.

---

## 3. Guia de Uso: Como Obter um Diagnóstico

A API FastAPI recebe uma imagem e retorna o diagnóstico via endpoint **`/analyze`**.

### 3.1 Etapa 1: Captura da Imagem

A precisão depende da qualidade da imagem:

- **Foco e iluminação:** Boa luz natural e nitidez  
- **Enquadramento:** A folha deve ocupar a maior parte do frame  
- **Envio:** Feito via HTTP POST para `/analyze`

---

### 3.2 Etapa 2: Parâmetros de Inferência

| Parâmetro         | Valor         | Descrição |
|------------------|----------------|-----------|
| Modelo Utilizado | PlantXViT      | Classificação de Espécie/Doença |
| Tamanho Imagem   | 224×224 px     | Redimensionamento |
| MIN_PROB         | 0.7            | Mínimo para retornar previsão |

---

### 3.3 Resultado da API

O retorno segue o padrão **Espécie___Doença**.

**Exemplos:**

- `Tomato___Tomato_Yellow_Leaf_Curl_Virus`  
  → Tomateiro infectado por vírus do enrolamento amarelo da folha

- `Apple___healthy`  
  → Maçã saudável

- `Corn_(maize)___Common_rust_`  
  → Milho com ferrugem comum

Se nenhuma classe atingir **probabilidade ≥ 0.7**, uma exceção é retornada.

---

## 4. Próximos Passos (Roadmap)

### 🔧 Fine-Tuning dos Modelos
- Pipeline MLOps para novas doenças regionais  
- Transfer learning com learning rates baixos  

### 💻 Front-End Web
- Upload de imagens  
- Integração com webcam  
- Inferência assíncrona com FastAPI  

### 📱 App Mobile
- Diagnóstico em campo via câmera  
- Edge inference (modelos leves no dispositivo)

---

