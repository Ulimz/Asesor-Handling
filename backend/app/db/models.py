from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship, declarative_base
from pgvector.sqlalchemy import Vector
from datetime import datetime

from app.db.base import Base

class LegalDocument(Base):
    """Parent document (Convenio, Estatuto, etc.)"""
    __tablename__ = "legal_documents"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)  # "V Convenio Handling"
    category = Column(String)  # "Convenio", "Estatuto", "Jurisprudencia"
    company = Column(String, nullable=True)  # "Iberia", "General"
    url_source = Column(String, nullable=True)
    
    # Relationship
    chunks = relationship("DocumentChunk", back_populates="document")

class DocumentChunk(Base):
    """Fragmentos del texto legal vectorizados para búsqueda semántica"""
    __tablename__ = "document_chunks"
    
    id = Column(Integer, primary_key=True)
    document_id = Column(Integer, ForeignKey("legal_documents.id"))
    content = Column(Text)  # El texto del artículo
    embedding = Column(Vector(384))  # Vector de sentence-transformers (all-MiniLM-L6-v2)
    article_ref = Column(String, index=True)  # "Art. 45" - indexed for faster lookups
    
    # Relationship
    document = relationship("LegalDocument", back_populates="chunks")

class UserClaim(Base):
    """Reclamaciones generadas por usuarios"""
    __tablename__ = "user_claims"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=True)  # Placeholder for future auth
    type = Column(String)  # "Nomina", "Horas", "Sancion"
    generated_text = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
