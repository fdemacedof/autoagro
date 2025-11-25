import os
import requests
import json
import time

# --- CONFIGURAÇÕES ---
API_URL = "http://localhost:5000/analisar_planta"
DATA_DIR = "vision_app/test/data" # Caminho relativo da raiz 'kampu'

# Cores
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
RESET = '\033[0m'
BLUE = '\033[94m'

def testar_api():
    print(f"{YELLOW}🚀 Iniciando Testes do KAMPU...{RESET}")
    print(f"📂 Varrendo subpastas em: {DATA_DIR}\n")
    
    # 1. Encontra todas as imagens (Recursivo / Profundo)
    imagens_encontradas = []
    
    # os.walk desce em todas as subpastas (pepper, tomato, etc)
    for root, dirs, files in os.walk(DATA_DIR):
        for file in files:
            if file.lower().endswith(('.jpg', '.jpeg', '.png', '.webp')):
                caminho_completo = os.path.join(root, file)
                imagens_encontradas.append(caminho_completo)

    if not imagens_encontradas:
        print(f"{RED}❌ Nenhuma imagem encontrada em {DATA_DIR} ou suas subpastas.{RESET}")
        return

    print(f"📋 Total de imagens: {len(imagens_encontradas)}\n")

    acertos = 0
    
    # 2. Testa cada imagem encontrada
    for caminho_img in imagens_encontradas:
        # Pega o nome do arquivo e da pasta pai para exibir (ex: pepper/teste.jpg)
        nome_arquivo = os.path.basename(caminho_img)
        nome_pasta = os.path.basename(os.path.dirname(caminho_img))
        
        print(f"📸 {BLUE}[{nome_pasta}]{RESET} {nome_arquivo}...", end=" ")
        
        try:
            inicio = time.time()
            with open(caminho_img, 'rb') as img:
                # Envia para o servidor
                response = requests.post(API_URL, files={'image': img})
            
            tempo = (time.time() - inicio) * 1000

            if response.status_code == 200:
                data = response.json()
                
                print(f"{GREEN}OK ({tempo:.0f}ms){RESET}")
                
                # Exibe o diagnóstico
                print(f"   🌱 Espécie: {data.get('especie')} ({data.get('confianca')})")
                
                if 'saude' in data:
                    print(f"   🏥 Saúde: {data.get('saude')}")
                
                # --- LINHA QUE FALTAVA ---
                if 'estagio' in data:
                    print(f"   📈 Estágio: {data.get('estagio')}")
                # -------------------------

                if 'alerta' in data:
                    print(f"   🧚 {data.get('alerta')}")
                
                acertos += 1
                
                acertos += 1
            else:
                print(f"{RED}ERRO {response.status_code}{RESET}")
                print(f"   Msg: {response.text}")
            
            print("-" * 40)

        except requests.exceptions.ConnectionError:
            print(f"\n{RED}❌ FALHA DE CONEXÃO{RESET}")
            print("   O servidor caiu ou não foi iniciado.")
            return
        except Exception as e:
            print(f"{RED}ERRO INESPERADO: {e}{RESET}")

    print(f"\n🏁 Sucesso: {acertos}/{len(imagens_encontradas)}")

if __name__ == "__main__":
    testar_api()