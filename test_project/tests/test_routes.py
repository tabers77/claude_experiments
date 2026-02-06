"""
Tests for API routes.
"""
import pytest
from fastapi.testclient import TestClient
from src.main import app
from src.api.routes import items_db


@pytest.fixture(autouse=True)
def clear_db():
    """Clear the in-memory database before each test."""
    items_db.clear()
    yield
    items_db.clear()


@pytest.fixture
def client():
    """Create a test client."""
    return TestClient(app)


def test_root_endpoint(client):
    """Test the health check endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_create_item(client):
    """Test creating an item."""
    response = client.post(
        "/api/items",
        json={"name": "Test Item", "description": "A test item"}
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Test Item"
    assert data["description"] == "A test item"
    assert "id" in data
    assert "created_at" in data


def test_list_items_empty(client):
    """Test listing items when empty."""
    response = client.get("/api/items")
    assert response.status_code == 200
    assert response.json() == []


def test_list_items_with_data(client):
    """Test listing items after creating some."""
    client.post("/api/items", json={"name": "Item 1"})
    client.post("/api/items", json={"name": "Item 2"})

    response = client.get("/api/items")
    assert response.status_code == 200
    assert len(response.json()) == 2


def test_get_item(client):
    """Test getting a specific item."""
    create_response = client.post("/api/items", json={"name": "Test Item"})
    item_id = create_response.json()["id"]

    response = client.get(f"/api/items/{item_id}")
    assert response.status_code == 200
    assert response.json()["name"] == "Test Item"


def test_get_item_not_found(client):
    """Test getting a non-existent item."""
    response = client.get("/api/items/nonexistent")
    assert response.status_code == 404


def test_delete_item(client):
    """Test deleting an item."""
    create_response = client.post("/api/items", json={"name": "To Delete"})
    item_id = create_response.json()["id"]

    response = client.delete(f"/api/items/{item_id}")
    assert response.status_code == 204

    # Verify it's gone
    get_response = client.get(f"/api/items/{item_id}")
    assert get_response.status_code == 404


def test_delete_item_not_found(client):
    """Test deleting a non-existent item."""
    response = client.delete("/api/items/nonexistent")
    assert response.status_code == 404
