"""Thin async wrapper around Playwright exposing the tools the agent needs."""

import asyncio
import json

from playwright.async_api import Browser as PlaywrightBrowser
from playwright.async_api import Frame, Page, Playwright, async_playwright

# Timeouts (ms)
_TIMEOUT_NAVIGATE = 30_000
_TIMEOUT_CLICK = 10_000
_TIMEOUT_LOAD = 15_000

# Content limits (chars) — keeps LLM context manageable
_SNAPSHOT_LIMIT = 8_000
_TEXT_LIMIT = 4_000
_HTML_LIMIT = 6_000
_CONSOLE_LIMIT = 100  # max console messages to keep


class Browser:
    """Chromium browser controlled by Playwright for the agent to inspect and interact with."""

    def __init__(self, headless: bool = False) -> None:
        self._headless = headless
        self._pw: Playwright | None = None
        self._browser: PlaywrightBrowser | None = None
        self._page: Page | None = None
        self._active_frame: Frame | None = None  # None = main page context
        self._console_messages: list[dict] = []

    @property
    def _p(self) -> Page:
        """Active page — raises if browser not started yet."""
        assert self._page is not None, "Browser not started — call start() first"
        return self._page

    @property
    def _ctx(self) -> Page | Frame:
        """Active frame if one is selected, otherwise the main page."""
        return self._active_frame if self._active_frame is not None else self._p

    async def start(self) -> None:
        self._pw = await async_playwright().start()
        self._browser = await self._pw.chromium.launch(headless=self._headless)
        self._page = await self._browser.new_page()
        self._page.on("console", self._on_console)

    def _on_console(self, msg) -> None:
        self._console_messages.append({"type": msg.type, "text": msg.text})
        if len(self._console_messages) > _CONSOLE_LIMIT:
            self._console_messages.pop(0)

    async def stop(self) -> None:
        if self._browser:
            await self._browser.close()
        if self._pw:
            await self._pw.stop()

    # ── Navigation ──────────────────────────────────────────────────────────

    async def navigate(self, url: str) -> str:
        await self._p.goto(url, wait_until="networkidle", timeout=_TIMEOUT_NAVIGATE)
        return f"Página: {await self._p.title()} | URL: {self._p.url}"

    async def navigate_back(self) -> str:
        await self._p.go_back(wait_until="networkidle", timeout=_TIMEOUT_NAVIGATE)
        return f"Voltou para: {await self._p.title()} | URL: {self._p.url}"

    async def navigate_forward(self) -> str:
        await self._p.go_forward(wait_until="networkidle", timeout=_TIMEOUT_NAVIGATE)
        return f"Avançou para: {await self._p.title()} | URL: {self._p.url}"

    async def reload(self) -> str:
        await self._p.reload(wait_until="networkidle", timeout=_TIMEOUT_NAVIGATE)
        return f"Recarregou: {await self._p.title()} | URL: {self._p.url}"

    async def get_url(self) -> str:
        return self._p.url

    # ── Snapshot / inspection ────────────────────────────────────────────────

    async def snapshot(self) -> str:
        tree = await self._p.accessibility.snapshot()  # type: ignore[attr-defined]
        return json.dumps(tree, indent=2, ensure_ascii=False)[:_SNAPSHOT_LIMIT]

    async def get_inputs(self) -> str:
        inputs = await self._ctx.evaluate("""
            () => Array.from(document.querySelectorAll('input, textarea, select')).map(el => ({
                tag: el.tagName.toLowerCase(),
                type: el.type || '',
                id: el.id || '',
                name: el.name || '',
                placeholder: el.placeholder || '',
                label: (() => {
                    if (el.id) {
                        const lbl = document.querySelector('label[for="' + el.id + '"]');
                        return lbl ? lbl.innerText.trim() : '';
                    }
                    return '';
                })(),
                visible: el.offsetParent !== null && el.type !== 'hidden',
            })).filter(el => el.visible)
        """)
        return json.dumps(inputs, indent=2, ensure_ascii=False)

    async def get_text(self) -> str:
        return (await self._ctx.inner_text("body"))[:_TEXT_LIMIT]

    async def get_html(self, selector: str = "body") -> str:
        return (await self._ctx.inner_html(selector))[:_HTML_LIMIT]

    async def get_console_messages(self) -> str:
        return json.dumps(self._console_messages, ensure_ascii=False)

    # ── Frames ───────────────────────────────────────────────────────────────

    async def get_frames(self) -> str:
        frames = []
        for i, frame in enumerate(self._p.frames):
            frames.append(
                {
                    "index": i,
                    "name": frame.name,
                    "url": frame.url,
                    "is_active": frame is self._active_frame,
                }
            )
        return json.dumps(frames, indent=2, ensure_ascii=False)

    async def switch_frame(
        self, index: int | None = None, name: str | None = None, url_contains: str | None = None
    ) -> str:
        frames = self._p.frames
        if index is not None:
            if index < 0 or index >= len(frames):
                return f"Frame {index} não encontrado. Total de frames: {len(frames)}"
            self._active_frame = frames[index]
        elif name is not None:
            match = next((f for f in frames if f.name == name), None)
            if match is None:
                return f"Frame com name='{name}' não encontrado"
            self._active_frame = match
        elif url_contains is not None:
            match = next((f for f in frames if url_contains in f.url), None)
            if match is None:
                return f"Frame com url contendo '{url_contains}' não encontrado"
            self._active_frame = match
        else:
            return "Informe index, name ou url_contains"
        return f"Contexto ativo: frame '{self._active_frame.name}' | URL: {self._active_frame.url}"

    async def switch_main_frame(self) -> str:
        self._active_frame = None
        return f"Voltou ao frame principal | Página: {await self._p.title()}"

    # ── Interaction ──────────────────────────────────────────────────────────

    async def click(self, selector: str) -> str:
        await self._ctx.locator(selector).first.click(timeout=_TIMEOUT_CLICK)
        await self._p.wait_for_load_state("networkidle", timeout=_TIMEOUT_LOAD)
        return f"Clicou: {selector} | Página: {await self._p.title()}"

    async def fill(self, selector: str, value: str) -> str:
        loc = self._ctx.locator(selector).first
        await loc.wait_for(state="visible", timeout=_TIMEOUT_CLICK)
        await loc.fill(value)
        return f"Preencheu '{selector}'"

    async def type_text(self, selector: str, text: str, delay: int = 0) -> str:
        """Type text character by character (useful when fill() bypasses input events)."""
        loc = self._ctx.locator(selector).first
        await loc.wait_for(state="visible", timeout=_TIMEOUT_CLICK)
        await loc.type(text, delay=delay)
        return f"Digitou em '{selector}'"

    async def fill_form(self, fields: list[dict]) -> str:
        """Fill multiple form fields in one call."""
        results = []
        for field in fields:
            selector = field["selector"]
            value = field.get("value", "")
            action = field.get("action", "fill")
            loc = self._ctx.locator(selector).first
            await loc.wait_for(state="visible", timeout=_TIMEOUT_CLICK)
            if action == "check":
                await loc.check(timeout=_TIMEOUT_CLICK)
                results.append(f"check '{selector}'")
            elif action == "uncheck":
                await loc.uncheck(timeout=_TIMEOUT_CLICK)
                results.append(f"uncheck '{selector}'")
            elif action == "select":
                await loc.select_option(value, timeout=_TIMEOUT_CLICK)
                results.append(f"select '{value}' em '{selector}'")
            else:
                await loc.fill(value)
                results.append(f"fill '{selector}' = '{value}'")
        return "Formulário preenchido: " + "; ".join(results)

    async def check(self, selector: str) -> str:
        await self._ctx.locator(selector).first.check(timeout=_TIMEOUT_CLICK)
        return f"Marcou (check): {selector}"

    async def uncheck(self, selector: str) -> str:
        await self._ctx.locator(selector).first.uncheck(timeout=_TIMEOUT_CLICK)
        return f"Desmarcou (uncheck): {selector}"

    async def press_key(self, key: str) -> str:
        await self._p.keyboard.press(key)
        await self._p.wait_for_load_state("networkidle", timeout=_TIMEOUT_LOAD)
        return f"Pressionou: {key} | Página: {await self._p.title()}"

    async def hover(self, selector: str) -> str:
        await self._ctx.locator(selector).first.hover(timeout=_TIMEOUT_CLICK)
        return f"Hover em: {selector}"

    async def select_option(self, selector: str, value: str) -> str:
        await self._ctx.locator(selector).first.select_option(value, timeout=_TIMEOUT_CLICK)
        return f"Selecionou '{value}' em: {selector}"

    async def drag(self, source_selector: str, target_selector: str) -> str:
        await self._p.drag_and_drop(source_selector, target_selector, timeout=_TIMEOUT_CLICK)
        return f"Arrastou de '{source_selector}' para '{target_selector}'"

    async def file_upload(self, selector: str, paths: list[str]) -> str:
        await self._ctx.locator(selector).first.set_input_files(paths, timeout=_TIMEOUT_CLICK)
        return f"Arquivos enviados em: {selector}: {paths}"

    async def scroll(self, direction: str = "down", amount: int = 300, selector: str = "") -> str:
        if selector:
            await self._ctx.locator(selector).first.scroll_into_view_if_needed()
            return f"Rolou até elemento: {selector}"
        delta_x = amount if direction == "right" else (-amount if direction == "left" else 0)
        delta_y = amount if direction == "down" else (-amount if direction == "up" else 0)
        await self._p.mouse.wheel(delta_x, delta_y)
        return f"Rolou {direction} {amount}px"

    # ── JavaScript ───────────────────────────────────────────────────────────

    async def evaluate(self, script: str) -> str:
        result = await self._ctx.evaluate(script)
        return json.dumps(result, ensure_ascii=False) if result is not None else "null"

    # ── Dialogs ──────────────────────────────────────────────────────────────

    async def handle_dialog(self, accept: bool = True, prompt_text: str = "") -> str:
        """Register a one-shot handler for the next browser dialog (alert/confirm/prompt)."""

        async def _handler(dialog):
            if accept:
                await dialog.accept(prompt_text or "")
            else:
                await dialog.dismiss()

        self._p.once("dialog", _handler)
        action = "aceitar" if accept else "recusar"
        return f"Handler de diálogo configurado para {action}"

    # ── Screenshot ───────────────────────────────────────────────────────────

    async def take_screenshot(self, path: str = "screenshot.png", full_page: bool = False) -> str:
        await self._p.screenshot(path=path, full_page=full_page)
        return f"Screenshot salvo em: {path}"

    # ── Misc ─────────────────────────────────────────────────────────────────

    async def wait(self, milliseconds: int = 1000) -> str:
        await asyncio.sleep(milliseconds / 1000)
        return f"Aguardou {milliseconds}ms"

    async def resize(self, width: int, height: int) -> str:
        await self._p.set_viewport_size({"width": width, "height": height})
        return f"Viewport redimensionado para {width}x{height}"
