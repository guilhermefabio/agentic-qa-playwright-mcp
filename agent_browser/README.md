# agent_browser

AI-powered Playwright test generator. Describe a user flow in plain text and the agent navigates a real browser, inspects the actual DOM, and generates Page Object Model files + pytest tests automatically.

## How it works

```
python main.py "Login, navigate to Auditoria > Lista de Auditorias and click Iniciar Auditoria"
```

The agent will:
1. Open a Chromium browser
2. Inspect real input fields before filling anything (`browser_get_inputs`)
3. Navigate the flow you described
4. Write `pages/` and `tests/` based on what it actually found in the DOM

## Project structure

```
agent_browser/
├── main.py              # CLI entry point
├── agent/
│   ├── browser.py       # Browser actions (navigate, click, fill, snapshot…)
│   ├── tools.py         # Tool definitions + dispatcher
│   ├── prompts.py       # System prompt
│   ├── runner.py        # Agent loop per LLM provider
│   └── writer.py        # Saves generated files to disk
└── utils/
    └── config.py        # Reads .env (BASE_URL, LOGIN_USER, LOGIN_PASSWORD)
```

## Setup

```bash
cd agent_browser
python -m venv .venv
.venv\Scripts\activate        # Windows
pip install -r requirements.txt
playwright install chromium
```

Copy `.env.example` to `.env` and fill in your values:

```env
BASE_URL=https://your-app/login
LOGIN_USER=admin
LOGIN_PASSWORD=secret

LLM_PROVIDER=openai           # openai | claude | ollama
OPENAI_API_KEY=sk-...
```

## LLM providers

| `LLM_PROVIDER` | Required |
|---|---|
| `openai` (default) | `OPENAI_API_KEY` |
| `claude` | `ANTHROPIC_API_KEY` |
| `ollama` | Ollama running locally + `LLM_MODEL=llama3.2` |

Override the model with `LLM_MODEL=gpt-4o-mini` (or any model the provider supports).

## Running generated tests

After the agent generates `pages/` and `tests/`, review the files and run:

```bash
pytest
```

> `pages/` and `tests/` are listed in `.gitignore` — commit them after reviewing.
