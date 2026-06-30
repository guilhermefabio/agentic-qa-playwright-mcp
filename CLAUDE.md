# agentic-qa-playwright-mcp — Codebase Guide

AI-powered Playwright test generator. Describe a user flow in plain text; the agent opens a real Chromium browser, inspects the live DOM, and writes Page Object Model classes + pytest tests automatically.

## Repository layout

```
MCP_PlayWright/
├── README.md                   # Full project documentation
├── LICENSE
├── pyproject.toml              # Root package metadata
└── agent_browser/              # Runnable application
    ├── main.py                 # CLI entry point (argparse + asyncio)
    ├── conftest.py             # pytest session-scoped `config` fixture
    ├── pytest.ini              # pytest config (browser: chromium, tests/)
    ├── .env.example            # Template — copy to .env and fill in
    ├── pyproject.toml          # Package deps (playwright, openai, anthropic…)
    ├── requirements.txt        # pip-installable dep list
    ├── agent/
    │   ├── browser.py          # Browser class — 9 async Playwright actions
    │   ├── tools.py            # Tool schemas (OpenAI + Anthropic) & dispatcher
    │   ├── prompts.py          # System prompt builder
    │   ├── runner.py           # TaskConfig dataclass + per-provider agent loops
    │   └── writer.py           # Parses LLM output and writes files to disk
    └── utils/
        └── config.py           # Config class — reads BASE_URL, LOGIN_USER, LOGIN_PASSWORD
```

## How it works

1. `main.py` parses CLI args and builds a `TaskConfig`.
2. `run_agent()` in `runner.py` starts Chromium via `Browser`, then enters a tool-call loop with the chosen LLM.
3. The LLM calls browser tools (defined in `tools.py`) to navigate, inspect, click, and fill fields.
4. When the LLM signals `stop` / `end_turn`, `writer.py` parses `<file path="…">` blocks and writes `pages/` and `tests/` to disk.
5. `pytest` runs the generated tests; `conftest.py` supplies the `config` fixture.

## Key design decisions

- **Always inspect before filling** — the system prompt requires `browser_get_inputs()` before any `browser_fill()` to avoid hardcoded selectors.
- **POM pattern** — generated page classes live in `pages/`, tests in `tests/`.
- **Locator priority**: `get_by_role(exact=True)` → `get_by_label` → `get_by_text(exact=True)`.
- **Two parallel LLM loops** — `_run_openai_compat` for OpenAI/Ollama, `_run_anthropic` for Claude; both share the same browser and tools.
- **Generated files are git-ignored** — `pages/` and `tests/` are excluded until the user reviews and commits them.

## Environment variables

| Variable | Required | Purpose |
|---|---|---|
| `BASE_URL` | For tests | Application URL |
| `LOGIN_USER` | For tests | Login username |
| `LOGIN_PASSWORD` | For tests | Login password |
| `LLM_PROVIDER` | No (default: `openai`) | `openai` \| `claude` \| `ollama` |
| `LLM_MODEL` | No | Override default model |
| `OPENAI_API_KEY` | If using `openai` | OpenAI key |
| `ANTHROPIC_API_KEY` | If using `claude` | Anthropic key |
| `OLLAMA_BASE_URL` | If using `ollama` | Default: `http://localhost:11434/v1` |

## Development setup

```bash
cd agent_browser
python -m venv .venv
.venv\Scripts\activate        # Windows
pip install -r requirements.txt
playwright install chromium
cp .env.example .env          # then fill in credentials and API key
```

## Running the generator

```bash
python main.py "Login and navigate to the dashboard"
python main.py "Checkout flow" --provider claude --headless --output ./generated
```

## Running generated tests

```bash
pytest               # all tests, headless
pytest --headed      # visible browser
pytest tests/test_login.py -v
```

## Constants and limits

`browser.py` defines module-level constants for all timeouts and content limits:

| Constant | Value | Used for |
|---|---|---|
| `_TIMEOUT_NAVIGATE` | 30 000 ms | `page.goto()` |
| `_TIMEOUT_CLICK` | 10 000 ms | `locator.click()`, `wait_for(visible)` |
| `_TIMEOUT_LOAD` | 15 000 ms | `wait_for_load_state("networkidle")` |
| `_SNAPSHOT_LIMIT` | 8 000 chars | Accessibility tree truncation |
| `_TEXT_LIMIT` | 4 000 chars | `get_text()` truncation |
| `_HTML_LIMIT` | 6 000 chars | `get_html()` truncation |

`runner.py` uses `_MAX_TOKENS = 8_096` for all LLM requests.
