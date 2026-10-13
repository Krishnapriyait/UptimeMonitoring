import pytest
from app import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_home_status(client):
    response = client.get('/')
    assert response.status_code == 200

def test_api_monitors(client):
    response = client.get('/api/monitors')
    assert response.status_code == 200