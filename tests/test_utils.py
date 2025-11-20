"""Tests pour les utilitaires et helpers"""
import pytest
from fastapi import HTTPException
from app.api.deps import get_api_key


def test_get_api_key_with_valid_key(monkeypatch):
    """Test que get_api_key accepte une clé valide"""
    monkeypatch.setenv("API_KEY", "secret-key")
    result = get_api_key("secret-key")
    assert result == "secret-key"


def test_get_api_key_with_invalid_key_raises(monkeypatch):
    """Test que get_api_key rejette une clé invalide"""
    monkeypatch.setenv("API_KEY", "secret-key")
    with pytest.raises(HTTPException) as exc_info:
        get_api_key("wrong-key")
    assert exc_info.value.status_code == 401


def test_get_api_key_with_none_raises(monkeypatch):
    """Test que get_api_key rejette None quand une clé est configurée"""
    monkeypatch.setenv("API_KEY", "secret-key")
    with pytest.raises(HTTPException) as exc_info:
        get_api_key(None)
    assert exc_info.value.status_code == 401


def test_get_api_key_fallback_to_settings(monkeypatch):
    """Test que get_api_key utilise settings si API_KEY env var n'est pas définie"""
    # Supprimer API_KEY de l'environnement
    monkeypatch.delenv("API_KEY", raising=False)
    # Cela va utiliser get_settings().API_KEY
    # Dans les tests, PYTEST_CURRENT_TEST est défini donc ça va utiliser "test-key"
    result = get_api_key("test-key")
    assert result == "test-key"
