import json
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from agent.browser import Browser
from agent.prompts import build_system_prompt
from agent.tools import TOOLS_OPENAI, TOOLS_ANTHROPIC, call_tool
from agent.writer import write_generated_files


@dataclass
class TaskConfig:
    prompt: str
    url: str = ""
    user: str = ""
    password: str = ""
    provider: str = "openai"
    model: str = ""
    headless: bool = False
    output_dir: Path = field(default_factory=Path)
    extra_context: str = ""

    def effective_model(self) -> str:
        if self.model:
            return self.model
        return {"openai": "gpt-4o", "claude": "claude-sonnet-4-6", "ollama": "llama3.2"}.get(
            self.provider, "gpt-4o"
        )

    def full_prompt(self) -> str:
        parts = [self.prompt]
        if self.url:
            parts.append(f"URL base: {self.url}")
        if self.user:
            parts.append(f"Usuário: {self.user}")
        if self.password:
            parts.append(f"Senha: {self.password}")
        if self.extra_context:
            parts.append(f"Contexto adicional: {self.extra_context}")
        return "\n".join(parts)


async def run_agent(config: TaskConfig) -> None:
    model = config.effective_model()
    system_prompt = build_system_prompt(config)

    print(f"Provedor : {config.provider}")
    print(f"Modelo   : {model}")
    print(f"URL      : {config.url or '(não informada)'}")
    print(f"Headless : {config.headless}")
    print(f"Saída    : {config.output_dir.resolve()}")
    print(f"Prompt   : {config.prompt}\n")

    browser = Browser(headless=config.headless)
    await browser.start()
    try:
        if config.provider in ("openai", "ollama"):
            from openai import OpenAI

            if config.provider == "openai":
                client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
            else:
                client = OpenAI(
                    base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434/v1"),
                    api_key="ollama",
                )
            await _run_openai_compat(client, model, config, system_prompt, browser)

        elif config.provider == "claude":
            from anthropic import Anthropic

            client = Anthropic()
            await _run_anthropic(client, model, config, system_prompt, browser)

        else:
            raise ValueError(
                f"Provedor desconhecido: '{config.provider}'. Use: openai, claude ou ollama"
            )
    finally:
        await browser.stop()


async def _run_openai_compat(
    client: Any, model: str, config: TaskConfig, system_prompt: str, browser: Browser
) -> None:
    messages: list[dict] = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": config.full_prompt()},
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
            write_generated_files(text, config.output_dir)
            break

        if choice.finish_reason == "tool_calls":
            messages.append(choice.message)
            for tc in choice.message.tool_calls or []:
                args = json.loads(tc.function.arguments or "{}")
                print(f"  -> {tc.function.name}({json.dumps(args)[:100]})")
                result = await call_tool(browser, tc.function.name, args)
                messages.append({"role": "tool", "tool_call_id": tc.id, "content": result})


async def _run_anthropic(
    client: Any, model: str, config: TaskConfig, system_prompt: str, browser: Browser
) -> None:
    messages: list[dict] = [{"role": "user", "content": config.full_prompt()}]
    while True:
        response = client.messages.create(
            model=model,
            max_tokens=8096,
            system=system_prompt,
            tools=TOOLS_ANTHROPIC,
            messages=messages,
        )
        if response.stop_reason == "end_turn":
            for block in response.content:
                if hasattr(block, "text"):
                    print(block.text)
                    write_generated_files(block.text, config.output_dir)
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
