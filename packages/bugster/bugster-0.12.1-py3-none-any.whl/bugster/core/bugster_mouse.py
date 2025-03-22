import time


class BugsterMouse:
    def __init__(self, page, mouse):
        self._mouse = mouse
        self._page = page
        self._highlight_color = (
            "hsla(259, 100%, 62%, 0.47)"  # Same color as element highlighting
        )
        self._step_delay = 1.0

    def _get_element_at_position(self, x: float, y: float):
        """Attempts to find the element at the given coordinates"""
        return self._page._page.evaluate(
            """
            (args) => {
                const { x, y } = args;
                const element = document.elementFromPoint(x, y);
                return element ? true : false;
            }
        """,
            {"x": x, "y": y},
        )

    def _create_highlight_element(self, x: float, y: float, size: int = 30):
        """Creates a temporary highlight circle at the specified coordinates"""
        # Create a temporary div element for highlighting
        self._page._page.evaluate(
            """
            (args) => {
                const { x, y, size, color } = args;
                const highlight = document.createElement('div');
                highlight.style.position = 'absolute';
                highlight.style.left = (x - size/2) + 'px';
                highlight.style.top = (y - size/2) + 'px';
                highlight.style.width = size + 'px';
                highlight.style.height = size + 'px';
                highlight.style.backgroundColor = color;
                highlight.style.borderRadius = '50%';
                highlight.style.pointerEvents = 'none';
                highlight.style.zIndex = '10000';
                highlight.id = 'mouse-highlight';
                document.body.appendChild(highlight);
            }
        """,
            {"x": x, "y": y, "size": size, "color": self._highlight_color},
        )

    def _remove_highlight(self):
        """Removes the temporary highlight element"""
        self._page._page.evaluate(
            """
            () => {
                const highlight = document.getElementById('mouse-highlight');
                if (highlight) highlight.remove();
            }
        """
        )

    def move(self, x: float, y: float, **kwargs):
        self._create_highlight_element(x, y)
        self._mouse.move(x, y, **kwargs)
        if self._page.screenshot:
            self._page.screenshot_step(name="after_mouse_move")
        self._remove_highlight()

    def click(self, x: float, y: float, **kwargs):
        time.sleep(self._step_delay)

        has_element = self._get_element_at_position(x, y)
        if self._page.screenshot:
            self._create_highlight_element(x, y)
            self._page.screenshot_step(name="after_mouse_click")
            self._remove_highlight()
        self._mouse.click(x, y, **kwargs)

    def __getattr__(self, name):
        return getattr(self._mouse, name)
