# MCP PlayWright

AI-powered browser automation framework that generates Playwright test suites from plain-text prompts.

## Overview

Describe a user flow in natural language. The agent opens a real browser, inspects the live DOM, and writes Page Object Model files + pytest tests automatically — no manual selector hunting.

## Repository structure

```
MCP_PlayWright/
└── agent_browser/       # Core project
    ├── main.py          # CLI entry point
    ├── agent/
    │   ├── browser.py   # Browser actions (navigate, click, fill, snapshot…)
    │   ├── tools.py     # Tool definitions + dispatcher
    │   ├── prompts.py   # System prompt
    │   ├── runner.py    # Agent loop per LLM provider
    │   └── writer.py    # Saves generated files to disk
    └── utils/
        └── config.py    # Reads .env (BASE_URL, LOGIN_USER, LOGIN_PASSWORD)
```

## Quick start

```bash
cd agent_browser
python -m venv .venv
.venv\Scripts\activate       # Windows
pip install -r requirements.txt
playwright install chromium
```

Copy `.env.example` to `.env`:

```env
BASE_URL=https://your-app/login
LOGIN_USER=admin
LOGIN_PASSWORD=secret

LLM_PROVIDER=openai          # openai | claude | ollama
OPENAI_API_KEY=sk-...
```

Run the generator:

```bash
python main.py "Login, navigate to Auditoria > Lista de Auditorias and click Iniciar Auditoria"
```

The agent will create `pages/` and `tests/` inside `agent_browser/`. Review them and run:

```bash
pytest
```

## LLM providers

| `LLM_PROVIDER` | Required |
|---|---|
| `openai` (default) | `OPENAI_API_KEY` |
| `claude` | `ANTHROPIC_API_KEY` |
| `ollama` | Ollama running locally + `LLM_MODEL=<model>` |
