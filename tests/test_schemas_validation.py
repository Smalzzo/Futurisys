import pytest
from pydantic import ValidationError
from app.api.schemas import PredictIn

# petit fichier de tests tres simple
# on verifie que notre schema pydantic se comporte comme on pense

# on essaye d envoyer un champ inconnu -> ça doit casser
def test_unknown_field_forbidden():    
    with pytest.raises(ValidationError):
        PredictIn(id_employee=1, unknown_feature=123) 

# yes devient OUI
# No devient NON
def test_heure_supplementaires_normalization():    
    m = PredictIn(id_employee=1, heure_supplementaires="yes")
    assert m.heure_supplementaires == "OUI"    
    m = PredictIn(id_employee=1, heure_supplementaires="No")
    assert m.heure_supplementaires == "NON"

 # les textes sont mis en MAJ et on strip les espaces
 # une chaine vide ou juste espaces -> None
def test_categorical_uppercased_and_blank_to_none():   
    m = PredictIn(id_employee=1, genre="femme", departement=" data ")
    assert m.genre == "FEMME"
    assert m.departement == "DATA"    
    m2 = PredictIn(id_employee=1, genre="   ")
    assert m2.genre is None

# pourcentage en string est converti en float
def test_percentage_coercion():    
    m = PredictIn(id_employee=1, augementation_salaire_precedente="5%")
    assert m.augementation_salaire_precedente == 5.0
    m2 = PredictIn(id_employee=1, augementation_salaire_precedente=" 2,5 % ")
    assert m2.augementation_salaire_precedente == 2.5

 # valeurs negatives interdites (pas logique pour ces champs)
@pytest.mark.parametrize("field", [
    "age",
    "nombre_experiences_precedentes",
    "annees_dans_le_poste_actuel",
    "satisfaction_employee_environnement",
])
def test_numeric_non_negative(field):   
    with pytest.raises(ValidationError):
        PredictIn(id_employee=1, **{field: -1})
