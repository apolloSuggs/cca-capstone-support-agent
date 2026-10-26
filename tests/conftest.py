import pytest

from support_agent.backend import demo_backend


@pytest.fixture
def backend():
    return demo_backend()
