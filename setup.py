from setuptools import setup, find_packages

setup(
    name="autoagro",
    version="0.2.0",
    description="Aplicação backend local para identificação e análise de saúde de plantas usando o modelo PlantXViT.",
    author="Felipe Ferreira",
    author_email="felipe.macedo@hupdata.com",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        # Servidor e API
        "fastapi>=0.109.0",
        "uvicorn[standard]>=0.23.0",

        # Deep learning e processamento de imagem
        "torch>=2.1.0",
        "torchvision>=0.16.0",
        "Pillow>=10.0.0",

        # Utilidades
        "tqdm>=4.66.0",
        "requests>=2.31.0",
    ],
    python_requires=">=3.9",
    entry_points={
        "console_scripts": [
            "autoagro-server=autoagro.server_local:app",
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
)