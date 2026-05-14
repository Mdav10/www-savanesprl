from sqlalchemy import Column, Integer, String, Float, DateTime, Enum, ForeignKey, Boolean, Text
from datetime import datetime
from app.database import Base
import enum

class RoleEnum(str, enum.Enum):
    DG = "DG"
    DAF = "DAF"
    DT = "DT"
    DIRECTEUR_COMMERCIAL = "DIRECTEUR_COMMERCIAL"
    COMPTABLE = "COMPTABLE"
    AGENT_STOCK = "AGENT_STOCK"
    AGENT_COMMERCIAL = "AGENT_COMMERCIAL"

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
    created_at = Column(DateTime, default=datetime.utcnow)

class Product(Base):
    __tablename__ = "products"
    id = Column(Integer, primary_key=True, index=True)
    nom = Column(String, nullable=False)
    prix_unitaire = Column(Float, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class StockMovement(Base):
    __tablename__ = "stock_movements"
    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    quantite_entree = Column(Integer, default=0)
    quantite_sortie = Column(Integer, default=0)
    quantite_disponible = Column(Integer, default=0)
    agent_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    date = Column(DateTime, default=datetime.utcnow)

class SaleReport(Base):
    __tablename__ = "sale_reports"
    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    quantite = Column(Integer, nullable=False)
    montant_total = Column(Float, nullable=False)
    agent_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    date = Column(DateTime, default=datetime.utcnow)

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

class ActiviteLog(Base):
    __tablename__ = "activite_logs"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    action = Column(String, nullable=False)
    details = Column(Text, nullable=True)
    date = Column(DateTime, default=datetime.utcnow)
