from sentence_transformers import SentenceTransformer
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.db.models import DocumentChunk
import numpy as np

class RagEngine:
    def __init__(self):
        # Load free local model (384 dimensions)
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
    
    def generate_embedding(self, text: str):
        """Convert text to vector using local model"""
        return self.model.encode(text).tolist()
    
    def search(self, query: str, company_slug: str = None, db: Session = None, limit: int = 5):
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
        stmt = select(DocumentChunk).order_by(
            DocumentChunk.embedding.cosine_distance(query_embedding)
        ).limit(limit)
        
        results = db.execute(stmt).scalars().all()
        
        # Format results
        formatted_results = []
        for chunk in results:
            formatted_results.append({
                "id": chunk.id,
                "content": chunk.content,
                "article_ref": chunk.article_ref,
                "document_id": chunk.document_id,
                "score": 1.0  # Placeholder, actual distance not exposed here
            })
        
        return formatted_results

rag_engine = RagEngine()
