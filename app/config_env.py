import os
from dotenv import load_dotenv


# Carrega variáveis do arquivo .env automaticamente
load_dotenv()


def get_env(env_key: str) -> str:
    """Pega o valor de uma variável de ambiente a partir da chave fornecida."""
    value = os.getenv(env_key)
    if value is None:
        print(f"Variável de ambiente '{env_key}' não está definida.")
        return None
    return value