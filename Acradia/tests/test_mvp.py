import os
import tempfile
from pathlib import Path

from fastapi.testclient import TestClient

_TEST_DB = Path(tempfile.gettempdir()) / "sahaay_test_mvp.db"
if _TEST_DB.exists():
    _TEST_DB.unlink()

os.environ["DATABASE_URL"] = f"sqlite:///{_TEST_DB}"

from backend.app.main import app  # noqa: E402


def test_full_mvp_citizen_journey():
    with TestClient(app) as client:
        # 1. Health & frontend root
        health = client.get("/api/health")
        assert health.status_code == 200
        assert health.json()["status"] == "ok"

        home = client.get("/")
        assert home.status_code == 200
        assert "SAHAAY" in home.text

        # 2. Curated scheme catalogue seeded
        schemes_resp = client.get("/api/schemes")
        assert schemes_resp.status_code == 200
        schemes = schemes_resp.json()
        assert len(schemes) >= 6

        # 3. Profile creation
        profile_payload = {
            "name": "Ramesh Kumar",
            "age": 32,
            "income": 150000,
            "location": "Maharashtra",
            "occupation": "farmer",
            "preferred_language": "hi",
        }
        profile_resp = client.post("/api/profiles", json=profile_payload)
        assert profile_resp.status_code == 201
        assert profile_resp.json()["occupation"] == "farmer"

        # 4. Eligibility matching
        match_resp = client.post("/api/schemes/match", json=profile_payload)
        assert match_resp.status_code == 200
        match_data = match_resp.json()
        matched_slugs = [m["scheme"]["slug"] for m in match_data["matches"]]
        assert "pm-kisan" in matched_slugs
        assert "maharashtra-ladki-bahin" in matched_slugs
        assert "nsp-post-matric" not in matched_slugs

        # 5. Grounded AI assistant (RAG)
        ask_resp = client.post(
            "/api/assistant/ask",
            json={"question": "How do I apply for PM-KISAN?", "scheme_slug": "pm-kisan"},
        )
        assert ask_resp.status_code == 200
        ask_data = ask_resp.json()
        assert "pmkisan.gov.in" in ask_data["answer"]
        assert any(c["slug"] == "pm-kisan" for c in ask_data["citations"])

        # 6. Voice synthesis metadata
        voice_resp = client.post(
            "/api/voice/speak",
            json={"text": "PM Kisan provides 6000 rupees per year.", "language": "hi"},
        )
        assert voice_resp.status_code == 200
        assert voice_resp.json()["bcp47_lang"] == "hi-IN"

        # 7. NGO consent enforcement & location routing
        no_consent = client.post(
            "/api/ngo/requests",
            json={
                "citizen_name": "Ramesh Kumar",
                "contact_info": "9876543210",
                "location": "Maharashtra",
                "scheme_slug": "pm-kisan",
                "message": "Need help uploading land records.",
                "consent_given": False,
            },
        )
        assert no_consent.status_code == 400

        with_consent = client.post(
            "/api/ngo/requests",
            json={
                "citizen_name": "Ramesh Kumar",
                "contact_info": "9876543210",
                "location": "Maharashtra",
                "scheme_slug": "pm-kisan",
                "message": "Need help uploading land records.",
                "consent_given": True,
            },
        )
        assert with_consent.status_code == 201
        req_data = with_consent.json()
        assert req_data["status"] == "assigned"
        assert req_data["assigned_ngo"]["location"] == "Maharashtra"

        # 8. Update request status
        patch_resp = client.patch(
            f"/api/ngo/requests/{req_data['id']}",
            json={"status": "in_progress"},
        )
        assert patch_resp.status_code == 200
        assert patch_resp.json()["status"] == "in_progress"
