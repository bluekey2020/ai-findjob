import pytest
import asyncio
import os
import tempfile

os.environ['DATABASE_URL'] = 'sqlite+aiosqlite://'
os.environ['JWT_SECRET_KEY'] = 'test-secret-key'
os.environ['ANTHROPIC_API_KEY'] = ''


@pytest.fixture(scope='session')
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()
