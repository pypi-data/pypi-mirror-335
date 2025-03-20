import os
from datetime import datetime, timezone
from bugster.config.paths import get_screenshots_dir, ensure_dir_exists


def capture_screenshot(
    page, locator=None, step_name="step", index=0
):
    """
    Captures a screenshot of the current page state.
    step_name: A descriptive name of the step being captured.
    index: An index to prepend to the filename for ordering.
    """
    output_dir = ensure_dir_exists(get_screenshots_dir())

    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S%f")
    filename = f"{index}_{step_name}_{timestamp}.png"
    path = os.path.join(output_dir, filename)
    mask = [locator] if locator else None
    mask_color = "hsla(259, 100%, 62%, 0.47)" if locator else None

    page.screenshot(path=path, mask=mask, mask_color=mask_color)
    return path
