# 0. Build do frontend (React + Vite) em uma imagem Node separada
FROM node:20-alpine AS frontend-build

# 0.1 Definir diretório de trabalho para o frontend
WORKDIR /frontend

# 0.2 Copiar apenas arquivos de dependência do frontend (melhora cache do build)
COPY frontend/package*.json ./

# 0.3 Instalar dependências do frontend
RUN npm install

# 0.4 Copiar o restante do código do frontend e gerar o build
COPY frontend/ .
RUN npm run build


# 1. Imagem base do Python (pode ser 3.11 ou 3.12)
FROM python:3.11-slim

# 2. Variáveis de ambiente úteis para o Python em produção
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# 3. Definir diretório de trabalho dentro do container
WORKDIR /app

# 4. Instalar dependências de sistema necessárias para algumas libs Python
RUN apt-get update \
    && apt-get install -y --no-install-recommends build-essential \
    && rm -rf /var/lib/apt/lists/*

# 5. Copiar o requirements primeiro (melhora cache de build)
COPY requirements.txt .

# 6. Instalar dependências Python
RUN pip install --no-cache-dir -r requirements.txt

# 7. Copiar o restante do código da API para dentro da imagem
COPY . .

# 8. Copiar o build do frontend (dist) para a pasta static usada pelo FastAPI
#    (garanta que o main.py está servindo ./static e o index.html em "/")
COPY --from=frontend-build /frontend/dist ./static

# 9. Expor a porta que o Uvicorn vai usar
EXPOSE 8000

# 10. Comando padrão para subir a API (app.main:app = arquivo app/main.py, objeto app = FastAPI)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
