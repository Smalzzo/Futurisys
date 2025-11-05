CREATE OR REPLACE VIEW mart.employee_features_input AS
SELECT
    -- COL_NUM
    age,
    nombre_experiences_precedentes,
    annees_dans_le_poste_actuel,
    satisfaction_employee_environnement,
    note_evaluation_precedente,
    niveau_hierarchique_poste,
    satisfaction_employee_nature_travail,
    satisfaction_employee_equipe,
    satisfaction_employee_equilibre_pro_perso,
    note_evaluation_actuelle,
    augementation_salaire_precedente,
    nombre_participation_pee,
    nb_formations_suivies,
    distance_domicile_travail,
    niveau_education,
    annees_depuis_la_derniere_promotion,
    annes_sous_responsable_actuel,
    anciennete_log,
    annee_experience_totale_log,

    -- COL_NOMINAL
    genre, statut_marital, departement, poste, heure_supplementaires, domaine_etude,

    -- COL_ORDINAL
    frequence_deplacement
FROM mart.employee_features;




-- Vue d’entrée "by id" : id_employee + features pour l’API /by-id/{employee_id}
DROP VIEW IF EXISTS mart.employee_features_input_by_id CASCADE;
CREATE VIEW mart.employee_features_input_by_id AS
SELECT
  id_employee,

  -- COL_NUM
    age,
    nombre_experiences_precedentes,
    annees_dans_le_poste_actuel,
    satisfaction_employee_environnement,
    note_evaluation_precedente,
    niveau_hierarchique_poste,
    satisfaction_employee_nature_travail,
    satisfaction_employee_equipe,
    satisfaction_employee_equilibre_pro_perso,
    note_evaluation_actuelle,
    augementation_salaire_precedente,
    nombre_participation_pee,
    nb_formations_suivies,
    distance_domicile_travail,
    niveau_education,
    annees_depuis_la_derniere_promotion,
    annes_sous_responsable_actuel,
    anciennete_log,
    annee_experience_totale_log,

    -- COL_NOMINAL
    genre, statut_marital, departement, poste, heure_supplementaires, domaine_etude,

    -- COL_ORDINAL
    frequence_deplacement

FROM mart.employee_features;
