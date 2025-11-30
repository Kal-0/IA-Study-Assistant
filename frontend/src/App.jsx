import { useEffect, useState } from "react";
import { marked } from "marked";

const BASE_API_URL = "https://ia-study-assistant.onrender.com";

const STORAGE_KEY = "iscool_chat_history";

marked.setOptions({
  breaks: true,
});

// ----- Configuração de modelos -----
const MODELS = [
  {
    id: "gemma",
    label: "Gemma 3 (worker) · padrão",
    endpoint: "/ask/gemma",
    displayName: "Gemma 3",
    isDefault: true,
  },
  {
    id: "gemini",
    label: "Gemini 2.0 Flash",
    endpoint: "/ask/gemini",
    displayName: "Gemini 2.0 Flash",
    isDefault: false,
  },
];

const DEFAULT_MODEL_ID =
  MODELS.find((m) => m.isDefault)?.id ?? MODELS[0]?.id ?? "gemma";

function getModelConfig(id) {
  return MODELS.find((m) => m.id === id) ?? MODELS[0];
}

function renderMarkdown(text) {
  return { __html: marked(text || "") };
}

function generateId() {
  if (typeof crypto !== "undefined" && crypto.randomUUID) {
    return crypto.randomUUID();
  }
  return `${Date.now()}-${Math.random().toString(36).slice(2, 8)}`;
}

// ----- Componentes de UI -----
function ModelSelector({ modelId, onChange, disabled, onClear, canClear }) {
  return (
    <div className="controls">
      <label htmlFor="model-select">Modelo:</label>
      <select
        id="model-select"
        value={modelId}
        onChange={(e) => onChange(e.target.value)}
        disabled={disabled}
      >
        {MODELS.map((m) => (
          <option key={m.id} value={m.id}>
            {m.label}
          </option>
        ))}
      </select>
      <button
        type="button"
        className="secondary"
        onClick={onClear}
        disabled={disabled || !canClear}
      >
        Limpar histórico
      </button>
    </div>
  );
}

function MessageList({ messages }) {
  if (!messages.length) {
    return (
      <section className="chat-window">
        <div className="empty-state">
          <p>
            <strong>Bem-vindo ao IsCoolGPT</strong>
          </p>
          <p>
            Faça sua pergunta e veja a resposta em Markdown com histórico.
          </p>
        </div>
      </section>
    );
  }

  return (
    <section className="chat-window">
      {messages.map((msg) => {
        const modelCfg = getModelConfig(msg.modelId || msg.model);
        const modelTag = modelCfg?.id?.toUpperCase() ?? "MODEL";

        return (
          <div
            key={msg.id}
            className={`message ${msg.role === "user" ? "user" : "assistant"}`}
          >
            <div className="meta">
              {msg.role === "user"
                ? "Você"
                : `IsCoolGPT · ${modelTag}`}
            </div>
            <div className="body">
              {msg.role === "assistant" ? (
                <div dangerouslySetInnerHTML={renderMarkdown(msg.text || "")} />
              ) : (
                <p>{msg.text}</p>
              )}
            </div>
          </div>
        );
      })}
    </section>
  );
}

function Composer({ value, onChange, onSubmit, loading, statusText }) {
  return (
    <form className="composer" onSubmit={onSubmit}>
      <textarea
        value={value}
        onChange={(e) => onChange(e.target.value)}
        placeholder="Digite sua pergunta aqui..."
        disabled={loading}
      />
      <div className="composer-footer">
        <div className="status">
          {loading && <span className="dot" />}
          {statusText}
        </div>
        <button type="submit" disabled={loading || !value.trim()}>
          Enviar ↵
        </button>
      </div>
    </form>
  );
}

// ----- Componente principal -----
function App() {
  const [messages, setMessages] = useState([]);
  const [modelId, setModelId] = useState(DEFAULT_MODEL_ID);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);

  const currentModel = getModelConfig(modelId);

  // carrega histórico
  useEffect(() => {
    try {
      const raw = localStorage.getItem(STORAGE_KEY);
      if (raw) {
        setMessages(JSON.parse(raw));
      }
    } catch {
      // ignore
    }
  }, []);

  // salva histórico
  useEffect(() => {
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(messages));
    } catch {
      // ignore
    }
  }, [messages]);

  function addMessage(msg) {
    setMessages((prev) => [
      ...prev,
      {
        id: generateId(),
        ...msg,
      },
    ]);
  }

  function clearHistory() {
    setMessages([]);
    localStorage.removeItem(STORAGE_KEY);
  }

  async function handleSubmit(e) {
    e.preventDefault();
    const question = input.trim();
    if (!question || loading) return;

    const endpoint = currentModel.endpoint;
    const fullUrl = BASE_API_URL + endpoint;

    addMessage({
      role: "user",
      text: question,
      modelId: currentModel.id,
    });
    setInput("");
    setLoading(true);

    try {
      const resp = await fetch(fullUrl, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question }),
      });

      let answerText;
      if (!resp.ok) {
        let detail = "";
        try {
          const data = await resp.json();
          detail = data.detail || JSON.stringify(data);
        } catch {
          detail = resp.statusText;
        }
        answerText = `Erro ${resp.status}. Detalhe: ${detail}`;
      } else {
        const data = await resp.json();
        answerText = data.answer || JSON.stringify(data);
      }

      addMessage({
        role: "assistant",
        text: answerText,
        modelId: currentModel.id,
      });
    } catch (err) {
      console.error(err);
      addMessage({
        role: "assistant",
        text:
          "❌ Não foi possível conectar à API. Verifique se o backend está online e tente novamente.",
        modelId: currentModel.id,
      });
    } finally {
      setLoading(false);
    }
  }

  const statusText = loading
    ? `Gerando resposta com ${currentModel.displayName}...`
    : `Pronto para responder.`;

  return (
    <div className="page">
      <main className="container">
        <header className="header">
          <div className="title">
            <h1>
              <span className="logo">is</span>IsCoolGPT
            </h1>
            <p>IA Assistente de estudos.</p>
          </div>

          <ModelSelector
            modelId={modelId}
            onChange={setModelId}
            disabled={loading}
            onClear={clearHistory}
            canClear={messages.length > 0}
          />
        </header>

        <MessageList messages={messages} />

        <Composer
          value={input}
          onChange={setInput}
          onSubmit={handleSubmit}
          loading={loading}
          statusText={statusText}
        />
      </main>
    </div>
  );
}

export default App;
