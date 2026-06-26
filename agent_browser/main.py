#!/usr/bin/env python3
"""
Gerador de fluxos de teste usando LLM + Playwright Python.

Uso:
    python main.py "Descreva o fluxo de teste que deseja gerar"

Provedor LLM (variável LLM_PROVIDER no .env):
    openai  — OpenAI GPT  (padrão; requer OPENAI_API_KEY)
    claude  — Anthropic   (requer ANTHROPIC_API_KEY)
    ollama  — Ollama local (requer OLLAMA_BASE_URL e LLM_MODEL)
"""

import asyncio
import os
import sys
from pathlib import Path

from dotenv import load_dotenv

from agent import run_agent

BASE_DIR = Path(__file__).parent


def main() -> None:
    load_dotenv(BASE_DIR / ".env")

    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    provider = os.getenv("LLM_PROVIDER", "openai").lower()
    base_url = os.getenv("BASE_URL", "")
    login_user = os.getenv("LOGIN_USER", "")
    login_password = os.getenv("LOGIN_PASSWORD", "")

    full_prompt = (
        f"{sys.argv[1]}\n\n"
        f"URL base: {base_url}\n"
        f"Usuário: {login_user}\n"
        f"Senha: {login_password}"
    )

    asyncio.run(run_agent(full_prompt, provider))


if __name__ == "__main__":
    main()
