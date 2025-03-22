import time
from playwright.sync_api import Page
from bugster.core.custom_locator import BugsterLocator
from bugster.core.bugster_mouse import BugsterMouse
from bugster.core.bugster_keyboard import BugsterKeyboard
from bugster.utils.dummy_files import create_dummy_file
from bugster.reporting.screenshots import capture_screenshot


class BugsterPage:
    """
    A custom page abstraction that:
    - Wraps Playwright's Page with extra functionality
    - Integrates BugsterLocator for stable element interactions
    - Could manage waits, screenshots, logging steps, etc.
    """

    def __init__(self, page: Page):
        self._page = page
        self.screenshot = False
        self.screenshot_index = 0  # Initialize the screenshot index
        self.mouse = BugsterMouse(self, page.mouse)
        self.keyboard = BugsterKeyboard(self, page.keyboard)

    def goto(self, url: str, **kwargs):
        self._page.goto(url, **kwargs)
        self.wait_for_net()
        if self.screenshot:
            self.screenshot_step(name="goto")

    def set_input_files(
        self, selector: str = "input[type='file']", file_path: str = "random.txt"
    ):
        # Get the parent element before setting files since the input may disappear
        parent_locator = self._page.locator(selector).locator("..")

        file_type = file_path.split(".")[-1]
        file_path = create_dummy_file(file_type)
        self._page.set_input_files(selector, file_path)

        self.wait_for_net()
        if self.screenshot:
            self.screenshot_step(name="set_input_file", locator=parent_locator)

    def wait_for_net(self, delay: float = 3.0):
        time.sleep(delay)

    def locator(self, selector: str, **kwargs) -> BugsterLocator:
        return BugsterLocator(self._page.locator(selector, **kwargs), self)

    def get_by_text(self, text: str, **kwargs) -> BugsterLocator:
        return BugsterLocator(self._page.get_by_text(text, **kwargs), self)

    def get_by_role(self, role: str, **kwargs) -> BugsterLocator:
        return BugsterLocator(self._page.get_by_role(role, **kwargs), self)

    def get_by_placeholder(self, placeholder: str, **kwargs) -> BugsterLocator:
        return BugsterLocator(
            self._page.get_by_placeholder(placeholder, **kwargs), self
        )

    def get_by_label(self, label: str, **kwargs) -> BugsterLocator:
        return BugsterLocator(self._page.get_by_label(label, **kwargs), self)

    def screenshot_step(self, name: str = "step", locator=None):
        """
        Capture a screenshot after a particular step. Integrate with highlighting if needed.
        """
        capture_screenshot(
            self._page, locator=locator, step_name=name, index=self.screenshot_index
        )
        self.screenshot_index += 1  # Increment the index after taking a screenshot

    def __getattr__(self, item):
        # Fallback to underlying page attributes if not defined here
        return getattr(self._page, item)
