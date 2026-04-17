import cv2
import os
from pathlib import Path
from PIL import Image

def obter_timestamp(caminho_arquivo):
    """
    Tenta ler a data de criação original (EXIF) da imagem.
    Se não conseguir, usa a data de modificação do arquivo no sistema.
    """
    try:
        with Image.open(caminho_arquivo) as img:
            exif = img._getexif()
            if exif:
                # O código 36867 corresponde a 'DateTimeOriginal' no padrão EXIF
                if 36867 in exif:
                    return exif[36867]
    except Exception:
        pass
    
    # Fallback: retorna o tempo de modificação do sistema operacional
    return os.path.getmtime(caminho_arquivo)

def criar_timelapse(pasta_origem, arquivo_saida, fps=30):
    caminho_pasta = Path(pasta_origem)
    formatos_suportados = ('.png', '.jpg', '.jpeg', '.bmp')
    
    # 1. Coletar imagens
    arquivos = [str(f) for f in caminho_pasta.iterdir() if f.suffix.lower() in formatos_suportados]
    
    if not arquivos:
        print("Erro: Nenhuma imagem encontrada na pasta especificada.")
        return

    print(f"Encontradas {len(arquivos)} imagens. Lendo metadados e ordenando...")

    # 2. Ordenar usando os metadados EXIF ou OS Timestamp
    arquivos.sort(key=obter_timestamp)

    # 3. Ler a primeira imagem para definir a resolução base
    primeira_img = cv2.imread(arquivos[0])
    altura, largura, _ = primeira_img.shape
    tamanho_video = (largura, altura)

    # 4. Configurar o gerador de vídeo
    # 'mp4v' é um codec excelente e com boa compatibilidade para arquivos .mp4
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    video = cv2.VideoWriter(arquivo_saida, fourcc, fps, tamanho_video)

    print(f"Iniciando renderização do vídeo (Resolução: {largura}x{altura} a {fps} FPS)...")

    # 5. Processar e adicionar cada frame
    for idx, caminho in enumerate(arquivos):
        img = cv2.imread(caminho)
        
        if img is None:
            print(f"\nAviso: Não foi possível ler a imagem {caminho}. Pulando.")
            continue

        # Redimensionar a imagem para o tamanho base. 
        # (O OpenCV falha silenciosamente se tentar juntar imagens de tamanhos diferentes num mesmo vídeo).
        if (img.shape[1], img.shape[0]) != tamanho_video:
            img = cv2.resize(img, tamanho_video)
            
        video.write(img)
        
        # Feedback visual no terminal
        if (idx + 1) % 10 == 0 or (idx + 1) == len(arquivos):
            print(f"Progresso: {idx + 1}/{len(arquivos)} frames processados", end='\r')

    # Liberar recursos
    video.release()
    print(f"\n\nSucesso! Timelapse salvo como: {arquivo_saida}")

# ==========================================
# CONFIGURAÇÕES DE USO
# ==========================================
pasta_das_fotos = 'assets/pictures_to_video'       # Coloque o caminho da sua pasta aqui
nome_do_video = 'kampu_sementes.mp4'      # Nome do arquivo final
frames_por_segundo = 15                  # 24 ou 30 para vídeo padrão, 60 para movimento super suave

# Executa o código
criar_timelapse(pasta_das_fotos, nome_do_video, frames_por_segundo)