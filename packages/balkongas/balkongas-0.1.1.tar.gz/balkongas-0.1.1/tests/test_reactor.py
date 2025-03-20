# tests/test_main.py
from balkongas import Reactor
import pytest


@pytest.fixture
def reactor_public():
    return Reactor("6f1d3382-6b95-4adc-9d6f-6785ae0456f3")


def test_example_function(reactor_public):
    reactor_public.refresh()
    assert reactor_public.data["hardware_version"] == "v1"
