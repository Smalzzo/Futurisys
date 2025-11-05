import os
import pytest
from fastapi.testclient import TestClient

# petit fichier de tests pour verifier la validation de l'API
# on envoie des payloads pas bon et on attend des erreurs 422




@pytest.fixture
def client(monkeypatch):
    os.environ.setdefault("API_KEY", "test-key")
    # on evite de charger un vrai model (pas besoin ici)
    from app.ml import serve as serve_mod
    monkeypatch.setattr(serve_mod.model_service, "load", lambda: None, raising=False)
    # on fixe la proba a 0.5 (de toute facon on teste la validation)
    monkeypatch.setattr(serve_mod.model_service, "predict_proba", lambda payload: 0.5, raising=False)
    from app.main import app
    return TestClient(app)


headers = {"x-api-key": "test-key"}


# on met un champ inconnu -> doit renvoyer 422
def test_predict_rejects_unknown_field(client):
    r = client.post("/api/v1/predict", json={"id_employee": 1, "age": 30, "revenu_mensuel": 2500}, headers=headers)
    assert r.status_code == 422


# age negatif -> pas logique -> 422
def test_predict_rejects_negative_numeric(client):
    r = client.post("/api/v1/predict", json={"id_employee": 1, "age": -1}, headers=headers)
    assert r.status_code == 422


# la valeur "yes" est normalisee -> OUI -> doit passer
def test_predict_accepts_yes_no_variants(client):
    r = client.post("/api/v1/predict", json={"id_employee": 1, "age": 30, "heure_supplementaires": "yes"}, headers=headers)
    # la validation passe, le model est stubbe donc 200
    assert r.status_code == 200


# valeur inconnue pour heure_supplementaires -> 422
def test_predict_rejects_invalid_heure_supplementaires(client):
    r = client.post("/api/v1/predict", json={"id_employee": 1, "heure_supplementaires": "maybe"}, headers=headers)
    assert r.status_code == 422
