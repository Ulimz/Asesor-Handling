from sentence_transformers import SentenceTransformer
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.db.models import DocumentChunk, LegalDocument
import numpy as np
import google.generativeai as genai
import os

class RagEngine:
    def __init__(self):
        # Initialize local embedding model (free)
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        
        # Initialize Gemini (free tier) if key is present
        api_key = os.getenv("GOOGLE_API_KEY")
        self.gen_model = None
        if api_key:
            genai.configure(api_key=api_key)
            self.gen_model = genai.GenerativeModel('gemini-2.0-flash')

    def generate_embedding(self, text: str):
        return self.model.encode(text)

    def search(self, query: str, company_slug: str = None, db: Session = None, limit: int = 10):
        """
        Semantic search using PgVector cosine similarity.
        """
        if not db:
            # Fallback to old Elasticsearch if no DB session provided
            from app.services.elasticsearch_service import es_service
            results = es_service.search_documents(query, company_slug)
            formatted_results = []
            for hit in results:
                source = hit["_source"]
                formatted_results.append({
                    "id": hit["_id"],
                    "score": hit["_score"],
                    "title": source.get("title"),
                    "content": source.get("content"),
                    "company_slug": source.get("company_slug"),
                    "tags": source.get("tags", [])
                })
            return formatted_results
        
        # Generate query embedding
        query_embedding = self.generate_embedding(query)
        
        # PgVector cosine similarity search
        # Using <=> operator for cosine distance (lower is better)
        stmt = select(DocumentChunk).join(LegalDocument).order_by(
            DocumentChunk.embedding.cosine_distance(query_embedding)
        )
        
        if company_slug:
            # Filter by specific company OR global documents (company IS NULL or 'general')
            stmt = stmt.filter(
                (LegalDocument.company == company_slug) | 
                (LegalDocument.company.is_(None)) |
                (LegalDocument.company == 'general')
            )

        stmt = stmt.limit(limit)
        
        results = db.execute(stmt).scalars().all()
        
        # Format results
        formatted_results = []
        for chunk in results:
            formatted_results.append({
                "id": chunk.id,
                "content": chunk.content,
                "article_ref": chunk.article_ref,
                "document_id": chunk.document.category if chunk.document else "unknown", # Access parent doc if needed
                "score": 1.0  # Placeholder
            })
        
        return formatted_results

    def generate_answer(self, query: str, context_chunks: list):
        """
        Generate answer using Gemini based on provided context
        """
        if not self.gen_model:
            return "Error: GOOGLE_API_KEY no configurada en el servidor."
            
        context_text = "\n\n".join([c['content'] for c in context_chunks])
        
        prompt = f"""Actúa como un Asistente Legal experto en Handling Aeroportuario en España.
Responde a la pregunta del usuario basándote EXCLUSIVAMENTE en el siguiente contexto proporcionado.
Si la respuesta no está en el contexto, indica que no tienes esa información.
Menciona explícitamente qué artículo o convenio usas si aparece en el contexto.

CONTEXTO:
{context_text}

PREGUNTA:
{query}
"""
        try:
            response = self.gen_model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"Error generando respuesta: {str(e)}"

rag_engine = RagEngine()
