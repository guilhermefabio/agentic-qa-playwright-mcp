import json
import os
from typing import Any

from agent.browser import Browser
from agent.prompts import SYSTEM_PROMPT
from agent.tools import TOOLS_OPENAI, TOOLS_ANTHROPIC, call_tool
from agent.writer import write_generated_files


def _default_model(provider: str) -> str:
    if m := os.getenv("LLM_MODEL"):
        return m
    return {"openai": "gpt-4o", "claude": "claude-sonnet-4-6", "ollama": "llama3.2"}[provider]


async def run_agent(prompt: str, provider: str) -> None:
    model = _default_model(provider)
    print(f"Provedor : {provider}")
    print(f"Modelo   : {model}")
    print(f"Prompt   : {prompt}\n")

    browser = Browser()
    await browser.start()
    try:
        if provider in ("openai", "ollama"):
            from openai import OpenAI
            if provider == "openai":
                client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
            else:
                client = OpenAI(
                    base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434/v1"),
                    api_key="ollama",
                )
            await _run_openai_compat(client, model, prompt, browser)

        elif provider == "claude":
            from anthropic import Anthropic
            client = Anthropic()
            await _run_anthropic(client, model, prompt, browser)

        else:
            raise ValueError(f"Provedor desconhecido: '{provider}'. Use: openai, claude ou ollama")
    finally:
        await browser.stop()


async def _run_openai_compat(client: Any, model: str, prompt: str, browser: Browser) -> None:
    messages: list[dict] = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": prompt},
    ]
    while True:
        response = client.chat.completions.create(
            model=model,
            max_tokens=8096,
            tools=TOOLS_OPENAI,
            messages=messages,
        )
        choice = response.choices[0]

        if choice.finish_reason == "stop":
            text = choice.message.content or ""
            print(text)
            write_generated_files(text)
            break

        if choice.finish_reason == "tool_calls":
            messages.append(choice.message)
            for tc in choice.message.tool_calls or []:
                args = json.loads(tc.function.arguments or "{}")
                print(f"  -> {tc.function.name}({json.dumps(args)[:100]})")
                result = await call_tool(browser, tc.function.name, args)
                messages.append({"role": "tool", "tool_call_id": tc.id, "content": result})


async def _run_anthropic(client: Any, model: str, prompt: str, browser: Browser) -> None:
    messages: list[dict] = [{"role": "user", "content": prompt}]
    while True:
        response = client.messages.create(
            model=model,
            max_tokens=8096,
            system=SYSTEM_PROMPT,
            tools=TOOLS_ANTHROPIC,
            messages=messages,
        )
        if response.stop_reason == "end_turn":
            for block in response.content:
                if hasattr(block, "text"):
                    print(block.text)
                    write_generated_files(block.text)
            break

        if response.stop_reason == "tool_use":
            tool_results = []
            for block in response.content:
                if block.type == "tool_use":
                    print(f"  -> {block.name}({json.dumps(block.input)[:100]})")
                    result = await call_tool(browser, block.name, block.input)
                    tool_results.append(
                        {"type": "tool_result", "tool_use_id": block.id, "content": result}
                    )
            messages.append({"role": "assistant", "content": response.content})
            messages.append({"role": "user", "content": tool_results})
