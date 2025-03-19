import pytest
from funcnodes_core import testing as fntesting


def pytest_addoption(parser):
    group = parser.getgroup("funcnodes-pytest", "Plugin for tesing Funcnodes-Nodes")
    group.addoption(
        "--nodetests-only",
        action="store_true",
        help="Run only tests marked as nodetest",
    )


def pytest_collection_modifyitems(session: pytest.Session, config, items):
    if config.getoption("--nodetests-only"):
        selected = []
        deselected = []
        for item in items:
            if "nodetest" in item.keywords:
                selected.append(item)
            else:
                deselected.append(item)

        if deselected:
            config.hook.pytest_deselected(items=deselected)

        items[:] = selected

    # Add a custom session attribute
    session.tested_nodes = set()

    for item in items:
        if "nodetest" in item.keywords:
            # get marger argument
            marker = item.get_closest_marker("nodetest")
            nodes = marker.kwargs.get("nodes")
            if nodes is None:
                continue
            session.tested_nodes.update(nodes)


def pytest_configure(config: pytest.Config):
    config.addinivalue_line("markers", "nodetest: mark test as an async node test")


@pytest.fixture(scope="session", autouse=True)
def all_nodes(request):
    return request.session.tested_nodes


@pytest.fixture(scope="session", autouse=True)
def my_session_fixture():
    # Setup code executed once per session
    print("Session fixture setup")
    yield
    # Teardown code executed once after all tests complete
    print("Session fixture teardown")


@pytest.fixture(autouse=True)
def nodetest_setup_teardown(request):
    marker = request.node.get_closest_marker("nodetest")
    if marker:
        # Code to run before the test function
        fntesting.setup()
    yield
    if marker:
        # Code to run after the test function
        fntesting.teardown()
