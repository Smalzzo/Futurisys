import os
from fastapi.testclient import TestClient

# petit module de test pour l'API
# on fait des tests simple: health, securité (api key), et predict


    # on prepare un client pour tester l'appli
    # on evite d'utiliser un vrai model: on monkeypatch les fonctions
def _client(monkeypatch) -> TestClient:
    os.environ.setdefault("API_KEY", "test-key")
    
    from app.ml import serve as serve_mod
    monkeypatch.setattr(serve_mod.model_service, "load", lambda: None, raising=False)    
    monkeypatch.setattr(serve_mod.model_service, "predict_proba", lambda payload: serve_mod.SEUIL_FIXE, raising=False)
    from app.main import app
    return TestClient(app)

  # test basique: la route health doit repondre ok
def test_health(monkeypatch):
  
    client = _client(monkeypatch)
    r = client.get("/api/v1/health")
    assert r.status_code == 200
    assert r.json()["status Api"] == "ok"

    # on envoi un payload minimum (avec id obligatoire)
    # et on verifie qu'on recoit bien une proba
def test_predict_success_minimal_payload(monkeypatch):
    client = _client(monkeypatch)
    headers = {"x-api-key": "test-key"}
    payload = {"id_employee": 1, "age": 30}
    r = client.post("/api/v1/predict", json=payload, headers=headers)
    assert r.status_code == 200
    body = r.json()
    assert "pred_quitte_entreprise" in body
    assert body["pred_quitte_entreprise"] in {"OUI", "NON"}

# pas de header -> doit renvoyer 401 (non authorisé)
def test_predict_missing_api_key_returns_401(monkeypatch):    
    client = _client(monkeypatch)
    r = client.post("/api/v1/predict", json={"id_employee": 1, "age": 30})
    assert r.status_code == 401

# mauvaise clef api -> 401 aussi (refus)
def test_predict_wrong_api_key_returns_401(monkeypatch):    
    client = _client(monkeypatch)
    headers = {"x-api-key": "wrong-key"}
    r = client.post("/api/v1/predict", json={"id_employee": 1, "age": 30}, headers=headers)
    assert r.status_code == 401

# pas d'id_employee -> la validation pydantic doit echouer (422)
def test_predict_rejects_empty_payload_without_id_employee(monkeypatch):    
    client = _client(monkeypatch)
    headers = {"x-api-key": "test-key"}
    r = client.post("/api/v1/predict", json={}, headers=headers)
    assert r.status_code == 422
