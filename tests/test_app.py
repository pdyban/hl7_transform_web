import pytest
import os
import sys
sys.path.append(os.path.abspath('.'))
print(sys.path)

from app import app


@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        with app.app_context():
            # e.g. app.init_db()
            pass
        yield client

def test_index(client):
    rv = client.get('/')
    # print(rv)
    assert rv.status_code in (200,)

def test_about(client):
    assert client.get('/about').status_code == 200

def test_example(client):
    assert client.get('/example').status_code == 200
