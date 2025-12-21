from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean, Float, JSON, Index
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
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
    updated_at = Column(DateTime, default=datetime.utcnow) # Control de versiones
    version = Column(String, default="1.0") # "1.0", "2024", etc.
    
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
    
    # ✅ FASE 1: Metadata Schema (Híbrido)
    doc_id = Column(String, nullable=True, index=True)  # ID lógico del documento
    chunk_metadata = Column(JSONB, nullable=False, default=dict)  # Metadata estructurada
    
    # Relationship
    document = relationship("LegalDocument", back_populates="chunks")
    
    # ✅ ÍNDICES OPTIMIZADOS para búsqueda determinista
    # NOTA: Los índices se crearán DESPUÉS de la migración
    # __table_args__ = (
    #     # Índices individuales con casting
    #     Index('idx_metadata_type', metadata['type'].astext),
    #     Index('idx_metadata_company', metadata['company'].astext),
    #     Index('idx_metadata_year', metadata['year'].astext.cast(Integer)),
    #     
    #     # Índice compuesto para queries frecuentes
    #     Index(
    #         'idx_company_intent_type',
    #         metadata['company'].astext,
    #         metadata['intent'],
    #         metadata['type'].astext,
    #     ),
    #     
    #     # Índice para version_hash
    #     Index('idx_version_hash', metadata['version_hash'].astext),
    # )

class UserClaim(Base):
    """Reclamaciones generadas por usuarios"""
    __tablename__ = "user_claims"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=True)  # Placeholder for future auth
    type = Column(String)  # "Nomina", "Horas", "Sancion"
    generated_text = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

class SalaryTable(Base):
    """Tablas salariales para calculos de nómina (Salarios Base Fijos)"""
    __tablename__ = "salary_tables"

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(String, index=True) # "iberia", "groundforce"
    year = Column(Integer, index=True) # 2024
    group = Column(String, index=True) # "Administrativos", "Gestores"
    level = Column(String, index=True) # "Nivel A", "Nivel 1"
    concept = Column(String) # "Salario Base", "Plus Convenio", "Plus Transporte"
    amount = Column(Float) # 1500.00
    variable_type = Column(String, nullable=True) # "hour", "day", "month"

class SalaryConceptDefinition(Base):
    """Definición de conceptos variables dinámicos (metadata)"""
    __tablename__ = "salary_concept_definitions"

    id = Column(Integer, primary_key=True, index=True)
    company_slug = Column(String, index=True) # "iberia"
    name = Column(String) # "Plus Nocturnidad"
    code = Column(String, index=True) # "PLUS_NOCT"
    description = Column(Text, nullable=True) # "Se cobra entre 22h y 6h..."
    input_type = Column(String, default="number") # "number" (horas), "bool" (si/no), "days"
    default_price = Column(Float, default=0.0) # Precio unitario por defecto (si aplica)
    level_values = Column(JSON, nullable=True) # Mapa de precios por nivel/grupo
    is_active = Column(Boolean, default=True)
