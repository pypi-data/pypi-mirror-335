import asyncio

import pytest
import pytest_asyncio


@pytest.fixture(scope='session')
async def xxx():
    print('session', id(asyncio.get_event_loop()))
    ...


@pytest.fixture
def yyy():
    print('function', id(asyncio.get_event_loop()))
    ...


async def test_foo(xxx, yyy):
    print('test', id(asyncio.get_event_loop()))


async def test_bar(xxx, yyy):
    print('test', id(asyncio.get_event_loop()))
