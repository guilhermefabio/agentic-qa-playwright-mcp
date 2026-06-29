# agent_browser

AI-powered Playwright test generator. Describe a user flow in plain text — the agent opens a real browser, inspects the live DOM, executes the flow, and writes Page Object Model classes + pytest tests automatically.

---

## Flowchart — agent loop

```mermaid
flowchart TD
    A([python main.py &lt;PROMPT&gt;]) --> B[Parse CLI args\nload .env]
    B --> C[Build TaskConfig\nprovider · model · url · headless]
    C --> D[Start Chromium\nvia Playwright]
    D --> E[Send system prompt + user prompt\nto LLM API]

    E --> F{LLM response\nstop_reason}
    F -->|tool_calls| G[Dispatch browser tool]
    G --> H[(Real Chromium DOM)]
    H --> I[Return result string to LLM]
    I --> E

    F -->|stop / end_turn| J[Parse <file path=...> blocks]
    J --> K[Write pages/*.py\nWrite tests/*.py]
    K --> L[Close browser]
    L --> M([Done])
```

---

## Flowchart — DOM inspection before fill

```mermaid
sequenceDiagram
    participant LLM
    participant Tools
    participant Browser

    LLM->>Tools: browser_navigate(url)
    Tools->>Browser: page.goto(url, wait_until=networkidle)
    Browser-->>LLM: "Página: Title | URL: ..."

    LLM->>Tools: browser_get_inputs()
    Tools->>Browser: evaluate() → querySelectorAll(input,textarea,select)
    Browser-->>LLM: [{tag, type, id, name, placeholder, label}, ...]

    Note over LLM: Selects correct selector\nfrom real attributes

    LLM->>Tools: browser_fill(selector, value)
    Tools->>Browser: locator(selector).fill(value)
    Browser-->>LLM: "Preencheu 'input[name=username]'"

    LLM->>Tools: browser_snapshot()
    Tools->>Browser: page.accessibility.snapshot()
    Browser-->>LLM: accessibility tree JSON
```

---

## Project structure

```
agent_browser/
├── main.py              # CLI entry point (argparse + asyncio)
├── conftest.py          # pytest fixture: config (session-scoped)
├── .env.example         # Template for environment variables
├── requirements.txt
├── agent/
│   ├── browser.py       # Browser class — 9 async actions
│   ├── tools.py         # Tool schemas (OpenAI + Anthropic) & dispatcher
│   ├── prompts.py       # System prompt builder
│   ├── runner.py        # TaskConfig + agent loops per provider
│   └── writer.py        # LLM output parser → writes files to disk
└── utils/
    └── config.py        # Reads BASE_URL, LOGIN_USER, LOGIN_PASSWORD from .env
```

---

## Setup

```bash
python -m venv .venv
.venv\Scripts\activate        # Windows
# source .venv/bin/activate   # Linux / macOS

pip install -r requirements.txt
playwright install chromium
```

Copy `.env.example` to `.env`:

```env
BASE_URL=https://your-app/login
LOGIN_USER=admin
LOGIN_PASSWORD=secret

LLM_PROVIDER=openai           # openai | claude | ollama
OPENAI_API_KEY=sk-...
# ANTHROPIC_API_KEY=sk-ant-...
# OLLAMA_BASE_URL=http://localhost:11434/v1
# LLM_MODEL=gpt-4o-mini
```

---

## CLI options

| Argument | Description |
|---|---|
| `PROMPT` (positional) | Natural language description of the flow |
| `--url URL` | Base URL (overrides `BASE_URL`) |
| `--user USER` | Login user (overrides `LOGIN_USER`) |
| `--password PASS` | Login password (overrides `LOGIN_PASSWORD`) |
| `--provider {openai,claude,ollama}` | LLM provider (overrides `LLM_PROVIDER`) |
| `--model MODEL` | Model name (overrides `LLM_MODEL`) |
| `--headless` | Run browser without visible window |
| `--output DIR` / `-o DIR` | Output directory (default: `.`) |
| `--context TEXT` / `-c TEXT` | Extra context about the site |

---

## Browser tools

| Tool | What it does |
|---|---|
| `browser_navigate` | `page.goto(url, wait_until="networkidle")` |
| `browser_get_inputs` | Lists all visible fields with real `id/name/type/placeholder/label` |
| `browser_snapshot` | Accessibility tree — roles, names, states (up to 8 000 chars) |
| `browser_click` | `locator.click()` then waits `networkidle` |
| `browser_fill` | Waits for visibility, then `locator.fill(value)` |
| `browser_press_key` | `keyboard.press(key)` then waits `networkidle` |
| `browser_get_text` | `inner_text("body")` — up to 4 000 chars |
| `browser_get_html` | `inner_html(selector)` — up to 6 000 chars |
| `browser_wait` | `asyncio.sleep(ms / 1000)` |

---

## LLM providers

| `LLM_PROVIDER` | Default model | Required |
|---|---|---|
| `openai` | `gpt-4o` | `OPENAI_API_KEY` |
| `claude` | `claude-sonnet-4-6` | `ANTHROPIC_API_KEY` |
| `ollama` | `llama3.2` | Ollama running locally |

---

## Running generated tests

After the agent writes `pages/` and `tests/`:

```bash
# Run everything
pytest

# Headed (visible browser)
pytest --headed

# Single test
pytest tests/test_login.py -v
```

The `conftest.py` provides a session-scoped `config` fixture that loads `.env`.
`page: Page` comes from `pytest-playwright`; `config: Config` comes from `conftest.py`.

> `pages/` and `tests/` are in `.gitignore` — review then commit.
