import pytest
from fastapi.testclient import TestClient
from httpx import AsyncClient
from datetime import datetime, timedelta

from main import app

# Test client
client = TestClient(app)


# Mock event data
@pytest.fixture
def event_data():
    start_time = datetime.utcnow() + timedelta(days=1)
    end_time = start_time + timedelta(hours=2)

    return {
        "name": "Test Event",
        "description": "Event for testing",
        "start_time": start_time.isoformat(),
        "end_time": end_time.isoformat(),
        "location": "Test Location",
        "max_attendees": 100
    }


# Tests
def test_create_event(event_data):
    response = client.post("/events/", json=event_data)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == event_data["name"]
    assert data["status"] == "scheduled"
    return data


def test_get_event(event_data):
    # Create an event first
    created_event = test_create_event(event_data)

    # Get the event
    response = client.get(f"/events/{created_event['_id']}")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == event_data["name"]


def test_update_event(event_data):
    # Create an event first
    created_event = test_create_event(event_data)

    # Update the event
    update_data = {"name": "Updated Test Event"}
    response = client.put(f"/events/{created_event['_id']}", json=update_data)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == update_data["name"]


def test_list_events(event_data):
    # Create an event first
    test_create_event(event_data)

    # List events
    response = client.get("/events/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0


def test_delete_event(event_data):
    # Create an event first
    created_event = test_create_event(event_data)

    # Delete the event
    response = client.delete(f"/events/{created_event['_id']}")
    assert response.status_code == 204

    # Try to get the deleted event
    response = client.get(f"/events/{created_event['_id']}")
    assert response.status_code == 404