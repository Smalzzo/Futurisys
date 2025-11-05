-- Préparation : vues "nettoyées" (UPPER + suppression espaces)
DROP VIEW IF EXISTS raw.sirh_clean CASCADE;
CREATE VIEW raw.sirh_clean AS
SELECT
  CAST(NULLIF(REPLACE(id_employee::text, ' ', ''), '') AS INT)                                       AS id_employee,
  CAST(NULLIF(REPLACE(age::text, ' ', ''), '') AS INT)                                               AS age,
  UPPER(TRIM(genre))                                                                                 AS genre,
  CAST(NULLIF(REPLACE(revenu_mensuel::text, ' ', ''), '') AS NUMERIC)                                AS revenu_mensuel,
  UPPER(TRIM(statut_marital))                                                                        AS statut_marital,
  UPPER(TRIM(departement))                                                                           AS departement,
  UPPER(TRIM(poste))                                                                                 AS poste,
  CAST(NULLIF(REPLACE(nombre_experiences_precedentes::text, ' ', ''), '') AS INT)                    AS nombre_experiences_precedentes,
  CAST(NULLIF(REPLACE(nombre_heures_travailless::text, ' ', ''), '') AS INT)                         AS nombre_heures_travailless,
  CAST(NULLIF(REPLACE(annee_experience_totale::text, ' ', ''), '') AS INT)                           AS annee_experience_totale,
  CAST(NULLIF(REPLACE(annees_dans_l_entreprise::text, ' ', ''), '') AS INT)                          AS annees_dans_l_entreprise,
  CAST(NULLIF(REPLACE(annees_dans_le_poste_actuel::text, ' ', ''), '') AS INT)                       AS annees_dans_le_poste_actuel
FROM raw.sirh_raw;



DROP VIEW IF EXISTS raw.eval_clean CASCADE;
CREATE VIEW raw.eval_clean AS
SELECT
  -- 'E_1' -> 1
  CAST(NULLIF(REGEXP_REPLACE(UPPER(REPLACE(eval_number, ' ', '')), '^\D+', ''), '') AS INT) AS id_employee,

  CAST(NULLIF(REPLACE(satisfaction_employee_environnement::text, ' ', ''), '') AS NUMERIC)   AS satisfaction_employee_environnement,
  CAST(NULLIF(REPLACE(note_evaluation_precedente::text, ' ', ''), '') AS NUMERIC)            AS note_evaluation_precedente,
  CAST(NULLIF(REPLACE(niveau_hierarchique_poste::text, ' ', ''), '') AS NUMERIC)             AS niveau_hierarchique_poste,
  CAST(NULLIF(REPLACE(satisfaction_employee_nature_travail::text, ' ', ''), '') AS NUMERIC)  AS satisfaction_employee_nature_travail,
  CAST(NULLIF(REPLACE(satisfaction_employee_equipe::text, ' ', ''), '') AS NUMERIC)          AS satisfaction_employee_equipe,
  CAST(NULLIF(REPLACE(satisfaction_employee_equilibre_pro_perso::text, ' ', ''), '') AS NUMERIC) AS satisfaction_employee_equilibre_pro_perso,
  CAST(NULLIF(REPLACE(note_evaluation_actuelle::text, ' ', ''), '') AS NUMERIC)              AS note_evaluation_actuelle,

  
  UPPER(TRIM(heure_supplementaires))                                                         AS heure_supplementaires,
  
  CAST(
    NULLIF(REPLACE(UPPER(REPLACE(augementation_salaire_precedente, ' ', '')), '%', ''), '')
    AS NUMERIC
  ) AS augementation_salaire_precedente
FROM raw.eval_raw;



DROP VIEW IF EXISTS raw.sondage_clean CASCADE;
CREATE VIEW raw.sondage_clean AS
SELECT
  -- '000001' -> 1
  CAST(NULLIF(REPLACE(code_sondage, ' ', ''), '') AS INT)                                          AS id_employee,

  UPPER(TRIM(a_quitte_l_entreprise))                                                               AS a_quitte_l_entreprise,
  CAST(NULLIF(REPLACE(nombre_participation_pee::text, ' ', ''), '') AS INT)                        AS nombre_participation_pee,
  CAST(NULLIF(REPLACE(nb_formations_suivies::text, ' ', ''), '') AS INT)                           AS nb_formations_suivies,
  CAST(NULLIF(REPLACE(nombre_employee_sous_responsabilite::text, ' ', ''), '') AS INT)             AS nombre_employee_sous_responsabilite,
  CAST(NULLIF(REPLACE(distance_domicile_travail::text, ' ', ''), '') AS NUMERIC)                   AS distance_domicile_travail,
  CAST(NULLIF(REPLACE(niveau_education::text, ' ', ''), '') AS INT)                                AS niveau_education,
  UPPER(TRIM(domaine_etude))                                                                        AS domaine_etude,
  UPPER(TRIM(ayant_enfants))                                                                        AS ayant_enfants,
  UPPER(TRIM(frequence_deplacement))                                                                AS frequence_deplacement,
  CAST(NULLIF(REPLACE(annees_depuis_la_derniere_promotion::text, ' ', ''), '') AS INT)             AS annees_depuis_la_derniere_promotion,
  CAST(NULLIF(REPLACE(annes_sous_responsable_actuel::text, ' ', ''), '') AS INT)                   AS annes_sous_responsable_actuel
FROM raw.sondage_raw;

