import pytest
from fastapi.testclient import TestClient

import copy
from src.app import app, activities as app_activities

client = TestClient(app)

# Save a pristine copy of the activities data
ORIGINAL_ACTIVITIES = copy.deepcopy(app_activities)

def reset_activities():
    app_activities.clear()
    app_activities.update(copy.deepcopy(ORIGINAL_ACTIVITIES))

def test_get_activities():
    reset_activities()
    response = client.get("/activities")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert "Chess Club" in data

def test_signup_and_unregister():
    reset_activities()
    activity = "Chess Club"
    email = "testuser@mergington.edu"
    # Ensure not already signed up
    client.post(f"/activities/{activity}/unregister", params={"email": email})
    # Sign up
    response = client.post(f"/activities/{activity}/signup", params={"email": email})
    assert response.status_code == 200
    assert f"Signed up {email}" in response.json()["message"]
    # Try duplicate signup
    response_dup = client.post(f"/activities/{activity}/signup", params={"email": email})
    assert response_dup.status_code == 400
    # Unregister
    response_unreg = client.post(f"/activities/{activity}/unregister", params={"email": email})
    assert response_unreg.status_code == 200
    assert f"Removed {email}" in response_unreg.json()["message"]
    # Unregister again (should fail)
    response_unreg2 = client.post(f"/activities/{activity}/unregister", params={"email": email})
    assert response_unreg2.status_code == 404

def test_signup_activity_not_found():
    reset_activities()
    response = client.post("/activities/Nonexistent/signup", params={"email": "nobody@mergington.edu"})
    assert response.status_code == 404

def test_unregister_activity_not_found():
    reset_activities()
    response = client.post("/activities/Nonexistent/unregister", params={"email": "nobody@mergington.edu"})
    assert response.status_code == 404
