# ============================================================
# IFRI_MentorLink — Test Script pour les Models SQLAlchemy
# backend/test_models.py
# ============================================================

from database import SessionLocal
from models import User, Skill, MentorshipPost, Match, Conversation, Message

def test_get_or_create_user(
    first_name: str = "John",
    last_name: str = "Doe",
    email: str = "john.doe@test.com",
    phone_number: str = "+22990000001",
    field_of_study: str = "IA",
    level: str = "L1",
    bio: str = "Étudiant en IA passionné par Python",
):
    """Test: Récupérer un utilisateur par email ou en créer un nouveau."""
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.email == email).first()
        if user:
            print(f"✓ User existant utilisé: ID={user.id}, {user.first_name} {user.last_name}, {user.email}")
            return user.id

        user = User(
            first_name=first_name,
            last_name=last_name,
            email=email,
            phone_number=phone_number,
            password_hash="$2b$12$hashed_password_example",
            field_of_study=field_of_study,
            level=level,
            bio=bio,
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        print(f"✓ User créé: ID={user.id}, {user.first_name} {user.last_name}, {user.email}")
        return user.id
    except Exception as e:
        print(f"✗ Erreur création user: {e}")
        db.rollback()
        return None
    finally:
        db.close()


def test_get_or_create_skill(skill_name: str = "Algorithmique"):
    """Test: Récupérer une compétence existante ou en créer une nouvelle"""
    db = SessionLocal()
    try:
        # Chercher si la compétence existe déjà
        skill = db.query(Skill).filter(Skill.name == skill_name).first()
        if skill:
            print(f"✓ Skill existant utilisé: ID={skill.id}, {skill.name}")
            return skill.id
        
        # Sinon, créer une nouvelle compétence
        skill = Skill(name=skill_name)
        db.add(skill)
        db.commit()
        db.refresh(skill)
        print(f"✓ Skill créé: ID={skill.id}, {skill.name}")
        return skill.id
    except Exception as e:
        print(f"✗ Erreur skill: {e}")
        db.rollback()
        return None
    finally:
        db.close()


def test_create_mentorship_post(user_id: int, skill_id: int):
    """Test: Créer un post de mentorat"""
    db = SessionLocal()
    try:
        post = MentorshipPost(
            user_id=user_id,
            type="offer",
            skill_id=skill_id,
            mode="online",
            description="Je peux aider en Python, disponible le soir"
        )
        db.add(post)
        db.commit()
        db.refresh(post)
        print(f"✓ Post créé: ID={post.id}, type={post.type}, skill_id={post.skill_id}")
        return post.id
    except Exception as e:
        print(f"✗ Erreur création post: {e}")
        db.rollback()
        return None
    finally:
        db.close()


def test_create_match(mentor_id: int, mentee_id: int, skill_id: int):
    """Test: Créer un match"""
    db = SessionLocal()
    try:
        match = Match(
            mentor_id=mentor_id,
            mentee_id=mentee_id,
            skill_id=skill_id,
            score=75.50,
            status="pending"
        )
        db.add(match)
        db.commit()
        db.refresh(match)
        print(f"✓ Match créé: ID={match.id}, mentor={match.mentor_id}, mentee={match.mentee_id}, score={match.score}")
        return match.id
    except Exception as e:
        print(f"✗ Erreur création match: {e}")
        db.rollback()
        return None
    finally:
        db.close()


def test_create_conversation(match_id: int):
    """Test: Créer une conversation"""
    db = SessionLocal()
    try:
        conversation = Conversation(match_id=match_id)
        db.add(conversation)
        db.commit()
        db.refresh(conversation)
        print(f"✓ Conversation créée: ID={conversation.id}, match_id={conversation.match_id}")
        return conversation.id
    except Exception as e:
        print(f"✗ Erreur création conversation: {e}")
        db.rollback()
        return None
    finally:
        db.close()


def test_create_message(conversation_id: int, sender_id: int):
    """Test: Créer un message"""
    db = SessionLocal()
    try:
        message = Message(
            conversation_id=conversation_id,
            sender_id=sender_id,
            content="Bonjour, je suis intéressé par ton offre de mentorat!"
        )
        db.add(message)
        db.commit()
        db.refresh(message)
        print(f"✓ Message créé: ID={message.id}, sender={message.sender_id}, content={message.content[:30]}...")
        return message.id
    except Exception as e:
        print(f"✗ Erreur création message: {e}")
        db.rollback()
        return None
    finally:
        db.close()


def test_read_all():
    """Test: Lire toutes les données"""
    db = SessionLocal()
    try:
        # Lire les utilisateurs
        users = db.query(User).all()
        print(f"\n📋 Utilisateurs ({len(users)}):")
        for u in users:
            print(f"  - ID={u.id}: {u.first_name} {u.last_name} ({u.email})")

        # Lire les compétences
        skills = db.query(Skill).all()
        print(f"\n📋 Compétences ({len(skills)}):")
        for s in skills:
            print(f"  - ID={s.id}: {s.name}")

        # Lire les posts
        posts = db.query(MentorshipPost).all()
        print(f"\n📋 Posts de mentorat ({len(posts)}):")
        for p in posts:
            print(f"  - ID={p.id}: type={p.type}, skill_id={p.skill_id}")

        # Lire les matches
        matches = db.query(Match).all()
        print(f"\n📋 Matches ({len(matches)}):")
        for m in matches:
            print(f"  - ID={m.id}: mentor={m.mentor_id}, mentee={m.mentee_id}, score={m.score}, status={m.status}")

    except Exception as e:
        print(f"✗ Erreur lecture: {e}")
    finally:
        db.close()


def cleanup_test_data():
    """Nettoyer les données de test"""
    db = SessionLocal()
    try:
        # Supprimer dans l'ordre inverse des dépendances
        db.query(Message).delete()
        db.query(Conversation).delete()
        db.query(Match).delete()
        db.query(MentorshipPost).delete()
        db.query(User).delete()
        # On garde les skills car ils sont des données de référence
        db.commit()
        print("✓ Données de test supprimées")
    except Exception as e:
        print(f"✗ Erreur cleanup: {e}")
        db.rollback()
    finally:
        db.close()


def run_all_tests():
    """Exécuter tous les tests"""
    print("=" * 60)
    print("🧪 TESTS DES MODÈLES SQLAlchemy - IFRI_MentorLink")
    print("=" * 60)

    # Test 1: Créer ou récupérer un utilisateur
    user_id = test_get_or_create_user()
    if not user_id:
        print("Arrêt: impossible de créer ou récupérer l'utilisateur")
        return

    # Test 2: Récupérer ou créer une compétence
    skill_id = test_get_or_create_skill()
    if not skill_id:
        print("Arrêt: impossible d'obtenir la compétence")
        return

    # Test 3: Récupérer ou créer un deuxième utilisateur pour le match
    user2_id = test_get_or_create_user(
        first_name="Jane",
        last_name="Smith",
        email="jane.smith@test.com",
        phone_number="+22990000002",
        field_of_study="GL",
        level="L2",
    )
    if not user2_id:
        print("⚠️ Impossible de créer ou récupérer le deuxième utilisateur, on réutilise le premier.")
        user2_id = user_id

    # Test 4: Créer un post
    post_id = test_create_mentorship_post(user_id, skill_id)

    # Test 5: Créer un match
    match_id = test_create_match(user_id, user2_id, skill_id)

    # Test 6: Créer une conversation
    if match_id:
        conv_id = test_create_conversation(match_id)

        # Test 7: Créer un message
        if conv_id:
            test_create_message(conv_id, user_id)

    # Test 8: Lire toutes les données
    test_read_all()

    print("\n" + "=" * 60)
    print("✅ TOUS LES TESTS TERMINÉS")
    print("=" * 60)

    # Optionnel: nettoyer les données de test
    # cleanup_test_data()


if __name__ == "__main__":
    run_all_tests()