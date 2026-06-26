from copy import deepcopy

import pytest
from fastapi.testclient import TestClient

from src import app as app_module
from src.app import app

client = TestClient(app)
INITIAL_ACTIVITIES = deepcopy(app_module.activities)

@pytest.fixture(autouse=True)
def reset_activities():
    app_module.activities.clear()
    app_module.activities.update(deepcopy(INITIAL_ACTIVITIES))
    yield


def test_get_activities():
    # Arrange
    expected_activity = "Chess Club"

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert expected_activity in data
    assert data[expected_activity]["max_participants"] == 12
    assert isinstance(data[expected_activity]["participants"], list)


def test_signup_and_participant_appears():
    # Arrange
    email = "test.student@mergington.edu"
    activity_path = "/activities/Chess%20Club/signup"

    # Act
    response = client.post(activity_path, params={"email": email})

    # Assert
    assert response.status_code == 200
    assert "Signed up" in response.json()["message"]

    # Act
    activities_response = client.get("/activities")

    # Assert
    assert activities_response.status_code == 200
    assert email in activities_response.json()["Chess Club"]["participants"]


def test_delete_participant():
    # Arrange
    email = "test.student@mergington.edu"
    client.post("/activities/Chess%20Club/signup", params={"email": email})

    # Act
    response = client.delete(
        "/activities/Chess%20Club/participants",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 200
    assert "Removed" in response.json()["message"]

    # Act
    activities_response = client.get("/activities")

    # Assert
    assert activities_response.status_code == 200
    assert email not in activities_response.json()["Chess Club"]["participants"]


def test_signup_invalid_activity_returns_404():
    # Arrange
    email = "foo@bar.com"
    invalid_path = "/activities/Invalid%20Club/signup"

    # Act
    response = client.post(invalid_path, params={"email": email})

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_remove_nonexistent_participant_returns_404():
    # Arrange
    email = "missing@mergington.edu"
    delete_path = "/activities/Chess%20Club/participants"

    # Act
    response = client.delete(delete_path, params={"email": email})

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Participant not found"
