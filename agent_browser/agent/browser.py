import asyncio
import json

from playwright.async_api import async_playwright, Page


class Browser:
    def __init__(self) -> None:
        self._pw = None
        self._browser = None
        self._page: Page | None = None

    async def start(self) -> None:
        self._pw = await async_playwright().start()
        self._browser = await self._pw.chromium.launch(headless=False)
        self._page = await self._browser.new_page()

    async def stop(self) -> None:
        if self._browser:
            await self._browser.close()
        if self._pw:
            await self._pw.stop()

    async def navigate(self, url: str) -> str:
        await self._page.goto(url, wait_until="networkidle", timeout=30_000)
        return f"Página: {await self._page.title()} | URL: {self._page.url}"

    async def snapshot(self) -> str:
        tree = await self._page.accessibility.snapshot()
        return json.dumps(tree, indent=2, ensure_ascii=False)[:8000]

    async def get_inputs(self) -> str:
        inputs = await self._page.evaluate("""
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

    async def click(self, selector: str) -> str:
        await self._page.locator(selector).first.click(timeout=10_000)
        await self._page.wait_for_load_state("networkidle", timeout=15_000)
        return f"Clicou: {selector} | Página: {await self._page.title()}"

    async def fill(self, selector: str, value: str) -> str:
        loc = self._page.locator(selector).first
        await loc.wait_for(state="visible", timeout=10_000)
        await loc.fill(value)
        return f"Preencheu '{selector}'"

    async def press_key(self, key: str) -> str:
        await self._page.keyboard.press(key)
        await self._page.wait_for_load_state("networkidle", timeout=15_000)
        return f"Pressionou: {key} | Página: {await self._page.title()}"

    async def get_text(self) -> str:
        return (await self._page.inner_text("body"))[:4000]

    async def get_html(self, selector: str = "body") -> str:
        return (await self._page.inner_html(selector))[:6000]

    async def wait(self, milliseconds: int = 1000) -> str:
        await asyncio.sleep(milliseconds / 1000)
        return f"Aguardou {milliseconds}ms"
