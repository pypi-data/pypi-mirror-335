class BugsterKeyboard:
    def __init__(self, page, keyboard):
        self._keyboard = keyboard
        self._page = page

    def type(self, text: str, **kwargs):
        self._keyboard.type(text, **kwargs)
        if self._page.screenshot:
            # Get the active element (focused input/textarea)
            active_element = self._page._page.locator(":focus")
            self._page.screenshot_step(
                name="after_keyboard_type", locator=active_element
            )

    def press(self, key: str, **kwargs):
        self._keyboard.press(key, **kwargs)
        if self._page.screenshot:
            # Get the active element (focused input/textarea)
            active_element = self._page._page.locator(":focus")
            self._page.screenshot_step(
                name="after_keyboard_press", locator=active_element
            )

    def __getattr__(self, name):
        return getattr(self._keyboard, name)
