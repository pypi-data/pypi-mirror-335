# sync_wrapper.py
import asyncio
from typing import Optional, Union, List, Any, Callable
from playwright.async_api import Page, ElementHandle, Locator
import weblair as  hydrogen_asyn_func  # Import all async functions and classes

class WebController:
    def __init__(self):
        self.page = None
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)

    def _run(self, coro):
        return self.loop.run_until_complete(coro)

    def start_chrome(self, url: Optional[str] = None, headless: bool = False, **kwargs) -> Page:
        return self._run(hydrogen_asyn_func.start_chromium(url, headless, **kwargs))

    def start_firefox(self, url: Optional[str] = None, headless: bool = False, **kwargs) -> Page:
        return self._run(start_firefox(url, headless, **kwargs))

    def go_to(self, url: str):
        return self._run(go_to(url))

    def write(self, text: str, into: Optional[Union[str, hydrogen_asyn_func.TextField]] = None):
        return self._run(write(text, into=into))

    def press(self, key: str):
        return self._run(press(key))

    def click(self, element: Union[str, ElementHandle, Locator, hydrogen_asyn_func.Point]):
        return self._run(click(element))

    def find_all(self, element_type: Union[hydrogen_asyn_func.Button, hydrogen_asyn_func.TextField, hydrogen_asyn_func.Link]) -> List:
        return self._run(find_all(element_type))

    def wait_until(self, condition_fn: Callable[[], bool], timeout: int = None):
        return self._run(wait_until(condition_fn, timeout))

    def attach_file(self, file_path: str, to: Optional[Union[str, hydrogen_asyn_func.TextField]] = None):
        return self._run(attach_file(file_path, to))

    def scroll_to(self, element: Union[str, ElementHandle, Locator]):
        return self._run(scroll_to(element))

    def hover(self, element: Union[str, ElementHandle, Locator]):
        return self._run(hover(element))

    def get_text(self, element: Union[str, ElementHandle, Locator]) -> str:
        return self._run(get_text(element))

    def take_screenshot(self, path: str, full_page: bool = False):
        return self._run(take_screenshot(path, full_page))

    def kill_browser(self):
        self._run(kill_browser())
        self.loop.close()

# Synchronous wrapper classes for GUI elements
class SyncGUIElement:
    def __init__(self, async_element):
        self.async_element = async_element
        self.loop = asyncio.get_event_loop()

    def exists(self) -> bool:
        return self.loop.run_until_complete(self.async_element.exists())

    def is_visible(self) -> bool:
        return self.loop.run_until_complete(self.async_element.is_visible())

    def wait_until_exists(self, timeout: int = None):
        return self.loop.run_until_complete(self.async_element.wait_until_exists(timeout))

class SyncButton(SyncGUIElement):
    def __init__(self, text: Optional[str] = None, page: Optional[Page] = None):
        super().__init__(Button(text, page))

    def is_enabled(self) -> bool:
        return self.loop.run_until_complete(self.async_element.is_enabled())

class SyncTextField(SyncGUIElement):
    def __init__(self, label: Optional[str] = None, page: Optional[Page] = None):
        super().__init__(TextField(label, page))

    def value(self) -> str:
        return self.loop.run_until_complete(self.async_element.value())

    def type(self, text: str):
        return self.loop.run_until_complete(self.async_element.type(text))

class SyncLink(SyncGUIElement):
    def __init__(self, text: Optional[str] = None, page: Optional[Page] = None):
        super().__init__(Link(text, page))

    def href(self) -> str:
        return self.loop.run_until_complete(self.async_element.href())

class SyncAlert:
    def __init__(self, page: Optional[Page] = None):
        self.async_alert = Alert(page)
        self.loop = asyncio.get_event_loop()

    def accept(self):
        return self.loop.run_until_complete(self.async_alert.accept())

    def dismiss(self):
        return self.loop.run_until_complete(self.async_alert.dismiss())

    def text(self) -> str:
        return self.loop.run_until_complete(self.async_alert.text())

# Create global controller instance
_controller = WebController()

# Export synchronous functions
start_chrome = _controller.start_chrome
start_firefox = _controller.start_firefox
go_to = _controller.go_to
write = _controller.write
press = _controller.press
click = _controller.click
find_all = _controller.find_all
wait_until = _controller.wait_until
attach_file = _controller.attach_file
scroll_to = _controller.scroll_to
hover = _controller.hover
get_text = _controller.get_text
take_screenshot = _controller.take_screenshot
kill_browser = _controller.kill_browser

# Export constants
from weblair import Keys, Config, Point

# Export synchronous GUI element classes
Button = SyncButton
TextField = SyncTextField
Link = SyncLink
Alert = SyncAlert