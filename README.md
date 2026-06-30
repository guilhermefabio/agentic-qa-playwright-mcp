# agentic-qa-playwright-mcp

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.12%2B-blue)](https://www.python.org/)
[![Playwright](https://img.shields.io/badge/Playwright-Chromium-green)](https://playwright.dev/)
[![Lint](https://github.com/guilhermefabio/agentic-qa-playwright-mcp/actions/workflows/lint.yml/badge.svg)](https://github.com/guilhermefabio/agentic-qa-playwright-mcp/actions/workflows/lint.yml)

AI-powered browser automation framework that generates complete Playwright test suites — Page Object Model + pytest — from plain-text prompts. Supports OpenAI, Anthropic Claude and Ollama out of the box.

---

## Table of Contents

- [Overview](#overview)
- [How it works](#how-it-works)
- [Repository structure](#repository-structure)
- [Quick start](#quick-start)
- [CLI reference](#cli-reference)
- [LLM providers](#llm-providers)
- [Browser tools](#browser-tools)
- [Generated output](#generated-output)
- [Running generated tests](#running-generated-tests)
- [Code quality](#code-quality)
- [Advanced usage](#advanced-usage)
- [Environment variables](#environment-variables)
- [License](#license)

---

## Overview

Describe a user flow in natural language. The agent:

1. Opens a **real Chromium browser** (visible or headless)
2. Navigates to your application
3. Inspects the **live DOM** — field ids, names, labels, roles — before touching anything
4. Executes the flow step-by-step, taking accessibility snapshots after each action
5. Writes **Page Object Model classes** + **pytest test files** based on what it actually found

No manual selector hunting. No brittle CSS hardcoding.

---

## How it works

### The analogy: an AI assistant that learns to test websites

Imagine you need to verify that the login of a system works correctly. Normally you would hire a QA engineer to do that. That person would:

1. Open the browser manually
2. Look at the screen and identify the fields ("here is a username field, there is a password field")
3. Fill in test data and click "Sign in"
4. Check whether the right page opened
5. Write a script documenting every step so another developer can repeat the test automatically

**This project does exactly that — with an AI model in place of the human QA engineer.**

---

### The full journey in 5 steps

```
┌─────────────────────────────────────────────────────────────────┐
│                                                                 │
│   YOU type an instruction in plain English                      │
│   e.g. "Log in and navigate to the dashboard"                  │
│                                                                 │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│  STEP 1 — Configuration                                         │
│                                                                 │
│  The system reads your .env file:                               │
│  • Site URL                                                     │
│  • Login username and password                                  │
│  • Which AI to use (OpenAI, Claude, or Ollama)                  │
│                                                                 │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│  STEP 2 — Browser opens                                         │
│                                                                 │
│  A real Chromium browser is launched (visible on screen         │
│  or running silently in the background).                        │
│  Your site is loaded automatically.                             │
│                                                                 │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│  STEP 3 — The AI "reads" the page and acts (smart loop)        │
│                                                                 │
│  ┌──────────────┐    request      ┌──────────────────────────┐  │
│  │              │ ─────────────► │                          │  │
│  │   AI (LLM)   │                │     Browser Tools        │  │
│  │  reasons &   │ ◄───────────── │  • Inspect fields        │  │
│  │  decides     │    result      │  • Click buttons         │  │
│  │              │                │  • Fill forms            │  │
│  └──────────────┘                │  • Take page snapshots   │  │
│         │                        └──────────────────────────┘  │
│         │                                    │                  │
│         │           Browser executes         │                  │
│         └────────────────────────────────────┘                  │
│                                                                 │
│  This cycle repeats until the task is complete.                 │
│  The AI never guesses a field — it ALWAYS inspects the          │
│  page before filling anything in.                               │
│                                                                 │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│  STEP 4 — Test code is generated                                │
│                                                                 │
│  Based on what it did, the AI writes two types of file:         │
│                                                                 │
│  pages/login_page.py  ──►  "How to interact with the login"    │
│  tests/test_login.py  ──►  "The test that verifies the login"  │
│                                                                 │
│  These files follow the Page Object Model (POM) pattern:        │
│  "how to use the page" is kept separate from "what to verify". │
│                                                                 │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│  STEP 5 — You review and run the tests                          │
│                                                                 │
│  $ pytest                                                       │
│                                                                 │
│  pytest executes the generated files.                           │
│  If login works ✔  the test passes (green).                     │
│  If something is wrong ✖  the test fails and tells you why.    │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

### What happens under the hood when you run a command?

Concrete example — you type:

```bash
python main.py "Log in and go to the dashboard"
```

What happens behind the scenes:

| # | What occurs | Who does it |
|---|---|---|
| 1 | Program reads `.env` to get URL, credentials, and AI provider | `main.py` + `config.py` |
| 2 | A Chromium browser opens and loads the site | `browser.py` (Playwright) |
| 3 | Your instruction is sent to the AI along with a full description of available tools | `runner.py` + `prompts.py` |
| 4 | AI responds: "I need to see the page fields" → calls `browser_get_inputs` | AI (LLM) |
| 5 | System returns all visible fields: `id="username"`, `id="password"`, button "Sign in" | `tools.py` + `browser.py` |
| 6 | AI responds: "Now I fill the username" → calls `browser_fill` | AI (LLM) |
| 7 | The username field is filled in the real browser | `browser.py` (Playwright) |
| 8 | This repeats for password, button click, and final URL verification | AI ↔ browser loop |
| 9 | AI finishes and writes the code as `<file path="pages/...">...</file>` | AI (LLM) |
| 10 | Code is extracted and saved to the correct `.py` files | `writer.py` |

---

### Why is this better than writing tests by hand?

| Pain point with manual tests | How this project solves it |
|---|---|
| Requires Playwright programming knowledge | Just describe the flow in plain text |
| CSS selectors break when HTML changes | AI uses semantic locators (by label, role, text) — much more stable |
| Hours to create a single test | Minutes to generate a complete test suite |
| Easy to miss a field | AI inspects every visible field on the page automatically |
| Hard to maintain tests as the site evolves | Simply re-run the generator with the same instruction |

---

### Quick glossary

| Term | What it means in practice |
|---|---|
| **Playwright** | The tool that controls the browser automatically (like "autopilot" for Chrome) |
| **pytest** | The program that runs the tests and reports pass or fail |
| **Page Object Model (POM)** | A code organisation pattern: one file describes the page, another describes the test — easier to maintain |
| **LLM / AI** | The language model (GPT-4, Claude, etc.) that understands your instruction and decides what to do |
| **Headless** | The browser runs without a visible window — faster, useful on servers |
| **`.env`** | Configuration file with your passwords and URLs — never committed to Git |
| **Tool call** | The AI "asks" the system to perform an action in the browser (click, fill, snapshot) |

---

### Agent execution loop

```mermaid
flowchart TD
    A([CLI: python main.py]) --> B[Parse args & load .env]
    B --> C[Build TaskConfig]
    C --> D[Select LLM provider\nOpenAI · Claude · Ollama]
    D --> E[Start Chromium browser]
    E --> F[Send system prompt\n+ user prompt to LLM]

    F --> G{LLM response}
    G -->|tool_calls| H[Dispatch browser tool]
    H --> I[Return tool result to LLM]
    I --> F
    G -->|stop / end_turn| J[Extract generated code]
    J --> K[Write files to disk\npages/ and tests/]
    K --> L[Stop browser]
    L --> M([Done])
```

### Browser interaction flow

```mermaid
flowchart LR
    subgraph LLM["LLM (reasoning)"]
        P[Decide next step]
    end

    subgraph Tools["Browser Tools"]
        T1[navigate]
        T2[get_inputs]
        T3[snapshot]
        T4[click / fill]
        T5[press_key]
        T6[get_text / get_html]
        T7[get_frames / switch_frame]
        T8[get_console_messages]
        T9[wait / resize]
    end

    subgraph Browser["Chromium (Playwright)"]
        B1[Real page DOM]
    end

    P -->|calls| Tools
    Tools -->|interacts with| B1
    B1 -->|result| P
```

### File generation flow

```mermaid
flowchart TD
    A[LLM final response text] --> B{Contains\n<file path=...>?}
    B -->|Yes| C[Parse all XML file blocks]
    C --> D[Create directories recursively]
    D --> E[Write pages/*.py]
    D --> F[Write tests/*.py]
    B -->|No| G{Markdown fenced block\nwith # path comment?}
    G -->|Yes| H[Extract path from first comment line]
    H --> D
    G -->|No| I[Warning: no files generated]
```

### LLM provider selection

```mermaid
flowchart TD
    A[--provider or LLM_PROVIDER env] --> B{Provider?}
    B -->|openai| C[OpenAI client\ngpt-4o default]
    B -->|claude| D[Anthropic client\nclaude-sonnet-4-6 default]
    B -->|ollama| E[OpenAI-compat client\nlocalhost:11434\nllama3.2 default]
    C & D & E --> F[Agentic loop\ntool_calls ↔ browser]
```

---

## Repository structure

```
agentic-qa-playwright-mcp/
├── .github/
│   └── workflows/
│       └── lint.yml            # CI: ruff + mypy + pip-audit on push/PR
├── .pre-commit-config.yaml     # Local git commit hooks
├── pyproject.toml              # Root package metadata + ruff/mypy config
├── README.md
├── LICENSE
└── agent_browser/              # Runnable application
    ├── main.py                 # CLI entry point (argparse + asyncio)
    ├── conftest.py             # pytest session-scoped `config` fixture
    ├── pytest.ini              # pytest config (browser: chromium, testpaths: tests/)
    ├── .env.example            # Template — copy to .env and fill in
    ├── pyproject.toml          # Package deps (playwright, openai, anthropic…)
    ├── requirements.txt        # pip-installable dep list
    ├── agent/
    │   ├── browser.py          # Browser class — async Playwright actions
    │   ├── tools.py            # Tool schemas (OpenAI + Anthropic) & dispatcher
    │   ├── prompts.py          # System prompt builder
    │   ├── runner.py           # TaskConfig dataclass + per-provider agent loops
    │   └── writer.py           # Parses LLM output and writes files to disk
    └── utils/
        └── config.py           # Config class — reads BASE_URL, LOGIN_USER, LOGIN_PASSWORD
```

---

## Quick start

```bash
cd agent_browser

# 1. Create and activate virtualenv
python -m venv .venv
.venv\Scripts\activate        # Windows
# source .venv/bin/activate   # Linux / macOS

# 2. Install dependencies
pip install -r requirements.txt
playwright install chromium

# 3. Configure
cp .env.example .env
# Edit .env with your app URL, credentials and API key
```

Minimal `.env`:

```env
BASE_URL=https://your-app/login
LOGIN_USER=admin
LOGIN_PASSWORD=secret

LLM_PROVIDER=openai
OPENAI_API_KEY=sk-...
```

Run the generator:

```bash
python main.py "Login and navigate to the dashboard"
```

The agent opens a browser, inspects the live DOM, executes the flow, and writes `pages/` + `tests/` to disk.

---

## CLI reference

```
python main.py <PROMPT> [OPTIONS]
```

| Argument | Flag | Description |
|---|---|---|
| `PROMPT` | positional | Natural language description of the flow to automate |
| URL | `--url URL` | Base URL (overrides `BASE_URL` from `.env`) |
| User | `--user USER` | Login username (overrides `LOGIN_USER`) |
| Password | `--password PASS` | Login password (overrides `LOGIN_PASSWORD`) |
| Provider | `--provider {openai,claude,ollama}` | LLM provider (overrides `LLM_PROVIDER`) |
| Model | `--model MODEL` | Specific model name (overrides `LLM_MODEL`) |
| Headless | `--headless` | Run browser without visible window |
| Output | `--output DIR` / `-o DIR` | Directory to write generated files (default: `.`) |
| Context | `--context TEXT` / `-c TEXT` | Extra context about the site (routing, framework, quirks) |

### Examples

```bash
# Basic login flow (reads URL and credentials from .env)
python main.py "Login and navigate to dashboard"

# Override credentials inline
python main.py "Login and check audit list" \
  --url https://myapp.com/login \
  --user admin --password secret123

# Use Claude, headless, save to a custom folder
python main.py "Checkout flow" \
  --provider claude \
  --headless \
  --output ./generated

# Extra context to help the agent navigate a SPA
python main.py "Create a new report" \
  --context "After login the app redirects to /dashboard. Sidebar has a 'Reports' entry. Uses React SPA."

# Use a local Ollama model
python main.py "Test login" \
  --provider ollama \
  --model llama3.2
```

---

## LLM providers

| `LLM_PROVIDER` | Default model | Required env var |
|---|---|---|
| `openai` (default) | `gpt-4o` | `OPENAI_API_KEY` |
| `claude` | `claude-sonnet-4-6` | `ANTHROPIC_API_KEY` |
| `ollama` | `llama3.2` | Ollama running locally; `OLLAMA_BASE_URL` (default `http://localhost:11434/v1`) |

Override the model for any provider:

```env
LLM_MODEL=gpt-4o-mini
```

```bash
python main.py "..." --provider claude --model claude-opus-4-8
```

Both OpenAI and Ollama share the same `_run_openai_compat` loop (OpenAI-compatible API). Claude uses `_run_anthropic` with the Anthropic SDK. Both loops share the same `Browser` instance and tool dispatcher.

---

## Browser tools

The LLM has the following tools available. It decides which to call and when, but is instructed to **always call `browser_get_inputs` before filling any field** — selectors are never guessed.

### Navigation

| Tool | Description |
|---|---|
| `browser_navigate` | Go to a URL, waits for `networkidle` |
| `browser_navigate_back` | Go back in history |
| `browser_navigate_forward` | Go forward in history |
| `browser_reload` | Reload the current page |
| `browser_get_url` | Return the current page URL |

### Inspection

| Tool | Description |
|---|---|
| `browser_get_inputs` | List all visible `input`, `textarea`, `select` with real `id`, `name`, `type`, `placeholder`, `label` |
| `browser_snapshot` | Accessibility tree (roles, names, states) — used after every important action |
| `browser_get_text` | All visible text from `<body>` (up to 4 000 chars) |
| `browser_get_html` | Inner HTML of a CSS selector (up to 6 000 chars) |
| `browser_get_console_messages` | Browser console log (errors, warnings, info) |

### Frames

| Tool | Description |
|---|---|
| `browser_get_frames` | List all frames with index, name, URL |
| `browser_switch_frame` | Switch active context to a frame (by index, name, or URL substring) |
| `browser_switch_main_frame` | Return to the main page context |

### Interaction

| Tool | Description |
|---|---|
| `browser_click` | Click an element by selector; waits for `networkidle` |
| `browser_fill` | Fill a form field; waits for element to be visible first |
| `browser_type_text` | Type character by character (useful when `fill` bypasses JS input events) |
| `browser_fill_form` | Fill multiple fields in one call |
| `browser_press_key` | Press a key (`Enter`, `Tab`, `Escape`, etc.) |
| `browser_wait` | Wait N milliseconds (animations, dropdowns) |
| `browser_resize` | Resize the browser viewport |

### Timeouts and content limits

Defined as module-level constants in `browser.py`:

| Constant | Value | Used for |
|---|---|---|
| `_TIMEOUT_NAVIGATE` | 30 000 ms | `page.goto()` |
| `_TIMEOUT_CLICK` | 10 000 ms | `locator.click()`, `wait_for(visible)` |
| `_TIMEOUT_LOAD` | 15 000 ms | `wait_for_load_state("networkidle")` |
| `_SNAPSHOT_LIMIT` | 8 000 chars | Accessibility tree truncation |
| `_TEXT_LIMIT` | 4 000 chars | `get_text()` truncation |
| `_HTML_LIMIT` | 6 000 chars | `get_html()` truncation |
| `_CONSOLE_LIMIT` | 100 entries | Max console messages kept in memory |

---

## Generated output

The agent produces files in the **Page Object Model** pattern:

```
pages/
├── login_page.py
└── dashboard_page.py

tests/
├── test_login.py
└── test_dashboard.py
```

### Page object example

```python
# pages/login_page.py
from playwright.sync_api import Page
from utils.config import Config

class LoginPage:
    def __init__(self, page: Page, config: Config):
        self.page = page
        self.config = config

    def navigate(self):
        self.page.goto(self.config.base_url)

    def login(self):
        self.page.get_by_label("Username").fill(self.config.login_user)
        self.page.get_by_label("Password").fill(self.config.login_password)
        self.page.get_by_role("button", name="Sign in", exact=True).click()
```

### Test example

```python
# tests/test_login.py
from playwright.sync_api import Page
from utils.config import Config
from pages.login_page import LoginPage

def test_login(page: Page, config: Config):
    lp = LoginPage(page, config)
    lp.navigate()
    lp.login()
    page.wait_for_url("**/dashboard")
```

### Locator priority (enforced in the system prompt)

1. `get_by_role(exact=True)`
2. `get_by_label`
3. `get_by_text(exact=True)`
4. `.first` when there is ambiguity

> `pages/` and `tests/` are in `.gitignore`. Review the generated files and commit them once you have approved them.

---

## Running generated tests

```bash
# From agent_browser/
pytest                          # all tests, headless (chromium)
pytest --headed                 # visible browser
pytest tests/test_login.py -v   # specific test, verbose
```

`conftest.py` provides a session-scoped `config` fixture that reads `.env`:

```python
@pytest.fixture(scope="session")
def config() -> Config:
    return Config()
```

Tests receive `page: Page` from `pytest-playwright` and `config: Config` from the above fixture.

---

## Code quality

### Pre-commit hooks

Install once after cloning:

```bash
pip install pre-commit
pre-commit install
```

From then on, every `git commit` automatically runs:

| Hook | What it checks |
|---|---|
| `trailing-whitespace` | Trailing spaces in any file |
| `end-of-file-fixer` | Ensures files end with a newline |
| `check-yaml` / `check-toml` | Syntax of config files |
| `check-merge-conflict` | Leftover merge conflict markers |
| `debug-statements` | `pdb` / `breakpoint()` left in code |
| `ruff` (lint) | PEP 8, unused imports, bugbear, pyupgrade — auto-fixes with `--fix` |
| `ruff-format` | Code formatting (replaces black) |
| `mypy` | Static type checking |
| `pip-audit` | Dependency vulnerability scan (runs only when `requirements.txt` changes) |

Run manually against all files at any time:

```bash
pre-commit run --all-files
```

### GitHub Actions CI

`.github/workflows/lint.yml` runs the same checks on every push to `main`/`dev` and on every pull request:

```
Lint & Validate
├── Ruff lint          (ruff check)
├── Ruff format check  (ruff format --check)
├── Mypy type check
└── pip-audit          (dependency CVE scan)
```

Linting rules are configured in the root `pyproject.toml` under `[tool.ruff]` and `[tool.mypy]`.

---

## Advanced usage

### Extra context (`--context`)

Pass free-form text about your app so the agent does not waste turns guessing navigation:

```bash
python main.py "Create a purchase order" \
  --context "Single-page React app. After login goes to /home. PO form is under Menu > Purchases > New PO. Fields use custom Angular components."
```

### Custom output directory

```bash
python main.py "Onboarding flow" --output ./tests/e2e
```

Generated `pages/` and `tests/` will be written inside `./tests/e2e/`.

### Multi-frame pages

If your app uses iframes, the agent can list all frames and switch context:

```
browser_get_frames  → [{index: 0, name: "main", ...}, {index: 1, name: "embed", ...}]
browser_switch_frame(index=1)
browser_get_inputs  → (inspects inside the iframe)
browser_fill(...)
browser_switch_main_frame
```

### Max tokens

`runner.py` sets `_MAX_TOKENS = 8_096` for all LLM responses. Increase this constant if the agent truncates on complex flows.

---

## Environment variables

| Variable | Required | Description |
|---|---|---|
| `BASE_URL` | Yes (for tests) | Application URL (e.g. `https://myapp.com/login`) |
| `LOGIN_USER` | Yes (for tests) | Login username |
| `LOGIN_PASSWORD` | Yes (for tests) | Login password |
| `LLM_PROVIDER` | No (default: `openai`) | `openai` \| `claude` \| `ollama` |
| `LLM_MODEL` | No | Override default model for the chosen provider |
| `OPENAI_API_KEY` | If using `openai` | OpenAI API key |
| `ANTHROPIC_API_KEY` | If using `claude` | Anthropic API key |
| `OLLAMA_BASE_URL` | If using `ollama` | Default: `http://localhost:11434/v1` |

Copy `.env.example` to `.env` and fill in the values. The `.env` file is git-ignored.

---

## License

[MIT](LICENSE) © 2026 Guilherme Fabio Vieira
