"""
Script de test des routes FastAPI pour IFRI_MentorLink.
Usage:
    python test_routes.py

Ce script utilise TestClient pour appeler les routes du backend
sans lancer un serveur HTTP séparé.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import random
import time
from fastapi.testclient import TestClient
from sqlalchemy import text
from sqlalchemy.exc import OperationalError

from database import SessionLocal
from main import app
from services.matching_service import create_match_record

client = TestClient(app)
TEST_PREFIX = f"unittest_route_{int(time.time())}"
PASSWORD = "Test1234!"


def auth_headers(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def assert_status_code(response, expected_code, route_name: str):
    if response.status_code != expected_code:
        raise AssertionError(
            f"{route_name} failed: expected {expected_code}, got {response.status_code}. Response: {response.text}"
        )


def ensure_db_ready():
    db = SessionLocal()
    try:
        result = db.execute(text("SELECT to_regclass('public.users')")).scalar()
        if not result:
            raise RuntimeError(
                "La base de données n'est pas initialisée ou la table 'users' est manquante."
                " Exécutez schema.sql ou initialisez la base avant de lancer ce script."
            )
    except OperationalError as exc:
        raise RuntimeError(
            "Impossible de se connecter à la base de données. Vérifiez DATABASE_URL et l'accès à PostgreSQL."
        ) from exc
    finally:
        db.close()


def cleanup_test_data():
    db = SessionLocal()
    try:
        initialized = db.execute(text("SELECT to_regclass('public.users')")).scalar()
        if not initialized:
            print("✓ Cleanup skipped: la base de données n'est pas initialisée")
            return

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
            print("✓ Cleanup: données de test supprimées")
        else:
            print("✓ Cleanup: aucune donnée de test trouvée")
    except Exception as exc:
        print(f"✗ Cleanup failed: {exc}")
        db.rollback()
    finally:
        db.close()


def create_test_user(suffix: str, field_of_study: str, level: str) -> dict:
    email = f"{TEST_PREFIX}_{suffix}@example.com"
    phone_number = f"+2299000{random.randint(1000, 9999):04d}"
    payload = {
        "first_name": suffix.capitalize(),
        "last_name": "RouteTest",
        "email": email,
        "phone_number": phone_number,
        "password": PASSWORD,
        "field_of_study": field_of_study,
        "level": level,
        "bio": "Utilisateur de test pour les routes API",
    }
    response = client.post("/api/auth/register", json=payload)
    assert_status_code(response, 201, "/api/auth/register")
    data = response.json()
    print(f"✓ Registered user {email}")
    return {"email": email, "token": data["access_token"], "id": data["user"]["id"]}


def login_user(email: str) -> str:
    response = client.post("/api/auth/login", json={"email": email, "password": PASSWORD})
    assert_status_code(response, 200, "/api/auth/login")
    token = response.json()["access_token"]
    print(f"✓ Logged in {email}")
    return token


def get_skills() -> list[dict]:
    response = client.get("/api/skills")
    assert_status_code(response, 200, "/api/skills")
    return response.json()


def get_skill_by_id(skill_id: int) -> dict:
    response = client.get(f"/api/skills/{skill_id}")
    assert_status_code(response, 200, f"/api/skills/{skill_id}")
    return response.json()


def run() -> None:
    print("=== Test des routes API IFRI_MentorLink ===")

    try:
        ensure_db_ready()
    except RuntimeError as exc:
        print(f"✗ Précondition DB non satisfaite : {exc}")
        return

    cleanup_test_data()

    # Créer deux utilisateurs tests
    user1 = create_test_user("user1", "IA", "L1")
    user2 = create_test_user("user2", "IA", "L1")

    # Login requis pour obtenir des jetons
    user1["token"] = login_user(user1["email"])
    user2["token"] = login_user(user2["email"])

    # Auth routes
    response = client.post(
        "/api/auth/reset-password",
        json={"email": user1["email"]},
    )
    assert_status_code(response, 200, "/api/auth/reset-password")
    print("✓ /api/auth/reset-password")

    response = client.get(
        "/api/auth/me",
        headers=auth_headers(user1["token"]),
    )
    assert_status_code(response, 200, "/api/auth/me")
    print("✓ /api/auth/me")

    # User routes
    response = client.get(
        "/api/users/me",
        headers=auth_headers(user1["token"]),
    )
    assert_status_code(response, 200, "/api/users/me")
    print("✓ GET /api/users/me")

    response = client.put(
        "/api/users/me",
        headers=auth_headers(user1["token"]),
        json={"first_name": "Route1", "bio": "Profil mis à jour"},
    )
    assert_status_code(response, 200, "/api/users/me PUT")
    print("✓ PUT /api/users/me")

    skills = get_skills()
    if not skills:
        raise RuntimeError("Aucune compétence disponible pour les tests")
    skill_id = skills[0]["id"]
    get_skill_by_id(skill_id)
    print("✓ GET /api/skills/{id}")

    response = client.post(
        "/api/users/me/skills",
        headers=auth_headers(user1["token"]),
        json={"skill_id": skill_id, "proficiency": "weak"},
    )
    assert_status_code(response, 201, "/api/users/me/skills")
    print("✓ POST /api/users/me/skills")

    response = client.post(
        "/api/users/me/availabilities",
        headers=auth_headers(user1["token"]),
        json={"day_of_week": "Monday", "start_time": "10:00", "end_time": "12:00"},
    )
    assert_status_code(response, 201, "/api/users/me/availabilities")
    availability_id = response.json()["id"]
    print("✓ POST /api/users/me/availabilities")

    response = client.get(
        "/api/users/me/availabilities",
        headers=auth_headers(user1["token"]),
    )
    assert_status_code(response, 200, "GET /api/users/me/availabilities")
    print("✓ GET /api/users/me/availabilities")

    response = client.delete(
        f"/api/users/me/availabilities/{availability_id}",
        headers=auth_headers(user1["token"]),
    )
    assert_status_code(response, 200, f"DELETE /api/users/me/availabilities/{availability_id}")
    print("✓ DELETE /api/users/me/availabilities/{id}")

    response = client.delete(
        f"/api/users/me/skills/{skill_id}",
        headers=auth_headers(user1["token"]),
    )
    assert_status_code(response, 200, f"DELETE /api/users/me/skills/{skill_id}")
    print("✓ DELETE /api/users/me/skills/{id}")

    # Recréer les éléments requis pour les matches et le chat
    response = client.post(
        "/api/users/me/skills",
        headers=auth_headers(user1["token"]),
        json={"skill_id": skill_id, "proficiency": "weak"},
    )
    assert_status_code(response, 201, "POST /api/users/me/skills user1")
    response = client.post(
        "/api/users/me/skills",
        headers=auth_headers(user2["token"]),
        json={"skill_id": skill_id, "proficiency": "strong"},
    )
    assert_status_code(response, 201, "POST /api/users/me/skills user2")

    response = client.post(
        "/api/users/me/availabilities",
        headers=auth_headers(user2["token"]),
        json={"day_of_week": "Monday", "start_time": "11:00", "end_time": "13:00"},
    )
    assert_status_code(response, 201, "POST /api/users/me/availabilities user2")
    print("✓ Recréation des données utilisateur pour matching")

    # Posts routes
    post_payload = {
        "type": "request",
        "skill_id": skill_id,
        "mode": "online",
        "description": "Recherche mentorat en Python",
        "availabilities": [
            {"day_of_week": "Monday", "start_time": "10:00", "end_time": "12:00"}
        ],
    }
    response = client.post(
        "/api/posts",
        headers=auth_headers(user1["token"]),
        json=post_payload,
    )
    assert_status_code(response, 201, "/api/posts")
    post_id = response.json()["id"]
    print("✓ POST /api/posts")

    response = client.get(
        "/api/posts",
        headers=auth_headers(user1["token"]),
    )
    assert_status_code(response, 200, "/api/posts GET")
    print("✓ GET /api/posts")

    response = client.get(
        f"/api/posts/{post_id}",
        headers=auth_headers(user1["token"]),
    )
    assert_status_code(response, 200, f"GET /api/posts/{post_id}")
    print("✓ GET /api/posts/{id}")

    response = client.put(
        f"/api/posts/{post_id}",
        headers=auth_headers(user1["token"]),
        json={"mode": "both", "description": "Post mis à jour"},
    )
    assert_status_code(response, 200, f"PUT /api/posts/{post_id}")
    print("✓ PUT /api/posts/{id}")

    response = client.delete(
        f"/api/posts/{post_id}",
        headers=auth_headers(user1["token"]),
    )
    assert_status_code(response, 200, f"DELETE /api/posts/{post_id}")
    print("✓ DELETE /api/posts/{id}")

    # Matches routes
    response = client.get(
        "/api/matches",
        headers=auth_headers(user1["token"]),
    )
    assert_status_code(response, 200, "/api/matches")
    matches = response.json().get("matches", [])
    if not matches:
        raise AssertionError("Aucun match trouvé par /api/matches")
    match_id = matches[0]["id"]
    print("✓ GET /api/matches")

    response = client.put(
        f"/api/matches/{match_id}/accept",
        headers=auth_headers(user1["token"]),
    )
    assert_status_code(response, 200, f"PUT /api/matches/{match_id}/accept")
    conversation_id = response.json()["conversation_id"]
    print("✓ PUT /api/matches/{id}/accept")

    # Create a second pending match to test rejection
    db = SessionLocal()
    try:
        reject_match = create_match_record(
            db,
            mentor_id=user2["id"],
            mentee_id=user1["id"],
            skill_id=skill_id,
            score=45.0,
            status="pending",
        )
        reject_match_id = reject_match.id
    finally:
        db.close()

    response = client.put(
        f"/api/matches/{reject_match_id}/reject",
        headers=auth_headers(user1["token"]),
    )
    assert_status_code(response, 200, f"PUT /api/matches/{reject_match_id}/reject")
    print("✓ PUT /api/matches/{id}/reject")

    # Chat routes
    response = client.get(
        "/api/conversations",
        headers=auth_headers(user1["token"]),
    )
    assert_status_code(response, 200, "/api/conversations")
    conversations = response.json().get("conversations", [])
    if not conversations:
        raise AssertionError("Aucune conversation trouvée après acceptation du match")
    print("✓ GET /api/conversations")

    response = client.get(
        f"/api/conversations/{conversation_id}/messages",
        headers=auth_headers(user1["token"]),
    )
    assert_status_code(response, 200, f"GET /api/conversations/{conversation_id}/messages")
    print("✓ GET /api/conversations/{conversation_id}/messages")

    response = client.post(
        f"/api/conversations/{conversation_id}/messages",
        headers=auth_headers(user1["token"]),
        json={"content": "Bonjour, voici un message de test."},
    )
    assert_status_code(response, 201, f"POST /api/conversations/{conversation_id}/messages")
    message_id = response.json()["id"]
    print("✓ POST /api/conversations/{conversation_id}/messages")

    response = client.get(
        f"/api/conversations/{conversation_id}/messages",
        headers=auth_headers(user1["token"]),
    )
    assert_status_code(response, 200, f"GET /api/conversations/{conversation_id}/messages after send")
    print("✓ GET /api/conversations/{conversation_id}/messages après envoi")

    response = client.put(
        f"/api/messages/{message_id}/read",
        headers=auth_headers(user2["token"]),
    )
    assert_status_code(response, 200, f"PUT /api/messages/{message_id}/read")
    print("✓ PUT /api/messages/{id}/read")

    print("\n=== Tous les tests de route ont réussi ===")


if __name__ == "__main__":
    try:
        run()
    finally:
        cleanup_test_data()
