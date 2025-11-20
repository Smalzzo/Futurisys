"""Tests pour la configuration"""
from app.core.config import get_settings, Settings


def test_get_settings_singleton():
    """Test que get_settings retourne toujours la même instance"""
    settings1 = get_settings()
    settings2 = get_settings()
    assert settings1 is settings2


def test_settings_has_required_fields():
    """Test que Settings a les champs requis"""
    settings = get_settings()
    assert hasattr(settings, "API_KEY")
    assert hasattr(settings, "DATABASE_URL")
