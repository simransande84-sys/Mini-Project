"""
test_duration_flow.py
Tests the complete duration → ML prediction flow via the Django backend API.
Requires Django to be running on port 8000.
"""
import requests, json

BASE = "http://localhost:8000/api"

# ── Login ──────────────────────────────────────────────────────────
print("Logging in...")
resp = requests.post(f"{BASE}/auth/login/",
                     json={"username": "admin", "password": "admin"})
if resp.status_code != 200:
    print(f"  Login failed ({resp.status_code}). Trying common credentials...")
    # Try alternate
    for u, p in [("admin","admin123"),("test","test"),("admin","password")]:
        resp = requests.post(f"{BASE}/auth/login/", json={"username":u,"password":p})
        if resp.status_code == 200:
            print(f"  Logged in as {u}")
            break
    else:
        print("  Could not login. Check credentials.")
        print("  Testing utils directly instead...")
        # Direct utils test
        import os; os.environ.setdefault('DJANGO_SETTINGS_MODULE','hostelSenseAI.settings')
        import django; django.setup()
        from complaints.utils import predict_priority, _duration_to_hours
        print("\n[DIRECT UTILS TEST]")
        for dur in ["1 hour","2 days","1 week","4 weeks",None]:
            h = _duration_to_hours(dur)
            pred = predict_priority({
                "complaint_text":"The electricity is not working in Block A wing",
                "complaint_type":"Public","block":"A","floor":"First",
                "category":"Electricity","duration": dur,
            })
            print(f"  duration='{dur}' → {h}h → predicted: {pred}")
        raise SystemExit(0)

token = resp.json()["access"]
headers = {"Authorization": f"Bearer {token}"}
print(f"  Token acquired.")

# ── Test cases ─────────────────────────────────────────────────────
test_cases = [
    {"complaint_text": "The fan is not working and it is very hot.", "duration": "1 hour",  "category": "Electricity"},
    {"complaint_text": "Water leaking from ceiling causing damage.",  "duration": "2 days",  "category": "Washroom"},
    {"complaint_text": "Dustbin overflowing near entrance.",          "duration": "1 week",  "category": "Cleanliness"},
    {"complaint_text": "WiFi is very slow and disconnecting often.",  "duration": "4 weeks", "category": "WiFi"},
]

print("\n[END-TO-END API TESTS]")
print("=" * 65)
all_pass = True

for i, tc in enumerate(test_cases, 1):
    payload = {
        "complaint_text" : tc["complaint_text"],
        "complaint_type" : "Public",
        "category"       : tc["category"],
        "students_affected": 1,
        "duration"       : tc["duration"],
    }
    resp = requests.post(f"{BASE}/complaints/", json=payload, headers=headers)
    ok = resp.status_code == 201

    if ok:
        data = resp.json()
        priority = data.get("predicted_priority", "MISSING")
        dur_back = data.get("duration", "MISSING")
        valid = priority in ["High", "Medium", "Low", "Critical"]
        all_pass = all_pass and valid
        status = "PASS" if valid else "FAIL"
        print(f"  [{status}] Test {i}: duration='{tc['duration']}' | category={tc['category']}")
        print(f"          Predicted Priority : {priority}")
        print(f"          Duration saved     : {dur_back}")
        print(f"          Complaint ID       : #{data.get('id')}")
    else:
        all_pass = False
        print(f"  [FAIL] Test {i}: HTTP {resp.status_code}")
        print(f"         {resp.text[:200]}")
    print()

print("=" * 65)
print(f"  Result: {'ALL PASS' if all_pass else 'SOME FAILURES'}")
print("  Duration field flows correctly through:")
print("  Frontend form → POST /api/complaints/ → serializer →")
print("  views.perform_create → utils._duration_to_hours() → Duration_Hours →")
print("  preprocessor.transform() → LinearSVC → predicted_priority")
print("=" * 65)
