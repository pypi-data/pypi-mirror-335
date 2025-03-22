# conftest.py
import os
import json
import re
import pytest
from urllib.parse import urlparse, urlunparse

from playwright.sync_api import sync_playwright

from bugster.core.base_page import BugsterPage
from bugster.auth.streategies import UserInputLoginStrategy
from bugster.config.credentials import load_credentials
from bugster.core.test_metadata import TestMetadata
from bugster.core.dependency_manager import DependencyManager
from bugster.reporting.screenshots import capture_screenshot
from bugster.reporting.trace_viewer import start_trace, stop_and_save_trace
from bugster.config.paths import get_base_dir


#############################
# Session-Level Fixtures
#############################


@pytest.fixture
def cred_key_param(request):
    try:
        return request.param
    except AttributeError:
        return None


@pytest.fixture(scope="session")
def test_metadata(request):
    """
    Loads and provides test metadata for the entire session.
    This could read a config path from ENV, or fallback to defaults.
    """
    base_path = get_base_dir()
    metadata = TestMetadata(base_path=base_path)
    # Set the environment from command line option
    metadata.current_env = request.config.getoption("--env")
    return metadata


@pytest.fixture(scope="session")
def credentials():
    """
    Loads credentials from environment or file.
    """
    return load_credentials()


@pytest.fixture(scope="session")
def login_strategy(test_metadata):
    """
    Dynamically loads a login strategy from an environment variable.
    """
    strategy_path = test_metadata.get_login_strategy()
    login_instructions = test_metadata.get_login_instructions()

    return UserInputLoginStrategy(login_instructions)


@pytest.fixture(scope="session")
def dependency_manager():
    """
    A session-level dependency manager to handle test dependencies.
    """
    return DependencyManager()


@pytest.fixture(scope="session", autouse=True)
def register_dependency_hooks(request, dependency_manager):
    """
    Hook into Pytest to run dependency checks before tests and record outcomes after tests.
    """
    # Store in pytest config for access in hooks
    request.config._dependency_manager = dependency_manager


#############################
# Browser and Context Setup
#############################


@pytest.fixture(scope="session")
def browser_type_launch_args(test_metadata):
    """
    Provides arguments to launch browser based on metadata.
    For simplicity, let's assume test_metadata can provide browser type and headless options.
    """
    browser_type = test_metadata.get_browser(default="chromium")
    headless = test_metadata.get_headless()
    args = [
        "--no-sandbox",
        "--disable-setuid-sandbox",
        "--disable-gpu",
        "--single-process",
    ]
    # Extend with logic to determine headless or other flags
    return {"headless": headless, "browser": browser_type, "args": args}


@pytest.fixture(scope="session")
def browser_context_args(test_metadata):
    """
    Default browser context arguments from metadata.
    Override in per-test fixtures if needed.
    """
    return {
        "viewport": test_metadata.get_viewport(),
        "user_agent": "Chrome/69.0.3497.100 Safari/537.36",
    }


@pytest.fixture(scope="function")
def page(
    request,
    browser_type_launch_args,
    browser_context_args,
    credentials,
    login_strategy,
    cred_key_param,
    test_metadata,
):
    """
    The main page fixture:
    - Reads per-test markers (e.g. @pytest.mark.viewport)
    - Launches the browser with given arguments
    - Creates a new context and page
    - Runs login if required
    - Starts trace, captures screenshots
    - Teardown: captures final screenshot, stops trace, closes context
    """
    # Handle per-test viewport override
    viewport_marker = request.node.get_closest_marker("viewport")
    final_context_args = dict(browser_context_args)
    if viewport_marker:
        w = viewport_marker.kwargs.get("width", final_context_args["viewport"]["width"])
        h = viewport_marker.kwargs.get(
            "height", final_context_args["viewport"]["height"]
        )
        final_context_args["viewport"] = {"width": w, "height": h}
    # Launch the browser
    with sync_playwright() as p:
        browser_type = browser_type_launch_args.get("browser", "chromium")
        if browser_type == "chromium":
            bt = p.chromium
        elif browser_type == "firefox":
            bt = p.firefox
        else:
            bt = p.webkit

        launch_args = dict(browser_type_launch_args)
        launch_args.pop(
            "browser", None
        )  # remove browser key as it's not a valid arg for launch
        browser = bt.launch(**launch_args)

        # Create a new context with overridden args if any
        context = browser.new_context(**final_context_args)

        # Start tracing for debugging
        start_trace(context)

        pg = context.new_page()
        bugster_page = BugsterPage(pg)
        credentials_list = credentials.get("auth", {}).get("credentials", [])
        if cred_key_param:
            # Multiple credentials scenario (or * scenario)
            selected_cred = next(
                (cred for cred in credentials_list if cred["id"] == cred_key_param),
                None,
            )
            if not selected_cred:
                raise ValueError(f"Credential '{cred_key_param}' not found.")
            login_strategy.run_login(bugster_page, selected_cred, test_metadata)
        else:
            # Check if there's a login marker with a single credential scenario
            login_marker = request.node.get_closest_marker("login")
            if login_marker:
                creds = login_marker.kwargs.get("credentials", None)
                if isinstance(creds, str) and creds != "*":
                    # Single credential scenario
                    selected_cred = next(
                        (cred for cred in credentials_list if cred["id"] == creds), None
                    )
                    if not selected_cred:
                        raise ValueError(f"Credential '{creds}' not found.")
                    login_strategy.run_login(bugster_page, selected_cred, test_metadata)
                # If creds == "*" but we didn't parametrize, that's a logic error in pytest_generate_tests
                # or the scenario isn't handled. Ensure that's handled below.

        startat_marker = request.node.get_closest_marker("startat")
        if startat_marker:
            start_path = startat_marker.kwargs.get("path")
            if start_path is None:
                # Optionally handle the case where user didn't provide path
                raise ValueError(
                    "startat marker requires a 'path' argument, e.g. @pytest.mark.startat(path='/waitlist')."
                )
            # Extract base URL from config or test_metadata if needed
            base_url = test_metadata.get_base_url()
            bugster_page.screenshot = True

            parsed = urlparse(base_url)

            base_path = parsed.path.rstrip("/")
            new_path = f"{base_path}/{start_path.lstrip('/')}"

            # Reconstruct URL with new path while preserving query params
            final_url = urlunparse(
                (
                    parsed.scheme,
                    parsed.netloc,
                    new_path,
                    parsed.params,
                    parsed.query,
                    parsed.fragment,
                )
            )

            bugster_page.goto(final_url)
        else:
            # If no startat marker is present, go to the base URL by default
            base_url = test_metadata.get_base_url()
            bugster_page.goto(base_url)
        bugster_page.screenshot = True
        yield bugster_page
        # Stop and save trace
        test_name = request.node.name
        stop_and_save_trace(context, test_name=test_name)

        # Cleanup
        context.close()
        browser.close()


#############################
# Hooks for Dependencies
#############################
def pytest_generate_tests(metafunc):
    login_marker = metafunc.definition.get_closest_marker("login")
    print(metafunc)
    if login_marker:
        creds = login_marker.kwargs.get("credentials", None)
        print(creds)
        if creds == "*":
            c = load_credentials()
            all_creds = c.get("auth", {}).get("credentials", [])
            param_values = [cred["id"] for cred in all_creds]
            if param_values:
                print(param_values)
                metafunc.parametrize("cred_key_param", param_values, ids=param_values)
        elif isinstance(creds, list):
            if len(creds) > 1:
                metafunc.parametrize("cred_key_param", creds, ids=creds)
        elif isinstance(creds, str):
            pass
        else:
            pass


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_call(item):
    """
    A hook to check dependencies before each test runs and record results after.
    """
    dm = item.session.config._dependency_manager
    dm.check_dependencies(item)
    outcome = yield
    # Record test result
    result = "passed" if outcome.excinfo is None else "failed"
    dm.record_result(item.name, result)


#############################
# Pyest Marks Data Validation
#############################

VALID_PATH_REGEX = re.compile(r"^/[a-zA-Z0-9-/]+$")


def pytest_collection_modifyitems(config, items):
    for item in items:
        startat_marker = item.get_closest_marker("startat")
        if startat_marker:
            path = startat_marker.kwargs.get("path")
            # Check if 'path' is provided
            if path is None:
                raise pytest.UsageError(
                    f"In test {item.name}: @pytest.mark.startat requires a 'path' argument."
                )
            # Validate the path using the regex
            if not VALID_PATH_REGEX.match(path):
                raise pytest.UsageError(
                    f"In test {item.name}: 'path' must 'match / + app_slug' , got '{path}'."
                )
    # Grafo de dependencias a partir de las marcas @pytest.mark.depends(on=[...])
    name_to_item = {item.name: item for item in items}
    graph = {}
    indegree = {}

    # Inicializar estructuras
    for item in items:
        graph[item.name] = []
        indegree[item.name] = 0

    # Llenar el grafo según las dependencias marcadas
    for item in items:
        mark = item.get_closest_marker("depends")
        if mark:
            dependencies = mark.kwargs.get("on", [])
            for dep in dependencies:
                if dep not in name_to_item:
                    # Dependencia no existente
                    raise pytest.UsageError(
                        f"El test {item.name} depende de {dep}, pero no se encontró un test con ese nombre."
                    )
                # Añadimos una arista dep -> item.name
                graph[dep].append(item.name)
                indegree[item.name] += 1

    # Ordenamiento topológico (Kahn's Algorithm)
    queue = [n for n in indegree if indegree[n] == 0]
    sorted_tests = []

    while queue:
        u = queue.pop(0)
        sorted_tests.append(u)
        for v in graph[u]:
            indegree[v] -= 1
            if indegree[v] == 0:
                queue.append(v)

    if len(sorted_tests) != len(items):
        # Esto indica que hay un ciclo o dependencia no resuelta
        raise pytest.UsageError("Existe un ciclo en las dependencias de los tests.")

    # Reordenar los items según el orden topológico
    name_to_position = {name: i for i, name in enumerate(sorted_tests)}
    items.sort(key=lambda i: name_to_position[i.name])


#################################
# Pyest New Marks Registration
#################################


def pytest_configure(config):
    config.addinivalue_line(
        "markers", "login(credentials=...): specify which credentials to use for login"
    )
    config.addinivalue_line(
        "markers",
        "depends(on=[]): marks a test that depends on other tests",
    )
    config.addinivalue_line(
        "markers", "startat(path): start the test from the given path within the app"
    )

    # Set the BUGSTER_BASE_DIR environment variable if --bugster-dir is provided
    bugster_dir = config.getoption("--bugster-dir")
    if bugster_dir:
        os.environ["BUGSTER_BASE_DIR"] = bugster_dir


def pytest_addoption(parser):
    """Add custom command line options to pytest."""
    parser.addoption(
        "--env",
        action="store",
        default="dev",
        help="Environment to run tests against (e.g., dev, qa, prod)",
    )

    # Add option for Bugster directory
    parser.addoption(
        "--bugster-dir",
        action="store",
        help="Base directory for Bugster files (credentials, traces, screenshots)",
    )
