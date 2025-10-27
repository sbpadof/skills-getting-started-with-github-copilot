from fastapi.testclient import TestClient
from src.app import app

client = TestClient(app)

def test_read_root():
    response = client.get("/")
    assert response.status_code in (200, 307)  # Both codes are valid for redirects
    if response.status_code == 307:
        assert response.headers["location"] == "/static/index.html"

def test_get_activities():
    response = client.get("/activities")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert "Chess Club" in data
    assert "Programming Class" in data

def test_signup_for_activity():
    activity_name = "Chess Club"
    email = "test@mergington.edu"
    
    # Try to sign up
    response = client.post(f"/activities/{activity_name}/signup?email={email}")
    assert response.status_code == 200
    assert response.json() == {"message": f"Signed up {email} for {activity_name}"}
    
    # Verify participant was added
    response = client.get("/activities")
    data = response.json()
    assert email in data[activity_name]["participants"]

def test_duplicate_signup():
    activity_name = "Programming Class"
    email = "emma@mergington.edu"  # Already registered
    
    response = client.post(f"/activities/{activity_name}/signup?email={email}")
    assert response.status_code == 400
    assert response.json() == {"detail": "Student already signed up for this activity"}

def test_signup_nonexistent_activity():
    response = client.post("/activities/NonexistentClub/signup?email=test@mergington.edu")
    assert response.status_code == 404
    assert response.json() == {"detail": "Activity not found"}

def test_unregister_from_activity():
    activity_name = "Chess Club"
    email = "michael@mergington.edu"  # Existing participant
    
    # Try to unregister
    response = client.delete(f"/activities/{activity_name}/unregister?email={email}")
    assert response.status_code == 200
    assert response.json() == {"message": f"Unregistered {email} from {activity_name}"}
    
    # Verify participant was removed
    response = client.get("/activities")
    data = response.json()
    assert email not in data[activity_name]["participants"]

def test_unregister_not_registered():
    activity_name = "Chess Club"
    email = "notregistered@mergington.edu"
    
    response = client.delete(f"/activities/{activity_name}/unregister?email={email}")
    assert response.status_code == 400
    assert response.json() == {"detail": "Student is not registered for this activity"}

def test_unregister_nonexistent_activity():
    response = client.delete("/activities/NonexistentClub/unregister?email=test@mergington.edu")
    assert response.status_code == 404
    assert response.json() == {"detail": "Activity not found"}