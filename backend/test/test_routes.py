import sys
import os
import random
import time
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import text
from sqlalchemy.exc import OperationalError

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from database import SessionLocal
from main import app
from services.matching_service import create_match_record

client = TestClient(app)
TEST_PREFIX = f"pytest_route_{int(time.time())}"
PASSWORD = "Test1234!"

@pytest.fixture(scope="module", autouse=True)
def setup_database():
    """Vérifie que la DB est prête et nettoie les données après les tests."""
    db = SessionLocal()
    try:
        result = db.execute(text("SELECT to_regclass('public.users')")).scalar()
        if not result:
            pytest.exit("La base de données n'est pas initialisée ou la table 'users' est manquante.")
    except OperationalError as exc:
        pytest.exit(f"Impossible de se connecter à la base de données: {exc}")
    finally:
        db.close()

    yield

    db = SessionLocal()
    try:
        users = [row[0] for row in db.execute(
            text("SELECT id FROM users WHERE email LIKE :prefix"),
            {"prefix": f"{TEST_PREFIX}%"},
        ).fetchall()]

        if users:
            ids = ",".join(str(uid) for uid in users)
            db.execute(text(f"DELETE FROM messages WHERE conversation_id IN (SELECT c.id FROM conversations c JOIN matches m ON c.match_id = m.id WHERE m.mentor_id IN ({ids}) OR m.mentee_id IN ({ids}))"))
            db.execute(text(f"DELETE FROM conversations WHERE match_id IN (SELECT id FROM matches WHERE mentor_id IN ({ids}) OR mentee_id IN ({ids}))"))
            db.execute(text(f"DELETE FROM matches WHERE mentor_id IN ({ids}) OR mentee_id IN ({ids})"))
            db.execute(text(f"DELETE FROM post_availabilities WHERE post_id IN (SELECT id FROM mentorship_posts WHERE user_id IN ({ids}))"))
            db.execute(text(f"DELETE FROM mentorship_posts WHERE user_id IN ({ids})"))
            db.execute(text(f"DELETE FROM user_availabilities WHERE user_id IN ({ids})"))
            db.execute(text(f"DELETE FROM user_skills WHERE user_id IN ({ids})"))
            db.execute(text(f"DELETE FROM users WHERE id IN ({ids})"))
            db.commit()
    except Exception as exc:
        db.rollback()
        print(f"Cleanup failed: {exc}")
    finally:
        db.close()


def auth_headers(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}

@pytest.fixture(scope="module")
def shared_data():
    """Dictionnaire partagé pour passer des données entre les tests (tokens, ids, etc.)"""
    return {}


# --- TESTS AUTHENTIFICATION ET UTILISATEURS ---

def test_register_users(shared_data):
    for suffix in ["user1", "user2"]:
        email = f"{TEST_PREFIX}_{suffix}@example.com"
        phone_number = f"+2299000{random.randint(1000, 9999):04d}"
        payload = {
            "first_name": suffix.capitalize(),
            "last_name": "RouteTest",
            "email": email,
            "phone_number": phone_number,
            "password": PASSWORD,
            "field_of_study": "IA",
            "level": "L1",
            "bio": "Utilisateur de test pour les routes API",
        }
        response = client.post("/api/auth/register", json=payload)
        assert response.status_code == 201
        data = response.json()
        shared_data[suffix] = {"email": email, "token": data["access_token"], "id": data["user"]["id"]}

def test_login_users(shared_data):
    for suffix in ["user1", "user2"]:
        response = client.post("/api/auth/login", json={"email": shared_data[suffix]["email"], "password": PASSWORD})
        assert response.status_code == 200
        shared_data[suffix]["token"] = response.json()["access_token"]

def test_auth_reset_password(shared_data):
    response = client.post("/api/auth/reset-password", json={"email": shared_data["user1"]["email"]})
    assert response.status_code == 200

def test_auth_me(shared_data):
    response = client.get("/api/auth/me", headers=auth_headers(shared_data["user1"]["token"]))
    assert response.status_code == 200

def test_users_me(shared_data):
    response = client.get("/api/users/me", headers=auth_headers(shared_data["user1"]["token"]))
    assert response.status_code == 200

def test_update_users_me(shared_data):
    response = client.put(
        "/api/users/me",
        headers=auth_headers(shared_data["user1"]["token"]),
        json={"first_name": "Route1", "bio": "Profil mis à jour"},
    )
    assert response.status_code == 200


# --- TESTS COMPÉTENCES ET DISPONIBILITÉS ---

def test_get_skills(shared_data):
    response = client.get("/api/skills")
    assert response.status_code == 200
    skills = response.json()
    assert len(skills) > 0
    shared_data["skill_id"] = skills[0]["id"]

def test_get_skill_by_id(shared_data):
    response = client.get(f"/api/skills/{shared_data['skill_id']}")
    assert response.status_code == 200

def test_add_user_skill(shared_data):
    response = client.post(
        "/api/users/me/skills",
        headers=auth_headers(shared_data["user1"]["token"]),
        json={"skill_id": shared_data["skill_id"], "proficiency": "weak"},
    )
    assert response.status_code == 201

def test_add_user_availability(shared_data):
    response = client.post(
        "/api/users/me/availabilities",
        headers=auth_headers(shared_data["user1"]["token"]),
        json={"day_of_week": "Monday", "start_time": "10:00", "end_time": "12:00"},
    )
    assert response.status_code == 201
    shared_data["availability_id"] = response.json()["id"]

def test_get_user_availabilities(shared_data):
    response = client.get("/api/users/me/availabilities", headers=auth_headers(shared_data["user1"]["token"]))
    assert response.status_code == 200

def test_delete_user_availability(shared_data):
    response = client.delete(
        f"/api/users/me/availabilities/{shared_data['availability_id']}",
        headers=auth_headers(shared_data["user1"]["token"]),
    )
    assert response.status_code == 200

def test_delete_user_skill(shared_data):
    response = client.delete(
        f"/api/users/me/skills/{shared_data['skill_id']}",
        headers=auth_headers(shared_data["user1"]["token"]),
    )
    assert response.status_code == 200

def test_recreate_data_for_matches(shared_data):
    # Recréer les éléments requis pour les matches et le chat
    response = client.post(
        "/api/users/me/skills",
        headers=auth_headers(shared_data["user1"]["token"]),
        json={"skill_id": shared_data["skill_id"], "proficiency": "weak"},
    )
    assert response.status_code == 201

    response = client.post(
        "/api/users/me/skills",
        headers=auth_headers(shared_data["user2"]["token"]),
        json={"skill_id": shared_data["skill_id"], "proficiency": "strong"},
    )
    assert response.status_code == 201

    response = client.post(
        "/api/users/me/availabilities",
        headers=auth_headers(shared_data["user2"]["token"]),
        json={"day_of_week": "Monday", "start_time": "11:00", "end_time": "13:00"},
    )
    assert response.status_code == 201


# --- TESTS POSTS DE MENTORAT ---

def test_create_post(shared_data):
    post_payload = {
        "type": "request",
        "skill_id": shared_data["skill_id"],
        "mode": "online",
        "description": "Recherche mentorat en Python",
        "availabilities": [
            {"day_of_week": "Monday", "start_time": "10:00", "end_time": "12:00"}
        ],
    }
    response = client.post(
        "/api/posts",
        headers=auth_headers(shared_data["user1"]["token"]),
        json=post_payload,
    )
    assert response.status_code == 201
    shared_data["post_id"] = response.json()["id"]

def test_get_posts(shared_data):
    response = client.get("/api/posts", headers=auth_headers(shared_data["user1"]["token"]))
    assert response.status_code == 200

def test_get_post_by_id(shared_data):
    response = client.get(f"/api/posts/{shared_data['post_id']}", headers=auth_headers(shared_data["user1"]["token"]))
    assert response.status_code == 200

def test_update_post(shared_data):
    response = client.put(
        f"/api/posts/{shared_data['post_id']}",
        headers=auth_headers(shared_data["user1"]["token"]),
        json={"mode": "both", "description": "Post mis à jour"},
    )
    assert response.status_code == 200

def test_delete_post(shared_data):
    response = client.delete(
        f"/api/posts/{shared_data['post_id']}",
        headers=auth_headers(shared_data["user1"]["token"]),
    )
    assert response.status_code == 200


# --- TESTS MATCHING ET MESSAGERIE ---

def test_get_matches(shared_data):
    response = client.get("/api/matches", headers=auth_headers(shared_data["user1"]["token"]))
    assert response.status_code == 200
    matches = response.json().get("matches", [])
    assert len(matches) > 0, "Aucun match trouvé par /api/matches"
    shared_data["match_id"] = matches[0]["id"]

def test_accept_match(shared_data):
    response = client.put(
        f"/api/matches/{shared_data['match_id']}/accept",
        headers=auth_headers(shared_data["user1"]["token"]),
    )
    assert response.status_code == 200
    shared_data["conversation_id"] = response.json()["conversation_id"]

def test_reject_match(shared_data):
    db = SessionLocal()
    try:
        reject_match = create_match_record(
            db,
            mentor_id=shared_data["user2"]["id"],
            mentee_id=shared_data["user1"]["id"],
            skill_id=shared_data["skill_id"],
            score=45.0,
            status="pending",
        )
        reject_match_id = reject_match.id
    finally:
        db.close()

    response = client.put(
        f"/api/matches/{reject_match_id}/reject",
        headers=auth_headers(shared_data["user1"]["token"]),
    )
    assert response.status_code == 200

def test_get_conversations(shared_data):
    response = client.get("/api/conversations", headers=auth_headers(shared_data["user1"]["token"]))
    assert response.status_code == 200
    conversations = response.json().get("conversations", [])
    assert len(conversations) > 0

def test_get_messages(shared_data):
    response = client.get(
        f"/api/conversations/{shared_data['conversation_id']}/messages",
        headers=auth_headers(shared_data["user1"]["token"]),
    )
    assert response.status_code == 200

def test_send_message(shared_data):
    response = client.post(
        f"/api/conversations/{shared_data['conversation_id']}/messages",
        headers=auth_headers(shared_data["user1"]["token"]),
        json={"content": "Bonjour, voici un message de test."},
    )
    assert response.status_code == 201
    shared_data["message_id"] = response.json()["id"]

def test_get_messages_after_send(shared_data):
    response = client.get(
        f"/api/conversations/{shared_data['conversation_id']}/messages",
        headers=auth_headers(shared_data["user1"]["token"]),
    )
    assert response.status_code == 200

def test_read_message(shared_data):
    response = client.put(
        f"/api/messages/{shared_data['message_id']}/read",
        headers=auth_headers(shared_data["user2"]["token"]),
    )
    assert response.status_code == 200
