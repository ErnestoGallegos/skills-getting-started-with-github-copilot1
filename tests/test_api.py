import copy
import urllib.parse

import pytest
from fastapi.testclient import TestClient

from src import app as app_module


client = TestClient(app_module.app)


@pytest.fixture(autouse=True)
def restore_activities():
    """Restore the in-memory activities dict after each test to avoid test bleed."""
    original = copy.deepcopy(app_module.activities)
    yield
    app_module.activities = original


def test_get_activities():
    r = client.get("/activities")
    assert r.status_code == 200
    data = r.json()
    assert "Chess Club" in data


def test_signup_adds_participant():
    activity = "Chess Club"
    activity_enc = urllib.parse.quote(activity, safe="")
    email = "testuser@mergington.edu"

    # Ensure participant is not present
    r = client.get("/activities")
    assert email not in r.json()[activity]["participants"]

    # Sign up
    r = client.post(f"/activities/{activity_enc}/signup", params={"email": email})
    assert r.status_code == 200

    # Confirm presence
    r = client.get("/activities")
    assert email in r.json()[activity]["participants"]


def test_delete_removes_participant():
    activity = "Chess Club"
    activity_enc = urllib.parse.quote(activity, safe="")
    email = "michael@mergington.edu"

    # Precondition: michael is in the participants list
    r = client.get("/activities")
    assert email in r.json()[activity]["participants"]

    # Delete
    r = client.delete(f"/activities/{activity_enc}/signup", params={"email": email})
    assert r.status_code == 200

    # Confirm removal
    r = client.get("/activities")
    assert email not in r.json()[activity]["participants"]


def test_duplicate_signup_rejected():
    activity = "Chess Club"
    activity_enc = urllib.parse.quote(activity, safe="")
    email = "duplicate@mergington.edu"

    r = client.post(f"/activities/{activity_enc}/signup", params={"email": email})
    assert r.status_code == 200

    # Second signup should fail with 400
    r = client.post(f"/activities/{activity_enc}/signup", params={"email": email})
    assert r.status_code == 400
