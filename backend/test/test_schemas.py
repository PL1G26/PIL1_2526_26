"""
Script de test pour les schémas Pydantic.
Teste la validation des données pour chaque schéma.
"""
import sys
import os
# Ajoute backend/ au sys.path → permet d'importer schemas, etc.
# Fonctionne que le script soit lancé avec pytest OU python3 directement.
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from datetime import datetime, time
from pydantic import ValidationError

# Import des schémas
from schemas.auth_schema import (
    RegisterRequest, LoginRequest, TokenResponse, ResetPasswordRequest
)
from schemas.user_schema import (
    UserProfileResponse, UpdateProfileRequest, AddSkillRequest,
    AddAvailabilityRequest, SkillResponse, UserSkillResponse, AvailabilityResponse
)
from schemas.post_schema import (
    PostResponse, CreatePostRequest, UpdatePostRequest,
    PostAvailabilityResponse, SkillBasicResponse, UserBasicResponse
)
from schemas.match_schema import (
    MatchResponse, MatchListResponse, AcceptMatchResponse, RejectMatchResponse
)
from schemas.message_schema import (
    MessageResponse, SendMessageRequest, MessageListResponse,
    ConversationResponse, ConversationListResponse, MarkReadResponse
)


def test_auth_schemas():
    """Test les schémas d'authentification."""
    print("\n📋 Test auth_schema...")
    
    # Test RegisterRequest - valide
    try:
        data = RegisterRequest(
            first_name="Jean",
            last_name="Dupont",
            email="jean.dupont@email.com",
            phone_number="+22912345678",
            password="password123",
            field_of_study="IA",
            level="L1"
        )
        print("  ✓ RegisterRequest valide")
    except ValidationError as e:
        print(f"  ✗ RegisterRequest invalide: {e}")
        return False
    
    # Test RegisterRequest - email invalide
    try:
        data = RegisterRequest(
            first_name="Jean",
            last_name="Dupont",
            email="invalid-email",
            phone_number="+22912345678",
            password="password123",
            field_of_study="IA",
            level="L1"
        )
        print("  ✗ RegisterRequest devrait rejeter email invalide")
        return False
    except ValidationError:
        print("  ✓ RegisterRequest rejette email invalide")
    
    # Test RegisterRequest - filière invalide
    try:
        data = RegisterRequest(
            first_name="Jean",
            last_name="Dupont",
            email="jean@email.com",
            phone_number="+22912345678",
            password="password123",
            field_of_study="INVALID",
            level="L1"
        )
        print("  ✗ RegisterRequest devrait rejeter filière invalide")
        return False
    except ValidationError:
        print("  ✓ RegisterRequest rejette filière invalide")
    
    # Test LoginRequest
    try:
        data = LoginRequest(email="jean@email.com", password="password123")
        print("  ✓ LoginRequest valide")
    except ValidationError as e:
        print(f"  ✗ LoginRequest invalide: {e}")
        return False
    
    # Test TokenResponse
    try:
        data = TokenResponse(
            access_token="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
            user={"id": 1, "name": "Jean"}
        )
        print("  ✓ TokenResponse valide")
    except ValidationError as e:
        print(f"  ✗ TokenResponse invalide: {e}")
        return False
    
    # Test ResetPasswordRequest
    try:
        data = ResetPasswordRequest(email="jean@email.com")
        print("  ✓ ResetPasswordRequest valide")
    except ValidationError as e:
        print(f"  ✗ ResetPasswordRequest invalide: {e}")
        return False
    
    return True


def test_user_schemas():
    """Test les schémas utilisateur."""
    print("\n👤 Test user_schema...")
    
    # Test AddSkillRequest
    try:
        data = AddSkillRequest(skill_id=1, proficiency="strong")
        print("  ✓ AddSkillRequest (strong) valide")
    except ValidationError as e:
        print(f"  ✗ AddSkillRequest invalide: {e}")
        return False
    
    # Test AddSkillRequest - proficiency invalide
    try:
        data = AddSkillRequest(skill_id=1, proficiency="invalid")
        print("  ✗ AddSkillRequest devrait rejeter proficiency invalide")
        return False
    except ValidationError:
        print("  ✓ AddSkillRequest rejette proficiency invalide")
    
    # Test AddAvailabilityRequest
    try:
        data = AddAvailabilityRequest(
            day_of_week="Monday",
            start_time="14:00",
            end_time="17:00"
        )
        print("  ✓ AddAvailabilityRequest valide")
    except ValidationError as e:
        print(f"  ✗ AddAvailabilityRequest invalide: {e}")
        return False
    
    # Test AddAvailabilityRequest - jour invalide
    try:
        data = AddAvailabilityRequest(
            day_of_week="InvalidDay",
            start_time="14:00",
            end_time="17:00"
        )
        print("  ✗ AddAvailabilityRequest devrait rejeter jour invalide")
        return False
    except ValidationError:
        print("  ✓ AddAvailabilityRequest rejette jour invalide")
    
    # Test UpdateProfileRequest
    try:
        data = UpdateProfileRequest(
            first_name="Jean",
            bio="Étudiant en IA"
        )
        print("  ✓ UpdateProfileRequest valide")
    except ValidationError as e:
        print(f"  ✗ UpdateProfileRequest invalide: {e}")
        return False
    
    return True


def test_post_schemas():
    """Test les schémas de posts."""
    print("\n📝 Test post_schema...")
    
    # Test CreatePostRequest - offer
    try:
        data = CreatePostRequest(
            type="offer",
            skill_id=1,
            mode="online",
            description="Je peux aider en Python"
        )
        print("  ✓ CreatePostRequest (offer) valide")
    except ValidationError as e:
        print(f"  ✗ CreatePostRequest invalide: {e}")
        return False
    
    # Test CreatePostRequest - request
    try:
        data = CreatePostRequest(
            type="request",
            skill_id=2,
            mode="both"
        )
        print("  ✓ CreatePostRequest (request) valide")
    except ValidationError as e:
        print(f"  ✗ CreatePostRequest invalide: {e}")
        return False
    
    # Test CreatePostRequest - type invalide
    try:
        data = CreatePostRequest(
            type="invalid",
            skill_id=1,
            mode="online"
        )
        print("  ✗ CreatePostRequest devrait rejeter type invalide")
        return False
    except ValidationError:
        print("  ✓ CreatePostRequest rejette type invalide")
    
    # Test CreatePostRequest - mode invalide
    try:
        data = CreatePostRequest(
            type="offer",
            skill_id=1,
            mode="invalid_mode"
        )
        print("  ✗ CreatePostRequest devrait rejeter mode invalide")
        return False
    except ValidationError:
        print("  ✓ CreatePostRequest rejette mode invalide")
    
    # Test UpdatePostRequest
    try:
        data = UpdatePostRequest(
            skill_id=2,
            is_active=False
        )
        print("  ✓ UpdatePostRequest valide")
    except ValidationError as e:
        print(f"  ✗ UpdatePostRequest invalide: {e}")
        return False
    
    return True


def test_match_schemas():
    """Test les schémas de matching."""
    print("\n🔗 Test match_schema...")
    
    # Test AcceptMatchResponse
    try:
        data = AcceptMatchResponse(
            message="Match accepté!",
            match_id=1,
            conversation_id=1
        )
        print("  ✓ AcceptMatchResponse valide")
    except ValidationError as e:
        print(f"  ✗ AcceptMatchResponse invalide: {e}")
        return False
    
    # Test RejectMatchResponse
    try:
        data = RejectMatchResponse(
            message="Match refusé",
            match_id=1
        )
        print("  ✓ RejectMatchResponse valide")
    except ValidationError as e:
        print(f"  ✗ RejectMatchResponse invalide: {e}")
        return False
    
    return True


def test_message_schemas():
    """Test les schémas de messagerie."""
    print("\n💬 Test message_schema...")
    
    # Test SendMessageRequest
    try:
        data = SendMessageRequest(content="Bonjour! Comment ça va?")
        print("  ✓ SendMessageRequest valide")
    except ValidationError as e:
        print(f"  ✗ SendMessageRequest invalide: {e}")
        return False
    
    # Test SendMessageRequest - contenu vide
    try:
        data = SendMessageRequest(content="")
        print("  ✗ SendMessageRequest devrait rejeter contenu vide")
        return False
    except ValidationError:
        print("  ✓ SendMessageRequest rejette contenu vide")
    
    # Test MarkReadResponse
    try:
        data = MarkReadResponse(
            message="Messages marqués comme lus",
            messages_marked_read=5
        )
        print("  ✓ MarkReadResponse valide")
    except ValidationError as e:
        print(f"  ✗ MarkReadResponse invalide: {e}")
        return False
    
    return True


def test_edge_cases():
    """Test les cas limites."""
    print("\n⚡ Test cas limites...")
    
    # Test mot de passe minimal
    try:
        data = RegisterRequest(
            first_name="A",
            last_name="B",
            email="a@b.com",
            phone_number="1",
            password="123456",  # 6 caractères minimum
            field_of_study="IA",
            level="L1"
        )
        print("  ✓ Mot de passe minimal (6 caractères) accepté")
    except ValidationError:
        print("  ✗ Mot de passe minimal devrait être accepté")
        return False
    
    # Test mot de passe trop court
    try:
        data = RegisterRequest(
            first_name="A",
            last_name="B",
            email="a@b.com",
            phone_number="1",
            password="12345",  # 5 caractères - trop court
            field_of_study="IA",
            level="L1"
        )
        print("  ✗ Mot de passe trop court devrait être rejeté")
        return False
    except ValidationError:
        print("  ✓ Mot de passe trop court rejeté")
    
    # Test tous les niveaux
    valid_levels = ["L1", "L2", "L3", "M1", "M2"]
    for level in valid_levels:
        try:
            data = RegisterRequest(
                first_name="Test",
                last_name="User",
                email="test@test.com",
                phone_number="+22900000000",
                password="password123",
                field_of_study="IA",
                level=level
            )
        except ValidationError:
            print(f"  ✗ Niveau {level} devrait être accepté")
            return False
    print("  ✓ Tous les niveaux acceptés (L1-L2-L3-M1-M2)")
    
    # Test toutes les filières
    valid_fields = ["IA", "IM", "GL", "SE&IoT", "SI"]
    for field in valid_fields:
        try:
            data = RegisterRequest(
                first_name="Test",
                last_name="User",
                email="test@test.com",
                phone_number="+22900000000",
                password="password123",
                field_of_study=field,
                level="L1"
            )
        except ValidationError:
            print(f"  ✗ Filière {field} devrait être acceptée")
            return False
    print("  ✓ Toutes les filières acceptées (IA, IM, GL, SE&IoT, SI)")
    
    return True


def main():
    """Exécute tous les tests."""
    print("=" * 60)
    print("🧪 TEST DES SCHÉMAS PYDANTIC - IFRI_MentorLink")
    print("=" * 60)
    
    all_passed = True
    
    # Exécution des tests
    tests = [
        ("Auth Schemas", test_auth_schemas),
        ("User Schemas", test_user_schemas),
        ("Post Schemas", test_post_schemas),
        ("Match Schemas", test_match_schemas),
        ("Message Schemas", test_message_schemas),
        ("Edge Cases", test_edge_cases),
    ]
    
    for name, test_func in tests:
        try:
            if not test_func():
                all_passed = False
        except Exception as e:
            print(f"\n  ✗ Erreur inattendue: {e}")
            all_passed = False
    
    # Résumé
    print("\n" + "=" * 60)
    if all_passed:
        print("✅ TOUS LES TESTS ONT RÉUSSI!")
    else:
        print("❌ CERTAINS TESTS ONT ÉCHOUÉ!")
    print("=" * 60)
    
    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())