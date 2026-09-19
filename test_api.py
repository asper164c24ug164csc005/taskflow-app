import os
import tempfile
import pytest

from app import app, db

@pytest.fixture()
def client():
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)

    app.config.update(
        TESTING=True,
        SQLALCHEMY_DATABASE_URI="sqlite:///" + path,
        JWT_SECRET_KEY="test-secret"
    )

    with app.app_context():
        db.drop_all()
        db.create_all()

    with app.test_client() as client:
        yield client

    with app.app_context():
        db.session.remove()
        db.drop_all()
    os.remove(path)

def register_and_login(client):
    client.post("/api/auth/register", json={
        "name": "Test User",
        "email": "test@example.com",
        "password": "secret123"
    })
    response = client.post("/api/auth/login", json={
        "email": "test@example.com",
        "password": "secret123"
    })
    return response.get_json()["access_token"]

def test_health(client):
    response = client.get("/api/health")
    assert response.status_code == 200

def test_register_and_login(client):
    response = client.post("/api/auth/register", json={
        "name": "Test User",
        "email": "test@example.com",
        "password": "secret123"
    })
    assert response.status_code == 201

    response = client.post("/api/auth/login", json={
        "email": "test@example.com",
        "password": "secret123"
    })
    assert response.status_code == 200
    assert "access_token" in response.get_json()

def test_task_crud(client):
    token = register_and_login(client)
    headers = {"Authorization": f"Bearer {token}"}

    create = client.post("/api/tasks", headers=headers, json={
        "title": "Week 3 API",
        "description": "Build Flask API",
        "status": "pending",
        "priority": "high"
    })
    assert create.status_code == 201
    task_id = create.get_json()["id"]

    get_one = client.get(f"/api/tasks/{task_id}", headers=headers)
    assert get_one.status_code == 200

    update = client.put(f"/api/tasks/{task_id}", headers=headers, json={
        "status": "completed"
    })
    assert update.status_code == 200
    assert update.get_json()["status"] == "completed"

    get_all = client.get("/api/tasks", headers=headers)
    assert get_all.status_code == 200
    assert len(get_all.get_json()) == 1

    delete = client.delete(f"/api/tasks/{task_id}", headers=headers)
    assert delete.status_code == 200
