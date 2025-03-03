import pytest
from fastapi.testclient import TestClient
from httpx import AsyncClient
from datetime import datetime, timedelta

from main import app

# Test client
client = TestClient(app)


# Mock event and attendee data
@pytest.fixture
def event_data():
    start_time = datetime.utcnow() + timedelta(hours=1)  # Set as ongoing soon
    end_time = start_time + timedelta(hours=2)

    return {
        "name": "Test Event",
        "description": "Event for testing",
        "start_time": start_time.isoformat(),
        "end_time": end_time.isoformat(),
        "location": "Test Location",
        "max_attendees": 100
    }


@pytest.fixture
def attendee_data():
    return {
        "first_name": "Test",
        "last_name": "User",
        "email": "test@example.com",
        "phone_number": "1234567890"
    }


# Helper to create an event
def create_test_event(event_data):
    response = client.post("/events/", json=event_data)
    assert response.status_code == 201
    return response.json()


# Tests
def test_register_attendee(event_data, attendee_data):
    # Create an event first
    created_event = create_test_event(event_data)

    # Register an attendee
    attendee_data["event_id"] = created_event["_id"]
    response = client.post("/attendees/", json=attendee_data)
    assert response.status_code == 201
    data = response.json()
    assert data["first_name"] == attendee_data["first_name"]
    assert data["check_in_status"] == False
    return data


def test_get_attendee(event_data, attendee_data):
    # Register an attendee first
    created_attendee = test_register_attendee(event_data, attendee_data)

    # Get the attendee
    response = client.get(f"/attendees/{created_attendee['_id']}")
    assert response.status_code == 200
    data = response.json()
    assert data["first_name"] == attendee_data["first_name"]


def test_list_attendees(event_data, attendee_data):
    # Register an attendee first
    created_attendee = test_register_attendee(event_data, attendee_data)

    # List attendees
    response = client.get(f"/attendees/event/{created_attendee['event_id']}")
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0


def test_update_attendee(event_data, attendee_data):
    # Register an attendee first
    created_attendee = test_register_attendee(event_data, attendee_data)

    # Update the attendee
    update_data = {"first_name": "Updated"}
    response = client.put(f"/attendees/{created_attendee['_id']}", json=update_data)
    assert response.status_code == 200
    data = response.json()
    assert data["first_name"] == update_data["first_name"]


def test_check_in_attendee(event_data, attendee_data):
    # Create an event and set it as ongoing
    created_event = create_test_event(event_data)
    client.put(f"/events/{created_event['_id']}", json={"status": "ongoing"})

    # Register an attendee
    attendee_data["event_id"] = created_event["_id"]
    response = client.post("/attendees/", json=attendee_data)
    created_attendee = response.json()

    # Check in the attendee
    response = client.post(f"/attendees/{created_attendee['_id']}/check-in")
    assert response.status_code == 200
    data = response.json()
    assert data["check_in_status"] == True