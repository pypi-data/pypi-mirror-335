from playwright.async_api import Page, Browser, ElementHandle, Locator, BrowserContext
from typing import Optional, Union, List, Any, Dict, Callable
import asyncio
import re
from enum import Enum
from dataclasses import dataclass
from contextlib import asynccontextmanager


class Keys:
    """Special keyboard keys, similar to Helium's implementation"""
    ENTER = "Enter"
    TAB = "Tab"
    ESCAPE = "Escape"
    BACKSPACE = "Backspace"
    DELETE = "Delete"
    LEFT = "ArrowLeft"
    RIGHT = "ArrowRight"
    UP = "ArrowUp"
    DOWN = "ArrowDown"
    HOME = "Home"
    END = "End"
    PAGE_UP = "PageUp"
    PAGE_DOWN = "PageDown"
    SHIFT = "Shift"
    CONTROL = "Control"
    ALT = "Alt"
    META = "Meta"


class Config:
    """Configuration settings for the wrapper"""
    implicit_wait_secs = 10
    browser_type = 'chromium'
    default_timeout = 10000  # milliseconds
    screenshot_dir = "screenshots"
    ignore_https_errors = False
    viewport_size = {"width": 1280, "height": 720}


@dataclass
class Point:
    """Represents a point on the screen"""
    x: int
    y: int

    def __add__(self, other):
        return Point(self.x + other[0], self.y + other[1])

    def __sub__(self, other):
        return Point(self.x - other[0], self.y - other[1])


class BrowserManager:
    """Manages browser instances and contexts"""

    def __init__(self):
        self.current_page: Optional[Page] = None
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None

    def set_current_page(self, page: Page):
        self.current_page = page


browser_manager = BrowserManager()

async def start_chromium(url: Optional[str] = None, headless: bool = False, **kwargs) -> Page:
    """Start a Chromium browser instance with additional options"""
    from playwright.async_api import async_playwright
    p = await async_playwright().start()

    browser_options = {
        "headless": headless,
        **kwargs
    }

    browser = await p.chromium.launch(**browser_options)
    context = await browser.new_context(
        viewport=Config.viewport_size,
        accept_downloads=True,
        ignore_https_errors=Config.ignore_https_errors
    )

    page = await context.new_page()
    browser_manager.browser = browser
    browser_manager.context = context
    browser_manager.current_page = page

    if url:
        await go_to(url, page)

    return page

async def start_firefox(url: Optional[str] = None, headless: bool = False, **kwargs) -> Page:
    """Start a Firefox browser instance with additional options"""
    from playwright.async_api import async_playwright
    p = await async_playwright().start()

    browser_options = {
        "headless": headless,
        "ignore_https_errors": Config.ignore_https_errors,
        **kwargs
    }

    browser = await p.firefox.launch(**browser_options)
    context = await browser.new_context(
        viewport=Config.viewport_size,
        accept_downloads=True
    )

    page = await context.new_page()
    browser_manager.browser = browser
    browser_manager.context = context
    browser_manager.current_page = page

    if url:
        await go_to(url, page)

    return page


async def go_to(url: str, page: Optional[Page] = None):
    """Navigate to a URL"""
    page = page or browser_manager.current_page
    if not page:
        raise RuntimeError("No browser instance is running")

    if '://' not in url:
        url = 'http://' + url
    await page.goto(url, wait_until='networkidle')


async def write(text: str, page: Optional[Page] = None, into: Optional[Union[str, 'TextField']] = None):
    """Write text into a field"""
    page = page or browser_manager.current_page
    if not page:
        raise RuntimeError("No browser instance is running")

    if isinstance(into, TextField):
        await into.type(text)
    elif isinstance(into, str):
        selectors = [
            f'text={into}',
            f'[placeholder="{into}"]',
            f'label:has-text("{into}") >> input',
            f'textarea:has-text("{into}")',
            f'[aria-label="{into}"]'
        ]
        for selector in selectors:
            try:
                element = await page.wait_for_selector(selector, timeout=1000)
                if element:
                    await element.fill(text)
                    return
            except:
                continue
        raise ValueError(f"Could not find element matching '{into}'")
    else:
        # Write to focused element
        focused = page.locator(':focus')
        await focused.fill(text)


async def press(key: str, page: Optional[Page] = None):
    """Press a keyboard key"""
    page = page or browser_manager.current_page
    if not page:
        raise RuntimeError("No browser instance is running")

    await page.keyboard.press(key)


async def click(element: Union[str, ElementHandle, Locator, 'Point'], page: Optional[Page] = None):
    """Click on an element or at coordinates"""
    page = page or browser_manager.current_page
    if not page:
        raise RuntimeError("No browser instance is running")

    if isinstance(element, Point):
        await page.mouse.click(element.x, element.y)
    elif isinstance(element, str):
        selectors = [
            f'text={element}',
            f'button:has-text("{element}")',
            f'[aria-label="{element}"]',
            f'a:has-text("{element}")'
        ]
        for selector in selectors:
            try:
                await page.click(selector, timeout=1000)
                return
            except:
                continue
        raise ValueError(f"Could not find clickable element matching '{element}'")
    elif isinstance(element, (ElementHandle, Locator)):
        await element.click()


class GUIElement:
    """Base class for GUI elements"""

    def __init__(self, locator: str, page: Optional[Page] = None):
        self.locator = locator
        self.page = page or browser_manager.current_page
        if not self.page:
            raise RuntimeError("No browser instance is running")

    async def exists(self) -> bool:
        """Check if element exists"""
        try:
            element = await self.page.wait_for_selector(self.locator, timeout=1000)
            return bool(element)
        except:
            return False

    async def is_visible(self) -> bool:
        """Check if element is visible"""
        element = self.page.locator(self.locator)
        return await element.is_visible()

    async def wait_until_exists(self, timeout: int = None):
        """Wait until element exists"""
        timeout = timeout or Config.default_timeout
        await self.page.wait_for_selector(self.locator, timeout=timeout)


class Button(GUIElement):
    def __init__(self, text: Optional[str] = None, page: Optional[Page] = None):
        locator = f'button:has-text("{text}")' if text else 'button'
        super().__init__(locator, page)
        self.text = text

    async def is_enabled(self) -> bool:
        """Check if button is enabled"""
        element = self.page.locator(self.locator)
        return await element.is_enabled()


class TextField(GUIElement):
    def __init__(self, label: Optional[str] = None, page: Optional[Page] = None):
        if label:
            locator = f'[placeholder="{label}"], label:has-text("{label}") >> input, textarea:has-text("{label}")'
        else:
            locator = 'input[type="text"], textarea'
        super().__init__(locator, page)
        self.label = label

    async def value(self) -> str:
        """Get text field value"""
        element = self.page.locator(self.locator)
        return await element.input_value()

    async def type(self, text: str):
        """Type text into the field"""
        element = self.page.locator(self.locator)
        await element.fill(text)


class Link(GUIElement):
    def __init__(self, text: Optional[str] = None, page: Optional[Page] = None):
        locator = f'a:has-text("{text}")' if text else 'a'
        super().__init__(locator, page)
        self.text = text

    async def href(self) -> str:
        """Get link href"""
        element = self.page.locator(self.locator)
        return await element.get_attribute('href')


class Alert:
    def __init__(self, page: Optional[Page] = None):
        self.page = page or browser_manager.current_page
        if not self.page:
            raise RuntimeError("No browser instance is running")

    async def accept(self):
        """Accept an alert dialog"""
        self.page.on('dialog', lambda dialog: dialog.accept())

    async def dismiss(self):
        """Dismiss an alert dialog"""
        self.page.on('dialog', lambda dialog: dialog.dismiss())

    async def text(self) -> str:
        """Get alert text"""
        dialog_text = None

        def handle_dialog(dialog):
            nonlocal dialog_text
            dialog_text = dialog.message
            dialog.accept()

        self.page.on('dialog', handle_dialog)
        return dialog_text


async def find_all(element_type: Union[Button, TextField, Link], page: Optional[Page] = None) -> List:
    """Find all elements of a given type"""
    page = page or browser_manager.current_page
    if not page:
        raise RuntimeError("No browser instance is running")

    if isinstance(element_type, Button):
        locator = page.locator('button')
    elif isinstance(element_type, TextField):
        locator = page.locator('input[type="text"], textarea')
    elif isinstance(element_type, Link):
        locator = page.locator('a')
    else:
        raise ValueError(f"Unsupported element type: {type(element_type)}")

    return await locator.all()


async def wait_until(
    condition_fn: Callable[[], bool],
    timeout: int = None,
    page: Optional[Page] = None
):
    """Wait until a condition is met"""
    page = page or browser_manager.current_page
    if not page:
        raise RuntimeError("No browser instance is running")

    timeout = timeout or Config.default_timeout
    try:
        if asyncio.iscoroutinefunction(condition_fn):
            await page.wait_for_function(condition_fn, timeout=timeout)
        else:
            # Convert sync function to async
            async def async_condition():
                return condition_fn()

            await page.wait_for_function(async_condition, timeout=timeout)
    except TimeoutError:
        raise TimeoutError(f"Condition not met within {timeout}ms")


async def attach_file(
    file_path: str,
    to: Optional[Union[str, 'TextField']] = None,
    page: Optional[Page] = None
):
    """Attach a file to a file input"""
    page = page or browser_manager.current_page
    if not page:
        raise RuntimeError("No browser instance is running")

    if isinstance(to, str):
        selector = f'input[type="file"]:near(:text("{to}"))'
    else:
        selector = 'input[type="file"]'

    await page.set_input_files(selector, file_path)


async def kill_browser(page: Optional[Page] = None):
    """Close the browser"""
    page = page or browser_manager.current_page
    if not page:
        raise RuntimeError("No browser instance is running")

    browser = page.context.browser
    await browser.close()
    browser_manager.current_page = None
    browser_manager.browser = None
    browser_manager.context = None


# Additional utility functions

async def scroll_to(element: Union[str, ElementHandle, Locator], page: Optional[Page] = None):
    """Scroll element into view"""
    page = page or browser_manager.current_page
    if not page:
        raise RuntimeError("No browser instance is running")

    if isinstance(element, str):
        element = page.locator(f'text={element}')
    await element.scroll_into_view_if_needed()


async def hover(element: Union[str, ElementHandle, Locator], page: Optional[Page] = None):
    """Hover over an element"""
    page = page or browser_manager.current_page
    if not page:
        raise RuntimeError("No browser instance is running")

    if isinstance(element, str):
        await page.hover(f'text={element}')
    elif isinstance(element, (ElementHandle, Locator)):
        await element.hover()


async def get_text(element: Union[str, ElementHandle, Locator], page: Optional[Page] = None) -> str:
    """Get text content of an element"""
    page = page or browser_manager.current_page
    if not page:
        raise RuntimeError("No browser instance is running")

    if isinstance(element, str):
        element = page.locator(f'text={element}')
    return await element.text_content()


async def take_screenshot(
    path: str,
    full_page: bool = False,
    page: Optional[Page] = None
):
    """Take a screenshot"""
    page = page or browser_manager.current_page
    if not page:
        raise RuntimeError("No browser instance is running")

    await page.screenshot(path=path, full_page=full_page)