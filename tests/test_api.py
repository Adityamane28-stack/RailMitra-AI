import os
import sys
from pathlib import Path

# Add backend directory to path
backend_dir = Path(__file__).resolve().parent.parent / "backend"
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from fastapi.testclient import TestClient
from app.main import app
from app.services.image_ai import analyze_image
from app.services.rail_vision import classify_railway_image
from app.services.ai_service import analyze_complaint
from app.services.audio_ai import analyze_audio

client = TestClient(app)


def test_health_and_database():
    print("Testing /health...")
    res = client.get("/health")
    assert res.status_code == 200
    assert res.json()["status"] == "healthy"
    print("  [PASS] Health check passed")
    print("Testing /database-test...")
    res = client.get("/database-test")
    assert res.status_code == 200
    assert res.json()["status"] == "success"
    print("  [PASS] Database connection passed")


def test_admin_flow():
    print("Testing Admin Login...")
    res = client.post("/admin/login", data={"username": "admin", "password": "admin123"})
    assert res.status_code == 200
    data = res.json()
    assert data["success"] is True
    admin_token = data["access_token"]
    print("  [PASS] Admin login succeeded, token acquired")

    admin_headers = {"Authorization": f"Bearer {admin_token}"}

    print("Testing Admin /admin/me...")
    res = client.get("/admin/me", headers=admin_headers)
    assert res.status_code == 200
    assert res.json()["username"] == "admin"
    print("  [PASS] Admin profile verified")

    print("Testing Admin /admin/stats...")
    res = client.get("/admin/stats", headers=admin_headers)
    assert res.status_code == 200
    stats = res.json()
    assert stats["success"] is True
    assert "total_complaints" in stats
    print(f"  [PASS] Admin stats verified: Total={stats['total_complaints']}, Pending={stats['pending']}")

    return admin_token


def test_passenger_and_complaints_flow(admin_token):
    import time
    test_username = f"testuser_{int(time.time())}"

    print(f"Testing Passenger Register ({test_username})...")
    res = client.post(
        "/passenger/register",
        data={
            "username": test_username,
            "password": "Password123!",
            "passenger_name": "Rohan Sharma",
            "phone_number": "9876543210"
        }
    )
    assert res.status_code == 200
    assert res.json()["success"] is True
    print("  [PASS] Passenger registered")

    print("Testing Passenger Login...")
    res = client.post(
        "/passenger/login",
        data={
            "username": test_username,
            "password": "Password123!"
        }
    )
    assert res.status_code == 200
    data = res.json()
    assert data["success"] is True
    passenger_token = data["access_token"]
    print("  [PASS] Passenger login succeeded, token acquired")

    p_headers = {"Authorization": f"Bearer {passenger_token}"}

    print("Testing Passenger /passenger/me...")
    res = client.get("/passenger/me", headers=p_headers)
    assert res.status_code == 200
    assert res.json()["username"] == test_username
    print("  [PASS] Passenger profile verified")

    print("Testing Complaint Creation with NLP Auto-Categorization...")
    # Fire complaint description -> should detect Fire/Emergency and Critical priority
    res = client.post(
        "/complaints/",
        headers=p_headers,
        data={
            "train_number": "12952",
            "coach_number": "B3",
            "seat_number": "45",
            "pnr_number": "2458901234",
            "location": "Near Kota Junction",
            "description": "Heavy smoke and spark from the electrical panel near washroom!",
        }
    )
    assert res.status_code == 200
    c_data = res.json()
    assert c_data["success"] is True
    complaint_id = c_data["complaint_id"]
    assert c_data["priority"] == "Critical"
    assert c_data["department"] == "Emergency Response"
    print(f"  [PASS] Complaint #{complaint_id} created & auto-classified as {c_data['category']} ({c_data['priority']})")

    print("Testing Passenger /complaints/my...")
    res = client.get("/complaints/my", headers=p_headers)
    assert res.status_code == 200
    my_c = res.json()
    assert my_c["count"] >= 1
    print(f"  [PASS] My complaints returned {my_c['count']} records")

    print(f"Testing Public Live Tracking for Complaint #{complaint_id}...")
    res = client.get(f"/complaints/track/{complaint_id}")
    assert res.status_code == 200
    track_data = res.json()
    assert track_data["success"] is True
    assert len(track_data["timeline"]) == 4
    print("  [PASS] Live tracking timeline verified (4 steps)")

    print(f"Testing Public Live Tracking via PNR...")
    res = client.get("/complaints/track/2458901234")
    assert res.status_code == 200
    assert res.json()["complaint"]["id"] == complaint_id
    print("  [PASS] PNR lookup verified")

    admin_headers = {"Authorization": f"Bearer {admin_token}"}

    print(f"Testing Admin Status Update for #{complaint_id}...")
    res = client.put(f"/complaints/{complaint_id}/status", headers=admin_headers, data={"status": "In Progress"})
    assert res.status_code == 200
    assert res.json()["status"] == "In Progress"
    print("  [PASS] Status updated to In Progress")

    print(f"Testing Admin Priority Update for #{complaint_id}...")
    res = client.put(f"/complaints/{complaint_id}/priority", headers=admin_headers, data={"priority": "High"})
    assert res.status_code == 200
    assert res.json()["priority"] == "High"
    print("  [PASS] Priority updated to High")

    print(f"Testing Admin Resolve Complaint #{complaint_id}...")
    res = client.put(f"/complaints/{complaint_id}/resolve", headers=admin_headers)
    assert res.status_code == 200
    assert res.json()["status"] == "Resolved"
    print("  [PASS] Complaint resolved successfully")


def test_ai_services():
    print("Testing NLP AI Text Classifier...")
    res1 = analyze_complaint("Toilet flush is broken and floor is completely dirty and stinking")
    assert res1["category"] == "Cleanliness"
    assert res1["department"] == "Housekeeping"
    print(f"  [PASS] Cleanliness text test: {res1['category']} -> {res1['department']}")

    res2 = analyze_complaint("AC is not cooling at all, fan is not working in coach A2")
    assert res2["category"] == "Electrical Issue"
    assert res2["department"] == "Electrical Department"
    print(f"  [PASS] Electrical text test: {res2['category']} -> {res2['department']}")

    print("Testing Railway Vision Label Classifier...")
    v_res = classify_railway_image("water leakage inside railway coach", 0.92)
    assert v_res["category"] == "Water Leakage"
    assert v_res["priority"] == "High"
    assert v_res["department"] == "Coach Maintenance"
    print(f"  [PASS] Vision label classification test: {v_res['category']} ({v_res['priority']})")


if __name__ == "__main__":
    print("\n==========================================")
    print("       RAILMITRA-AI FULL TEST SUITE       ")
    print("==========================================\n")
    test_health_and_database()
    admin_tok = test_admin_flow()
    test_passenger_and_complaints_flow(admin_tok)
    test_ai_services()
    print("\n==========================================")
    print("     ALL TESTS PASSED WITH 100% SUCCESS!  ")
    print("==========================================\n")
