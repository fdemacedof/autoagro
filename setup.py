from setuptools import setup, find_packages

setup(
    name="autoagro",
    version="0.1.0",
    description="Aplicação backend para identificação e análise de saúde de plantas via Plant.id",
    author="Felipe Ferreira",
    author_email="felipe.macedo@hupdata.com",
    packages=find_packages(),
    install_requires=[
        "fastapi",
        "uvicorn",
        "cryptography",
        "requests",
    ],
    python_requires=">=3.9",
)