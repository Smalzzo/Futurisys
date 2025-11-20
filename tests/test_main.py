"""Tests pour le module principal et le lifespan"""
import pytest
import os
from app.main import create_app, lifespan
from fastapi.testclient import TestClient


def test_create_app_returns_fastapi_instance():
    """Test que create_app retourne une instance FastAPI"""
    app = create_app()
    assert app is not None
    assert hasattr(app, "routes")


def test_app_with_lifespan_startup(monkeypatch, tmp_path):
    """Test que le lifespan s'exécute correctement au démarrage"""
    # Mock pour éviter le vrai modèle
    from app.ml import serve as serve_mod
    from app.ml import model_loader
    
    monkeypatch.setattr(serve_mod.model_service, "load", lambda: None, raising=False)
    monkeypatch.setattr(serve_mod.model_service, "close", lambda: None, raising=False)
    monkeypatch.setattr(model_loader, "get_model", lambda: None, raising=False)
    
    # Mock pour utiliser une DB temporaire
    test_db_path = tmp_path / "test.db"
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{test_db_path}")
    
    # Créer l'app et tester avec TestClient (déclenche lifespan)
    app = create_app()
    with TestClient(app) as client:
        # Le lifespan s'est exécuté, vérifions que l'app fonctionne
        response = client.get("/")
        assert response.status_code == 200


def test_app_handles_missing_model_file(monkeypatch, tmp_path):
    """Test que l'app démarre même si le fichier modèle est manquant"""
    from app.ml import model_loader
    
    # Mock get_model pour ne rien faire
    monkeypatch.setattr(model_loader, "get_model", lambda: None)
    
    # Mock model_service.load pour lever FileNotFoundError
    from app.ml import serve as serve_mod
    def mock_load():
        raise FileNotFoundError("Model not found")
    
    monkeypatch.setattr(serve_mod.model_service, "load", mock_load, raising=False)
    monkeypatch.setattr(serve_mod.model_service, "close", lambda: None, raising=False)
    monkeypatch.setattr(serve_mod.model_service, "predict_proba", lambda p: 0.5, raising=False)
    
    test_db_path = tmp_path / "test.db"
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{test_db_path}")
    
    # L'app doit démarrer quand même (warning dans les logs)
    app = create_app()
    with TestClient(app) as client:
        response = client.get("/api/v1/health")
        assert response.status_code == 200


def test_data_directory_creation(monkeypatch, tmp_path):
    """Test que le répertoire data est créé au démarrage"""
    from app.ml import serve as serve_mod
    from app.ml import model_loader
    
    # Changer vers un dossier temporaire
    original_cwd = os.getcwd()
    try:
        os.chdir(tmp_path)
        
        # Mock les dépendances
        monkeypatch.setattr(serve_mod.model_service, "load", lambda: None, raising=False)
        monkeypatch.setattr(serve_mod.model_service, "close", lambda: None, raising=False)
        monkeypatch.setattr(model_loader, "get_model", lambda: None, raising=False)
        
        # Créer l'app (doit créer ./data)
        app = create_app()
        with TestClient(app):
            # Vérifier que ./data existe
            assert os.path.exists("./data")
    finally:
        os.chdir(original_cwd)
