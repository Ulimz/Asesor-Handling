from app.services.elasticsearch_service import es_service

class RagEngine:
    def search(self, query: str, company_slug: str = None):
        """
        Executes a semantic search against the legal knowledge base.
        In the future, this method can be expanded to retrieve context + generate an answer (RAG).
        """
        results = es_service.search_documents(query, company_slug)
        
        # Formatting for frontend consumption (simplified structure)
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

rag_engine = RagEngine()
