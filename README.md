# IsCoolGPT – IA Study Assistant

IsCoolGPT é uma aplicação de **assistente de estudos** que combina um backend em FastAPI,
um frontend em React/Vite e modelos de linguagem (Gemma 3 e Gemini 2.0 Flash) para responder
perguntas em formato de chat, com histórico e respostas em Markdown.

O projeto foi pensado para a disciplina de Cloud, demonstrando:

- API moderna em FastAPI
- Containerização com Docker (multi-stage)
- Orquestração simples com Docker Compose
- Integração Contínua com GitHub Actions (pytest)
- Deploy em cloud usando Render (Docker)
- Frontend single-page consumindo a API

---

## Arquitetura

Visão geral da arquitetura atual:

```text
[Browser / Frontend React]
           |
           v
[FastAPI Backend + Servidor de arquivos estáticos]
    |                          |
    |                          +--> Servindo build do Vite (index.html, assets/)
    |
    +--> /ask/gemma  ----> Worker Gemma 3 (GEMMA3_URL)
    |
    +--> /ask/gemini ----> API Gemini (GEMINI_API_KEY)
```

Principais componentes:

- `app/main.py`
  - Cria a instância FastAPI
  - Configura CORS
  - Monta os arquivos estáticos do frontend (`/assets`, `/`)
  - Implementa endpoints:
    - `GET /health`
    - `POST /ask/gemma`
    - `POST /ask/gemini`
- `app/services/gemini_service.py`
  - Encapsula chamada à API do Gemini (Google)
- `app/services/local_gemma3_service.py`
  - Encapsula chamada ao worker local / tunelado do Gemma 3
- `frontend/`
  - Aplicação React + Vite com interface de chat
  - Selector de modelo (Gemma 3 / Gemini)
  - Histórico de mensagens armazenado em `localStorage`
  - Renderização das respostas em Markdown (biblioteca `marked`)

---

## Tecnologias

**Backend**

- Python 3.11
- FastAPI
- httpx (requisições async)
- python-dotenv (carregar `.env` em desenvolvimento)
- Pydantic (validação de payloads)
- Uvicorn

**Frontend**

- React (Vite)
- JavaScript
- marked (renderização de Markdown)

**Infra / DevOps**

- Docker (multi-stage build)
- Docker Compose
- GitHub Actions (CI com pytest)
- Render.com (Deploy Docker + CD)
- GitHub Secrets para variáveis sensíveis

---

## Variáveis de ambiente

O projeto usa variáveis de ambiente para não expor credenciais nem URLs sensíveis.

As principais são:

- `GEMMA3_URL`
  - URL do worker do Gemma 3 (ex.: `http://localhost:8009` ou URL do túnel ngrok)
  - O código garante que o endpoint `/generate` seja usado
- `GEMINI_API_KEY`
  - API key do Gemini (Google)
- Outras variáveis específicas do provedor de LLM podem ser incluídas no futuro

Em desenvolvimento, use um arquivo `.env` na raiz do projeto:

```env
GEMMA3_URL=http://localhost:8009
GEMINI_API_KEY=SEU_TOKEN_AQUI
```

No Docker Compose, esse `.env` é carregado via `env_file`.  
No GitHub Actions e no Render, use **Secrets / Environment variables** da plataforma.

---

## Estrutura de pastas (simplificada)

```text
IA-Study-Assistant/
├─ app/
│  ├─ main.py
│  ├─ services/
│  │  ├─ gemini_service.py
│  │  └─ local_gemma3_service.py
│  └─ ... (schemas, config, etc.)
├─ frontend/
│  ├─ index.html
│  ├─ src/
│  │  ├─ App.jsx
│  │  └─ main.jsx
│  └─ ...
├─ static/                # gerado pelo build do Vite (copiado no Docker multi-stage)
├─ tests/
│  └─ test_api.py
├─ Dockerfile
├─ docker-compose.yml
├─ requirements.txt
├─ pytest.ini
├─ .github/
│  └─ workflows/
│     └─ ci.yml
└─ README.md
```

> Obs.: a pasta `static/` normalmente é resultado do build do frontend
> e não deve ser commitada em repositórios públicos (pode ser gerada no CI/CD).

---

## Rodando localmente (sem Docker)

Pré-requisitos:

- Python 3.11+
- Node 18+ (para o frontend)
- pip

### 1. Backend

Crie e ative um ambiente virtual, depois instale as dependências:

```bash
python -m venv venv
source venv/bin/activate  # Linux/macOS
# .\venv\Scripts\activate  # Windows PowerShell

pip install --upgrade pip
pip install -r requirements.txt
```

Crie um arquivo `.env` na raiz com os valores necessários:

```env
GEMMA3_URL=http://localhost:8009
GEMINI_API_KEY=SEU_TOKEN_AQUI
```

Rode a API:

```bash
uvicorn app.main:app --reload --port 8000
```

A API ficará disponível em `http://localhost:8000`.

### 2. Frontend (modo desenvolvimento)

Dentro da pasta `frontend/`:

```bash
cd frontend
npm install
npm run dev
```

Por padrão, o Vite roda em `http://localhost:5173`.

No código do frontend (`App.jsx`) há uma constante `BASE_API_URL` que aponta
para a URL da API (em desenvolvimento ou produção). Ajuste se necessário.

---

## Rodando com Docker + Docker Compose

Pré-requisitos:

- Docker
- Docker Compose (ou `docker compose` CLI)

### Build e subida dos serviços

```bash
docker compose up --build
```

Isso irá:

- Construir a imagem usando o **Dockerfile multi-stage**
  - Stage 1: build do frontend (Vite)
  - Stage 2: imagem final do backend com static bundado em `/app/static`
- Subir o container exposeando a porta `8000`

A aplicação estará acessível em:

- `http://localhost:8000/` → frontend (build de produção do Vite)
- `http://localhost:8000/health` → health check
- `POST http://localhost:8000/ask/gemma`
- `POST http://localhost:8000/ask/gemini`

---

## Testes

Os testes são escritos com `pytest` e moram em `tests/`.

Para rodar localmente (com o venv ativo):

```bash
pytest
```

Dicas:

- Alguns testes usam o endpoint `/ask/gemma`. Caso queira que eles passem usando
  um worker real, certifique-se de que o `GEMMA3_URL` esteja configurado.
- Em ambiente de CI (GitHub Actions), as variáveis são injetadas via `secrets`.

---

## CI (GitHub Actions)

O workflow principal fica em `.github/workflows/ci.yml` e faz:

- Dispara em `push` e `pull_request` para `main`/`master`
- Configura Python 3.11
- Instala dependências (`requirements.txt` + `pytest` + `python-dotenv`)
- Roda `pytest`

As variáveis `GEMMA3_URL` e `GEMINI_API_KEY` são passadas via `secrets`:

```yaml
env:
  GEMMA3_URL: ${{ secrets.GEMMA3_URL }}
  GEMINI_API_KEY: ${{ secrets.GEMINI_API_KEY }}
```

---

## Deploy (Render)

O deploy em produção é feito no **Render.com**, usando:

- Serviço do tipo **Web Service (Docker)** apontando para o repositório GitHub
- Dockerfile multi-stage do projeto
- Variáveis de ambiente configuradas no painel do Render
- Auto deploy ativado na branch principal (CD simples)

A URL de produção atual (exemplo) é:

```text
https://ia-study-assistant.onrender.com
```

Em produção:

- O backend FastAPI e o frontend compilado vivem no mesmo container
- `GET /` serve o `index.html` do build
- Os assets do Vite são servidos via `/assets/...`

---

## Futuras melhorias

- Autenticação de usuário (perfis, histórico por conta)
- Suporte a mais modelos (por exemplo, OpenAI, Claude, etc.)
- Salvamento de sessões em banco de dados
- Página de configurações do estudante (tema, persona, nível de detalhe)
- Logging estruturado e observabilidade mais completa
