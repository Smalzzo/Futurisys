-- SIRH
TRUNCATE raw.sirh_raw;
COPY raw.sirh_raw (
  id_employee,age,genre,revenu_mensuel,statut_marital,departement,poste,nombre_experiences_precedentes,
  nombre_heures_travailless,annee_experience_totale,annees_dans_l_entreprise,annees_dans_le_poste_actuel
)
FROM '/imports/extrait_sirh.csv'
WITH (FORMAT csv, HEADER true, DELIMITER ',', NULL '', QUOTE '"', ENCODING 'UTF8');

-- EVAL
TRUNCATE raw.eval_raw;
COPY raw.eval_raw (
  satisfaction_employee_environnement,note_evaluation_precedente,niveau_hierarchique_poste,satisfaction_employee_nature_travail,satisfaction_employee_equipe,satisfaction_employee_equilibre_pro_perso,
  eval_number,note_evaluation_actuelle,heure_supplementaires,augementation_salaire_precedente
)
FROM '/imports/extrait_eval.csv'
WITH (FORMAT csv, HEADER true, DELIMITER ',', NULL '', QUOTE '"', ENCODING 'UTF8');

-- SONDAGE
TRUNCATE raw.sondage_raw;
COPY raw.sondage_raw (
  a_quitte_l_entreprise,nombre_participation_pee,nb_formations_suivies,nombre_employee_sous_responsabilite,
  code_sondage,distance_domicile_travail,niveau_education,domaine_etude,ayant_enfants,
  frequence_deplacement,annees_depuis_la_derniere_promotion,annes_sous_responsable_actuel                  
)
FROM '/imports/extrait_sondage.csv'
WITH (FORMAT csv, HEADER true, DELIMITER ',', NULL '', QUOTE '"', ENCODING 'UTF8');

-- 3) Index utiles pour les jointures du mart
CREATE INDEX IF NOT EXISTS ix_raw_sirh_id_employee   ON raw.sirh_raw (id_employee);
CREATE INDEX IF NOT EXISTS ix_raw_eval_eval_number   ON raw.eval_raw (eval_number);
CREATE INDEX IF NOT EXISTS ix_raw_sondage_emp_number ON raw.sondage_raw (code_sondage);
