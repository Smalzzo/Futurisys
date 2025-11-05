CREATE SCHEMA IF NOT EXISTS mart;

-- 1) Drop dans le bon ordre (enfants -> parent)
DROP VIEW IF EXISTS mart.employee_features_input_by_id;
DROP VIEW IF EXISTS mart.employee_features_input;


DROP TABLE IF EXISTS mart.employee_features;



CREATE  TABLE mart.employee_features AS
SELECT
    s.id_employee,
    so.a_quitte_l_entreprise,

    s.age,
    s.nombre_experiences_precedentes,
    s.annees_dans_le_poste_actuel,
    e.satisfaction_employee_environnement,
    e.note_evaluation_precedente,
    e.niveau_hierarchique_poste,
    e.satisfaction_employee_nature_travail,
    e.satisfaction_employee_equipe,
    e.satisfaction_employee_equilibre_pro_perso,
    e.note_evaluation_actuelle,
    e.augementation_salaire_precedente,      
    so.nombre_participation_pee,
    so.nb_formations_suivies,
    so.distance_domicile_travail,
    so.niveau_education,
    so.annees_depuis_la_derniere_promotion,
    so.annes_sous_responsable_actuel,

    -- Logs
    LN(NULLIF(s.annees_dans_l_entreprise,0)) AS anciennete_log,
    LN(NULLIF(s.annee_experience_totale,0))  AS annee_experience_totale_log,

   
    s.genre,
    s.statut_marital,
    s.departement,
    s.poste,
    UPPER(TRIM(e.heure_supplementaires))     AS heure_supplementaires, 
    so.domaine_etude,
    so.frequence_deplacement,

    
    s.revenu_mensuel
FROM raw.sirh_clean     AS s
LEFT JOIN raw.eval_clean     AS e  ON e.id_employee = s.id_employee
LEFT JOIN raw.sondage_clean  AS so ON so.id_employee = s.id_employee;
