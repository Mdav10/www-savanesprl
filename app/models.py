from sqlalchemy import Column, Integer, String, Float, DateTime, Enum, ForeignKey, Boolean, Text
from datetime import datetime
from app.database import Base
import enum

class RoleEnum(str, enum.Enum):
    DG = "DG"
    DAF = "DAF"
    DIRECTEUR_COMMERCIAL = "DIRECTEUR_COMMERCIAL"
    COMPTABLE = "COMPTABLE"
    AGENT_MARKETING = "AGENT_MARKETING"

class TransactionStatus(str, enum.Enum):
    EN_ATTENTE = "EN_ATTENTE"
    APPROUVE = "APPROUVE"
    REJETE = "REJETE"

class TransactionType(str, enum.Enum):
    ENTREE = "entree"
    SORTIE = "sortie"

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    nom = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    mot_de_passe = Column(String, nullable=False)
    role_id = Column(Enum(RoleEnum), nullable=False)
    is_active = Column(Boolean, default=True)
    session_token = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class Transaction(Base):
    __tablename__ = "transactions"
    id = Column(Integer, primary_key=True, index=True)
    type = Column(Enum(TransactionType), nullable=False)
    montant = Column(Float, nullable=False)
    libelle = Column(String, nullable=False)
    statut = Column(Enum(TransactionStatus), default=TransactionStatus.EN_ATTENTE)
    valide_par = Column(Integer, ForeignKey("users.id"), nullable=True)
    cree_par = Column(Integer, ForeignKey("users.id"), nullable=False)
    date = Column(DateTime, default=datetime.utcnow)

class Vente(Base):
    __tablename__ = "ventes"
    id = Column(Integer, primary_key=True, index=True)
    produit = Column(String, nullable=False)
    quantite = Column(Integer, nullable=False)
    prix_unitaire = Column(Float, nullable=False)
    montant_total = Column(Float, nullable=False)
    agent_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    date = Column(DateTime, default=datetime.utcnow)

class Stock(Base):
    __tablename__ = "stock"
    id = Column(Integer, primary_key=True, index=True)
    produit = Column(String, unique=True, nullable=False)
    quantite_entree = Column(Integer, default=0)
    quantite_sortie = Column(Integer, default=0)
    quantite_disponible = Column(Integer, default=0)

class ActiviteLog(Base):
    __tablename__ = "activite_logs"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    action = Column(String, nullable=False)
    details = Column(Text)
    ip_address = Column(String)
    date = Column(DateTime, default=datetime.utcnow)
