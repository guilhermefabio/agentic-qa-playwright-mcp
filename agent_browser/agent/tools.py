import json
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from agent.browser import Browser

TOOLS_OPENAI = [
    {
        "type": "function",
        "function": {
            "name": "browser_navigate",
            "description": "Navega para uma URL e aguarda o carregamento completo",
            "parameters": {
                "type": "object",
                "properties": {"url": {"type": "string"}},
                "required": ["url"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "browser_get_inputs",
            "description": (
                "Retorna todos os campos de input visíveis com seus atributos reais "
                "(id, name, type, placeholder, label). "
                "Use SEMPRE antes de preencher qualquer campo para descobrir o seletor correto."
            ),
            "parameters": {"type": "object", "properties": {}},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "browser_snapshot",
            "description": (
                "Retorna a árvore de acessibilidade da página (elementos, roles, nomes). "
                "Use após cada ação para entender o estado da tela."
            ),
            "parameters": {"type": "object", "properties": {}},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "browser_click",
            "description": "Clica em um elemento. Ex: 'text=Login', '#btn-submit', 'input[type=submit]'",
            "parameters": {
                "type": "object",
                "properties": {"selector": {"type": "string"}},
                "required": ["selector"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "browser_fill",
            "description": "Preenche um campo. Use o seletor exato retornado por browser_get_inputs.",
            "parameters": {
                "type": "object",
                "properties": {
                    "selector": {"type": "string"},
                    "value": {"type": "string"},
                },
                "required": ["selector", "value"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "browser_press_key",
            "description": "Pressiona uma tecla. Ex: 'Enter', 'Tab', 'Escape'",
            "parameters": {
                "type": "object",
                "properties": {"key": {"type": "string"}},
                "required": ["key"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "browser_get_text",
            "description": "Retorna o texto visível da página (útil para checar mensagens ou confirmar navegação)",
            "parameters": {"type": "object", "properties": {}},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "browser_get_html",
            "description": "Retorna o HTML interno de um seletor CSS para inspecionar a estrutura dos elementos",
            "parameters": {
                "type": "object",
                "properties": {
                    "selector": {"type": "string", "description": "Seletor CSS (padrão: 'body')"}
                },
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "browser_wait",
            "description": "Aguarda N milissegundos (use quando animações ou dropdowns precisam terminar)",
            "parameters": {
                "type": "object",
                "properties": {"milliseconds": {"type": "integer", "default": 1000}},
            },
        },
    },
]

TOOLS_ANTHROPIC = [
    {
        "name": t["function"]["name"],
        "description": t["function"]["description"],
        "input_schema": t["function"].get("parameters", {"type": "object", "properties": {}}),
    }
    for t in TOOLS_OPENAI
]


async def call_tool(browser: "Browser", name: str, args: dict) -> str:
    try:
        dispatch = {
            "browser_navigate":   lambda: browser.navigate(args["url"]),
            "browser_get_inputs": lambda: browser.get_inputs(),
            "browser_snapshot":   lambda: browser.snapshot(),
            "browser_click":      lambda: browser.click(args["selector"]),
            "browser_fill":       lambda: browser.fill(args["selector"], args["value"]),
            "browser_press_key":  lambda: browser.press_key(args["key"]),
            "browser_get_text":   lambda: browser.get_text(),
            "browser_get_html":   lambda: browser.get_html(args.get("selector", "body")),
            "browser_wait":       lambda: browser.wait(args.get("milliseconds", 1000)),
        }
        if name in dispatch:
            return await dispatch[name]()
        return f"Ferramenta desconhecida: {name}"
    except Exception as exc:
        return f"Erro em {name}: {exc}"
