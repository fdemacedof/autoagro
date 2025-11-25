# 🌿 Kampu
**Sistema de Agricultura de Precisão.**

---

## 📖 Sobre o Projeto
O **Kampu** é um sistema inteligente de monitoramento vegetal focado em agricultura de precisão "artesanal". Diferente das grandes soluções industriais, o Kampu foca no cuidado individual da planta, utilizando Inteligência Artificial para identificar espécies, diagnosticar doenças e acompanhar estágios fenológicos (crescimento).

### 🏺 Por que "Kampu"?
O nome tem raízes na língua Tupi-Guarani, derivado de *kampu-ci* (Cambuci), que significa "pote de água" ou "vaso". Ele representa a essência do projeto: conter a vida e a sabedoria da terra através da tecnologia.

---

## 📂 Estrutura do Projeto
A organização atual do módulo de visão computacional é:

```text
kampu/
├── requirements.txt         # Dependências do Python
├── setup.sh                 # Script de instalação automática
└── vision_app/              # Módulo de Visão
    ├── app.py               # Servidor Flask (API + Lógica)
    ├── templates/           # Interface Web
    │   └── index.html
    ├── test/                # Scripts de teste automatizado
    │   └── run_tests.py
    └── models/              # (IMPORTANTE) Pasta dos modelos de Machine Learning
        ├── router_species.keras
        └── pepper/
            ├── health.keras
            └── growth.keras
```

---

## ⚙️ Instalação e Setup

### 1. Pré-requisitos
* Python 3.10 ou superior.
* Git.

### 2. Configuração do Ambiente
Recomendamos usar o script automático de setup (Linux/Mac/WSL):

```bash
chmod +x setup.sh
./setup.sh
```

⚠️ Evite instalar as dependências manualmente; o script de setup também baixa os modelos **.keras** necessários para o funcionamento da aplicação. 

---

## 🧠 Pipeline de Aplicação dos Modelos de Visão Computacional

O Kampu não utiliza um modelo genérico único. Ele opera com uma **Arquitetura Hierárquica de Decisão** para garantir maior precisão e modularidade.

### O Fluxo de Dados:
1.  **Entrada:** A imagem é capturada e sofre pré-processamento (Center Crop) para focar na planta.
2.  **Nível 1 (Roteador Taxonômico):** O primeiro modelo identifica *qual* é a planta.
3.  **Nível 2 (Especialistas):** Com base na espécie, o sistema aciona modelos específicos para aquela cultura.
   
---

## 🚀 Como Rodar

### Iniciar o Servidor
Com o ambiente virtual ativado:

```bash
python vision_app/app.py
```
O servidor estará acessível em: `http://localhost:5000`

### Interface Web
Acesse o link acima no navegador para usar a interface visual, onde é possível fazer upload de fotos ou usar a webcam para diagnóstico em tempo real.

---

## 🧪 Testes Automatizados
O projeto possui um script que valida a API contra um banco de imagens de teste.

```bash
python vision_app/test/run_tests.py
```
Isso enviará imagens de teste para o servidor e exibirá o diagnóstico e o tempo de resposta no terminal.

---

## 🔮 Roadmap e Próximos Passos
O módulo de visão (`vision_app`) é apenas o primeiro passo. O objetivo do Kampu é se tornar uma plataforma completa de monitoramento autônomo.

### Fases Futuras:
* **💧 Monitoramento Hídrico:** Integração de sensores capacitivos de umidade do solo para acionamento automático de rega.
* **🌡️ Clima:** Monitoramento de temperatura e umidade do ar para ajustes de ventilação em estufa.
* **☀️ Luminosidade:** Sensores de luz para garantir a fotossíntese ideal (e acionamento de grow-lights se necessário).
* **🌵 Novas Espécies:** Treinamento de modelos específicos para outras espécies.

---
