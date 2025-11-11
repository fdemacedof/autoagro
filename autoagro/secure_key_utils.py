# secure_key_utils.py
"""
Ferramentas para criptografar e descriptografar a API key da Plant.id.
Cada usuário deve gerar sua própria chave e senha pessoal.

Uso rápido no terminal:
    python secure_key_utils.py encrypt
    python secure_key_utils.py decrypt
"""

import base64
import json
import os
from getpass import getpass
from typing import Optional
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.fernet import Fernet
from cryptography.hazmat.backends import default_backend


# ============================================================
# 🔑 Utilitários internos
# ============================================================

def _derive_key(password: bytes, salt: bytes, iterations: int = 390000) -> bytes:
    """Deriva uma chave Fernet segura a partir de uma senha e um salt."""
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=iterations,
        backend=default_backend(),
    )
    return base64.urlsafe_b64encode(kdf.derive(password))


# ============================================================
# 🧩 Funções principais (usadas no pipeline)
# ============================================================

def encrypt_api_key(
    api_key: str,
    passphrase: str,
    out_path: str = "plantid_key.enc"
) -> None:
    """Criptografa uma API key e grava o arquivo .enc contendo salt + token."""
    salt = os.urandom(16)
    key = _derive_key(passphrase.encode(), salt)
    f = Fernet(key)
    token = f.encrypt(api_key.encode())

    payload = {
        "salt": base64.b64encode(salt).decode(),
        "token": base64.b64encode(token).decode(),
    }

    with open(out_path, "w") as fh:
        json.dump(payload, fh)

    print(f"✅ Arquivo criptografado salvo em: {out_path}")
    print("⚠️ Guarde sua passphrase com segurança — ela NÃO é armazenada.")


def decrypt_api_key(enc_path: str, passphrase: str) -> str:
    """Descriptografa e retorna a API key em texto claro."""
    with open(enc_path, "r") as fh:
        blob = json.load(fh)
    salt = base64.b64decode(blob["salt"])
    token = base64.b64decode(blob["token"])
    key = _derive_key(passphrase.encode(), salt)
    f = Fernet(key)
    return f.decrypt(token).decode()


# ============================================================
# 🚀 Interface CLI opcional
# ============================================================

if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2 or sys.argv[1] not in ("encrypt", "decrypt"):
        print("Uso: python secure_key_utils.py [encrypt|decrypt]")
        sys.exit(1)

    mode = sys.argv[1]
    if mode == "encrypt":
        print("=== Encriptar API key da Plant.id ===")
        api_key = getpass("Cole sua API key (texto escondido): ").strip()
        passphrase = getpass("Escolha uma passphrase (não a perca): ").strip()
        confirm = getpass("Confirme a passphrase: ").strip()
        if passphrase != confirm:
            print("❌ Passphrases não conferem. Abortando.")
            sys.exit(1)
        out_file = input("Arquivo de saída [plantid_key.enc]: ").strip() or "plantid_key.enc"
        encrypt_api_key(api_key, passphrase, out_path=out_file)

    elif mode == "decrypt":
        print("=== Descriptografar API key da Plant.id ===")
        enc_file = input("Caminho do arquivo .enc [plantid_key.enc]: ").strip() or "plantid_key.enc"
        passphrase = getpass("Digite sua passphrase: ").strip()
        try:
            key = decrypt_api_key(enc_file, passphrase)
            print(f"\n✅ API key descriptografada: {key}")
        except Exception as e:
            print(f"❌ Erro ao descriptografar: {e}")