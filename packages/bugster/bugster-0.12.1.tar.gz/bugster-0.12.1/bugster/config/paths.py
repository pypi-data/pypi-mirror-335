import os

# Default base directory for all Bugster files
DEFAULT_BASE_DIR = os.path.join(os.getcwd(), ".bugster")


def get_base_dir():
    """
    Get the base directory for Bugster files.
    Priority:
    1. BUGSTER_BASE_DIR environment variable
    2. Default (.bugster in current working directory)
    """
    return os.environ.get("BUGSTER_BASE_DIR", DEFAULT_BASE_DIR)


def get_credentials_path():
    """Get the path to the credentials file"""
    return os.path.join(get_base_dir(), "bugster.json")


def get_traces_dir():
    """Get the directory for trace files"""
    return os.path.join(get_base_dir(), "traces")


def get_screenshots_dir():
    """Get the directory for screenshot files"""
    return os.path.join(get_base_dir(), "screenshots")


def get_dummy_files_dir():
    """Get the directory for dummy files"""
    return os.path.join(get_base_dir(), "dummy_files")


def ensure_dir_exists(directory):
    """Ensure the specified directory exists"""
    if not os.path.exists(directory):
        os.makedirs(directory, exist_ok=True)
    return directory
