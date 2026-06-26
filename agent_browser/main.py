#!/usr/bin/env python3
"""
Gerador de fluxos de teste usando LLM + Playwright Python.

Uso:
    python main.py "Descreva o fluxo" [--url URL] [--user USER] [--password PASS]
                   [--provider PROV] [--model MODEL] [--headless] [--output DIR]
                   [--context TEXTO]

Exemplos:
    python main.py "Login e módulo Auditoria" --url https://app.com --user admin --password 123
    python main.py "Testar checkout" --url https://loja.com --headless --provider claude
    python main.py "Criar relatório" --url https://erp.com --user ops --password x \\
        --context "Após login redireciona para /dashboard. Menu lateral tem 'Relatórios'."

Provedor LLM (--provider ou LLM_PROVIDER no .env):
    openai  — OpenAI GPT  (padrão; requer OPENAI_API_KEY)
    claude  — Anthropic   (requer ANTHROPIC_API_KEY)
    ollama  — Ollama local (requer OLLAMA_BASE_URL e LLM_MODEL)
"""

import argparse
import asyncio
import os
from pathlib import Path

from dotenv import load_dotenv

from agent.runner import TaskConfig, run_agent

BASE_DIR = Path(__file__).parent


def main() -> None:
    load_dotenv(BASE_DIR / ".env")

    parser = argparse.ArgumentParser(
        description="Gerador de testes Playwright via LLM",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("prompt", help="Descrição do fluxo de teste a gerar")
    parser.add_argument("--url", help="URL base do sistema (substitui BASE_URL do .env)")
    parser.add_argument("--user", help="Usuário de login (substitui LOGIN_USER do .env)")
    parser.add_argument("--password", help="Senha de login (substitui LOGIN_PASSWORD do .env)")
    parser.add_argument(
        "--provider",
        choices=["openai", "claude", "ollama"],
        help="Provedor LLM (substitui LLM_PROVIDER do .env)",
    )
    parser.add_argument("--model", help="Modelo LLM (substitui LLM_MODEL do .env)")
    parser.add_argument(
        "--headless",
        action="store_true",
        help="Executar o browser sem janela visível",
    )
    parser.add_argument(
        "--output", "-o",
        default=".",
        help="Diretório de saída dos arquivos gerados (padrão: diretório atual)",
    )
    parser.add_argument(
        "--context", "-c",
        default="",
        help="Contexto adicional sobre o site (ex: 'usa React, login em /auth, sem senha pré-definida')",
    )

    args = parser.parse_args()

    config = TaskConfig(
        prompt=args.prompt,
        url=args.url or os.getenv("BASE_URL", ""),
        user=args.user or os.getenv("LOGIN_USER", ""),
        password=args.password or os.getenv("LOGIN_PASSWORD", ""),
        provider=(args.provider or os.getenv("LLM_PROVIDER", "openai")).lower(),
        model=args.model or os.getenv("LLM_MODEL", ""),
        headless=args.headless,
        output_dir=Path(args.output),
        extra_context=args.context,
    )

    asyncio.run(run_agent(config))


if __name__ == "__main__":
    main()
