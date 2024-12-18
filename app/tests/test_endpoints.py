import pytest
from app import create_app, db

@pytest.fixture
def client():
    app = create_app()
    app.config['TESTING'] = True
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
        yield client

def test_register_and_login(client):
    response = client.post('/register', json={"username": "prof1", "password": "password", "role": "professor"})
    assert response.status_code == 201
    response = client.post('/login', json={"username": "prof1", "password": "password"})
    assert response.status_code == 200
    assert "token" in response.get_json()
