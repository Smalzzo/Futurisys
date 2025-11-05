import os
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Float, String, Integer, BigInteger, Text, ForeignKey, UniqueConstraint, JSON, DateTime
from .base import Base
from datetime import datetime
from app.core.config import get_settings



try:
    # Préfère la config Pydantic (charge .env) pour déterminer le backend
    IS_SQLITE = get_settings().DATABASE_URL.startswith("sqlite:")
except Exception:
    # Fallback sur les variables d'environnement si settings indisponible à l'import
    IS_SQLITE = (
        os.getenv("DATABASE_URL", "").startswith("sqlite:")
        or os.getenv("DB_BACKEND", "").lower() == "sqlite"
    )


# Types adaptés par backend (SQLite a besoin d'un INTEGER PRIMARY KEY pour l'auto-incrément)
IdPKType = Integer if 'IS_SQLITE' in globals() and IS_SQLITE else BigInteger
BigIntCompat = Integer if 'IS_SQLITE' in globals() and IS_SQLITE else BigInteger


class EmployeeFeatures(Base):
    __tablename__ = "employee_features"
    __table_args__ = ({"schema": "mart"} if not IS_SQLITE else {})

    id_employee: Mapped[int] = mapped_column(Integer, primary_key=True)    
    a_quitte_l_entreprise: Mapped[str] = mapped_column(String)
    age: Mapped[int] = mapped_column(Integer)
    nombre_experiences_precedentes: Mapped[int] = mapped_column(Integer)
    annees_dans_le_poste_actuel: Mapped[int] = mapped_column(Integer)
    satisfaction_employee_environnement: Mapped[float] = mapped_column(Float)
    note_evaluation_precedente: Mapped[float] = mapped_column(Float)
    niveau_hierarchique_poste: Mapped[str] = mapped_column(String)
    satisfaction_employee_nature_travail: Mapped[float] = mapped_column(Float)
    satisfaction_employee_equipe: Mapped[float] = mapped_column(Float)
    satisfaction_employee_equilibre_pro_perso: Mapped[float] = mapped_column(Float)
    note_evaluation_actuelle: Mapped[float] = mapped_column(Float)
    augementation_salaire_precedente: Mapped[float] = mapped_column(Float)
    nombre_participation_pee: Mapped[int] = mapped_column(Integer)
    nb_formations_suivies: Mapped[int] = mapped_column(Integer)
    distance_domicile_travail: Mapped[float] = mapped_column(Float)
    niveau_education: Mapped[int] = mapped_column(Integer)
    annees_depuis_la_derniere_promotion: Mapped[int] = mapped_column(Integer)
    annes_sous_responsable_actuel: Mapped[int] = mapped_column(Integer)
    anciennete_log: Mapped[float] = mapped_column(Float)
    annee_experience_totale_log: Mapped[float] = mapped_column(Float)
    genre: Mapped[str] = mapped_column(String)
    statut_marital: Mapped[str] = mapped_column(String)
    departement: Mapped[str] = mapped_column(String)
    poste: Mapped[str] = mapped_column(String)
    heure_supplementaires: Mapped[str] = mapped_column(String)  
    domaine_etude: Mapped[str] = mapped_column(String)
    frequence_deplacement: Mapped[str] = mapped_column(String)
    
class PredictionLog(Base):
    __tablename__ = "prediction_log"
    __table_args__ = (
        (UniqueConstraint("employee_id", name="uq_prediction_log_employee_id"), {"schema": "ml_logs"})
        if not IS_SQLITE
        else (UniqueConstraint("employee_id", name="uq_prediction_log_employee_id"),)
    )
    id: Mapped[int] = mapped_column(IdPKType, primary_key=True, autoincrement=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    endpoint: Mapped[str] = mapped_column(Text, nullable=False)
    requested_by: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    employee_id: Mapped[Optional[int]] = mapped_column(BigIntCompat, nullable=True)
    latency_ms: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    status: Mapped[str] = mapped_column(Text, nullable=False, default="OK")    
    payload: Mapped[Dict[str, Any]] = mapped_column(JSON, nullable=False)
    output:  Mapped[Dict[str, Any]] = mapped_column(JSON, nullable=False)

class ErrorLog(Base):
    __tablename__ = "error_log"
    __table_args__ = ({"schema": "ml_logs"} if not IS_SQLITE else {})
    id: Mapped[int] = mapped_column(IdPKType, primary_key=True, autoincrement=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    endpoint: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    http_status: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    error_class: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    context: Mapped[Dict[str, Any]] = mapped_column(JSON, nullable=False, default=dict)
