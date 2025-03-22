from datetime import datetime, timezone
from bugster.config.paths import get_traces_dir, ensure_dir_exists
import os


def start_trace(context):
    """
    Start recording a Playwright trace.
    Call this before test steps begin.
    """
    context.tracing.start(title="test_trace", snapshots=True, screenshots=True)


def stop_and_save_trace(context, test_name="test"):
    """
    Stop tracing and save the trace file.
    """
    output_dir = ensure_dir_exists(get_traces_dir())
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S%f")
    filename = f"{test_name}_{timestamp}.zip"
    trace_path = os.path.join(output_dir, filename)
    context.tracing.stop(path=trace_path)
    return trace_path
