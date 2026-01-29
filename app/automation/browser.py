import asyncio
from playwright.async_api import async_playwright, Browser, Page
from typing import Optional

class BrowserManager:
    def __init__(self):
        self.playwright = None
        self.browser: Optional[Browser] = None
        self.page: Optional[Page] = None
        self.lock = asyncio.Lock()

    async def start(self):
        async with self.lock:
            if not self.browser:
                self.playwright = await async_playwright().start()
                # Headless=False is MANDATORY for Phase 8 (Visible)
                self.browser = await self.playwright.chromium.launch(headless=False)
                context = await self.browser.new_context()
                self.page = await context.new_page()

    async def stop(self):
        async with self.lock:
            if self.browser:
                await self.browser.close()
                self.browser = None
            if self.playwright:
                await self.playwright.stop()
                self.playwright = None
            self.page = None

    async def goto(self, url: str):
        if not self.page:
            await self.start()
        
        if not url.startswith("http"):
            url = "https://" + url
            
        await self.page.goto(url)
        title = await self.page.title()
        return f"Navigated to: {title}"

    async def click(self, selector: str):
        if not self.page:
            return "Error: Browser not open."
        try:
            # wait for element
            await self.page.wait_for_selector(selector, timeout=5000)
            await self.page.click(selector)
            return f"Clicked '{selector}'"
        except Exception as e:
            return f"Error clicking '{selector}': {str(e)}"

    async def type_text(self, selector: str, text: str):
        if not self.page:
            return "Error: Browser not open."
        try:
            await self.page.wait_for_selector(selector, timeout=5000)
            await self.page.fill(selector, text)
            return f"Typed '{text}' into '{selector}'"
        except Exception as e:
            return f"Error typing: {str(e)}"
            
    async def get_state(self):
        if not self.page:
            return "Browser Closed"
        return await self.page.title()

browser_manager = BrowserManager()

def get_browser_manager():
    return browser_manager
