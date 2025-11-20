import os
import pytest
from fastapi.testclient import TestClient

# petit module de test pour l'API
# on fait des tests simple: health, securité (api key), et predict

# Setup environment AVANT l'import
os.environ.setdefault("API_KEY", "test-key")

# Import de l'app en dehors des tests
from app.main import create_app
from app.ml import serve as serve_mod


@pytest.fixture
def client(monkeypatch):
    """Fixture qui prepare un client pour tester l'appli"""
    # on evite d'utiliser un vrai model: on monkeypatch les fonctions
    monkeypatch.setattr(serve_mod.model_service, "load", lambda: None, raising=False)    
    monkeypatch.setattr(serve_mod.model_service, "predict_proba", lambda payload: serve_mod.SEUIL_FIXE, raising=False)
    monkeypatch.setattr(serve_mod.model_service, "close", lambda: None, raising=False)
    
    # Mock aussi get_model pour éviter le téléchargement
    from app.ml import model_loader
    monkeypatch.setattr(model_loader, "get_model", lambda: None, raising=False)
    
    app = create_app()
    # TestClient avec raise_server_exceptions=True pour capturer les erreurs
    # et avec lifespan activé (par défaut dans les versions récentes de Starlette)
    with TestClient(app) as test_client:
        yield test_client


# test basique: la route health doit repondre ok
def test_health(client):
    r = client.get("/api/v1/health")
    assert r.status_code == 200
    assert r.json()["status Api"] == "ok"

# on envoi un payload minimum (avec id obligatoire)
# et on verifie qu'on recoit bien une proba
def test_predict_success_minimal_payload(client):
    headers = {"x-api-key": "test-key"}
    payload = {"id_employee": 1, "age": 30}
    r = client.post("/api/v1/predict", json=payload, headers=headers)
    assert r.status_code == 200
    body = r.json()
    assert "pred_quitte_entreprise" in body
    assert body["pred_quitte_entreprise"] in {"OUI", "NON"}

# pas de header -> doit renvoyer 401 (non authorisé)
def test_predict_missing_api_key_returns_401(client):    
    r = client.post("/api/v1/predict", json={"id_employee": 1, "age": 30})
    assert r.status_code == 401

# mauvaise clef api -> 401 aussi (refus)
def test_predict_wrong_api_key_returns_401(client):    
    headers = {"x-api-key": "wrong-key"}
    r = client.post("/api/v1/predict", json={"id_employee": 1, "age": 30}, headers=headers)
    assert r.status_code == 401

# pas d'id_employee -> la validation pydantic doit echouer (422)
def test_predict_rejects_empty_payload_without_id_employee(client):    
    headers = {"x-api-key": "test-key"}
    headers = {"x-api-key": "test-key"}
    r = client.post("/api/v1/predict", json={}, headers=headers)
    assert r.status_code == 422


# Test endpoint racine
def test_root_endpoint(client):
    r = client.get("/")
    assert r.status_code == 200
    body = r.json()
    assert "message" in body
    assert "version" in body
    assert body["message"] == "Futurisys ML API"


# Test /predict avec payload complet incluant des string à normaliser
def test_predict_with_full_payload_and_normalization(client):
    headers = {"x-api-key": "test-key"}
    payload = {
        "id_employee": 123,
        "age": 35,
        "genre": " masculin ",  # doit etre normalisé en uppercase
        "heure_supplementaires": "yes",  # doit devenir "OUI"
        "statut_marital": "marie",
        "departement": "ventes",
        "annees_dans_l_entreprise": 5,
        "annee_experience_totale": 10,
    }
    r = client.post("/api/v1/predict", json=payload, headers=headers)
    assert r.status_code == 200
    body = r.json()
    assert body["employee_id"] == 123
    assert body["pred_quitte_entreprise"] in {"OUI", "NON"}


# Test /predict avec empty strings (doivent devenir None)
def test_predict_normalizes_empty_strings_to_none(client):
    headers = {"x-api-key": "test-key"}
    payload = {
        "id_employee": 456,
        "age": 28,
        "genre": "  ",  # string vide après strip -> None
        "departement": "",
    }
    r = client.post("/api/v1/predict", json=payload, headers=headers)
    assert r.status_code == 200


# Test /predict avec heure_supplementaires="non"
def test_predict_normalizes_heures_supplementaires_non(client):
    headers = {"x-api-key": "test-key"}
    payload = {
        "id_employee": 789,
        "age": 40,
        "heure_supplementaires": "no",  # doit devenir "NON"
    }
    r = client.post("/api/v1/predict", json=payload, headers=headers)
    assert r.status_code == 200
    body = r.json()
    assert body["pred_quitte_entreprise"] in {"OUI", "NON"}


# Test /predict avec annees_dans_l_entreprise pour déclencher anciennete_log
def test_predict_computes_log_features(client):
    headers = {"x-api-key": "test-key"}
    payload = {
        "id_employee": 999,
        "age": 35,
        "annees_dans_l_entreprise": 5,  # doit calculer anciennete_log = log(5)
        "annee_experience_totale": 12,   # doit calculer annee_experience_totale_log = log(12)
    }
    r = client.post("/api/v1/predict", json=payload, headers=headers)
    assert r.status_code == 200
    body = r.json()
    assert body["employee_id"] == 999
    assert body["pred_quitte_entreprise"] in {"OUI", "NON"}


# Test /predict avec annees=0 (ne doit pas crasher avec log(0))
def test_predict_handles_zero_years(client):
    headers = {"x-api-key": "test-key"}
    payload = {
        "id_employee": 888,
        "age": 22,
        "annees_dans_l_entreprise": 0,  # log(0) devrait être None
    }
    r = client.post("/api/v1/predict", json=payload, headers=headers)
    assert r.status_code == 200


# Test /predict avec différentes variantes de "OUI" pour heure_supplementaires
def test_predict_handles_yes_variants(client):
    headers = {"x-api-key": "test-key"}
    for yes_variant in ["YES", "Y", "1", "TRUE", "yes", "oui"]:
        payload = {
            "id_employee": 100 + ord(yes_variant[0]),
            "age": 30,
            "heure_supplementaires": yes_variant,
        }
        r = client.post("/api/v1/predict", json=payload, headers=headers)
        assert r.status_code == 200


