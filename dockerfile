# 1. Imagem base do Python (pode ser 3.11 ou 3.12)
FROM python:3.11-slim

# 2. Definir diretório de trabalho dentro do container
WORKDIR /app

# 3. Copiar o requirements primeiro (melhora cache de build)
COPY requirements.txt .

# 4. Instalar dependências
RUN pip install --no-cache-dir -r requirements.txt

# 5. Copiar o restante do código para dentro da imagem
COPY . .

# 6. Expor a porta que o Uvicorn vai usar
EXPOSE 8000

# 7. Comando padrão para subir a API
# (app.main:app = arquivo app/main.py, objeto app = FastAPI)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
