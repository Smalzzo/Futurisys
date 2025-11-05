-- Schémas
CREATE SCHEMA IF NOT EXISTS raw;
CREATE SCHEMA IF NOT EXISTS mart;


DROP TABLE IF EXISTS raw.sirh_raw CASCADE;
CREATE TABLE raw.sirh_raw (
    id_employee                 INT PRIMARY KEY,
    age                         INT,
    genre                       TEXT,
    revenu_mensuel              NUMERIC,
    statut_marital              TEXT,
    departement                 TEXT,
    poste                       TEXT,
    nombre_experiences_precedentes INT,
    nombre_heures_travailless   INT,
    annee_experience_totale     INT,
    annees_dans_l_entreprise    INT,
    annees_dans_le_poste_actuel INT
);


DROP TABLE IF EXISTS raw.sondage_raw CASCADE;
CREATE TABLE raw.sondage_raw (
    code_sondage                            TEXT,  
    a_quitte_l_entreprise                   TEXT,   
    nombre_participation_pee                INT,
    nb_formations_suivies                   INT,
    nombre_employee_sous_responsabilite     INT,
    distance_domicile_travail               NUMERIC,
    niveau_education                        INT,
    domaine_etude                           TEXT,
    ayant_enfants                           TEXT,   
    frequence_deplacement                   TEXT,   
    annees_depuis_la_derniere_promotion     INT,
    annes_sous_responsable_actuel           INT
);


DROP TABLE IF EXISTS raw.eval_raw CASCADE;
CREATE TABLE raw.eval_raw (
    eval_number                         TEXT,   
    satisfaction_employee_environnement NUMERIC,
    note_evaluation_precedente          NUMERIC,
    niveau_hierarchique_poste           NUMERIC,
    satisfaction_employee_nature_travail NUMERIC,
    satisfaction_employee_equipe        NUMERIC,
    satisfaction_employee_equilibre_pro_perso NUMERIC,
    note_evaluation_actuelle            NUMERIC,
    heure_supplementaires               TEXT,   
    augementation_salaire_precedente    TEXT 
);


