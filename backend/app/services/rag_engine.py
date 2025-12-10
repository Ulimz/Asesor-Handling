from sentence_transformers import SentenceTransformer
from sqlalchemy import select, func
from sqlalchemy.orm import Session
from app.db.models import DocumentChunk, LegalDocument
import numpy as np
import google.generativeai as genai
import os
from app.constants import (
    EMBEDDING_MODEL_NAME,
    EMBEDDING_DIMENSION,
    HISTORY_CONTEXT_MESSAGES,
    MAX_CONTEXT_CHARS
)

class RagEngine:
    def __init__(self):
        # Lazy loading: model will be loaded on first use
        self._model = None
        
        # Initialize Gemini (free tier) if key is present
        api_key = os.getenv("GOOGLE_API_KEY")
        self.gen_model = None
        if api_key:
            genai.configure(api_key=api_key)
            self.gen_model = genai.GenerativeModel('gemini-2.0-flash')
    
    @property
    def model(self):
        """Lazy load the embedding model only when needed (saves ~400MB RAM per worker)"""
        if self._model is None:
            print(f"[INFO] Loading SentenceTransformer model ({EMBEDDING_MODEL_NAME})...")
            self._model = SentenceTransformer(EMBEDDING_MODEL_NAME)
        return self._model

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
        
        # PgVector cosine similarity search with eager loading
        # Using <=> operator for cosine distance (lower is better)
        from sqlalchemy.orm import joinedload
        
        stmt = select(DocumentChunk).join(LegalDocument).options(
            joinedload(DocumentChunk.document)  # Eager load to prevent N+1 queries
        ).order_by(
            DocumentChunk.embedding.cosine_distance(query_embedding)
        )
        
        if company_slug:
            # Filter by specific company OR global documents (company IS NULL or 'general' case-insensitive)
            stmt = stmt.filter(
                (LegalDocument.company == company_slug) | 
                (LegalDocument.company.is_(None)) |
                (LegalDocument.company.ilike('general'))
            )

        stmt = stmt.limit(limit)
        
        results = db.execute(stmt).scalars().all()
        results = list(results) # Convert to list to allow appending

        # --- HYBRID SEARCH: FORCE ANEXOS FOR SALARY QUERIES ---
        # Vector search can miss tables (Anexos). If query is about salary, force fetch Anexos.
        salary_keywords = ['precio', 'salario', 'retribución', 'retribucion', 'paga', 'sueldo', 
                          'complemento', 'plus', 'hora', 'extraordinaria', 'perentoria',
                          'nocturna', 'festiva', 'tabla', 'anexo', 'cuanto', 'cuánto', 'euros', '€']
        
        is_salary_query = any(k in query.lower() for k in salary_keywords)
        
        if is_salary_query and company_slug:
            print(f"💰 Salary intent detected in search: forcing retrieval of ANEXOs/Tablas")
            
            # 1. PRIORITY: Fetch BIG chunks from ANEXOs/TABLAS (Tables are usually large)
            priority_stmt = select(DocumentChunk).join(LegalDocument).filter(
                (LegalDocument.company == company_slug) &
                ((DocumentChunk.article_ref.ilike('%ANEXO%')) | (DocumentChunk.article_ref.ilike('%TABLA%')))
            ).order_by(
                func.length(DocumentChunk.content).desc()
            ).limit(3)
            
            priority_results = list(db.execute(priority_stmt).scalars().all())
            
            # Add priority results immediately
            existing_ids = {r.id for r in results}
            for pr in priority_results:
                if pr.id not in existing_ids:
                    print(f"   ⭐⭐ PRIORITY Force-added: {pr.article_ref}")
                    results.append(pr)
                    existing_ids.add(pr.id)

            # 2. General Fallback: Other Anexos/Tablas
            anexo_stmt = select(DocumentChunk).join(LegalDocument).filter(
                (LegalDocument.company == company_slug) &
                ((DocumentChunk.article_ref.ilike('%ANEXO%')) | (DocumentChunk.article_ref.ilike('%TABLA%')))
            ).limit(10) 
            
            anexo_results = db.execute(anexo_stmt).scalars().all()
            
            # Add ONLY if not already in results
            existing_ids = {r.id for r in results}
            for ar in anexo_results:
                if ar.id not in existing_ids:
                    print(f"   ➕ Force-added: {ar.article_ref}")
                    results.append(ar)
        # -----------------------------------------------------

        # Format results
        
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

    def rewrite_query(self, current_query: str, history: list = None):
        """
        Rewrite query using conversation history for context.
        Enhanced to detect salary-related queries and prioritize ANEXOS.
        
        Example: "y si tengo 4x4?" + Context [User: "Vacaciones en Azul"] -> "Vacaciones en rotación 4x4"
        """
        # SALARY DETECTION: Enhance query if it's about prices/salaries
        salary_keywords = ['precio', 'salario', 'retribución', 'retribucion', 'paga', 'sueldo', 
                          'complemento', 'plus', 'hora', 'horas', 'extraordinaria', 'perentoria',
                          'nocturna', 'festiva', 'complementaria', 'tabla', 'anexo', 'cuanto', 'cuánto']
        
        query_lower = current_query.lower()
        is_salary_query = any(keyword in query_lower for keyword in salary_keywords)
        
        if is_salary_query and 'anexo' not in query_lower:
            # Add ANEXO keywords to improve semantic search
            current_query = f"{current_query} ANEXO tabla salarial retribución"
            print(f"💰 Salary query detected, enhanced to search in ANEXOS")
        
        if not history:
            return current_query

        # FAST PATH: If query clearly indicates continuation, merge immediately without LLM
        clean_q = current_query.strip().lower()
        if clean_q.startswith(("y ", "pero ", "entonces ", "ademas ", "también ")):
             last_user_msg = next((m['content'] for m in reversed(history) if m['role'] == 'user'), None)
             if last_user_msg:
                 print(f"⚡ Fast-Path Context Merge: '{last_user_msg}' + '{current_query}'")
                 return f"{last_user_msg} {current_query}"

        if not self.gen_model:
            return current_query

        # Format last N messages for context
        relevant_history = history[-HISTORY_CONTEXT_MESSAGES:] 
        history_text = "\n".join([f"{msg['role']}: {msg['content']}" for msg in relevant_history])
        
        prompt = f"""Dada esta conversación:
{history_text}

Nueva pregunta del usuario: {current_query}

Si la nueva pregunta hace referencia a algo mencionado antes (ej: "y eso?", "cuánto es?"), reescríbela de forma completa y autónoma.
Si ya es clara y completa, devuélvela tal cual.

Pregunta reescrita:"""
        
        try:
            response = self.gen_model.generate_content(prompt)
            rewritten = response.text.strip()
            
            # Heuristic Fallback: If LLM failed to change anything but query looks dependent
            if rewritten == current_query and history:
                # Check for last USER message
                last_user_msg = next((m['content'] for m in reversed(history) if m['role'] == 'user'), None)
                if last_user_msg:
                    print(f"⚠️ LLM lazy, using heuristic merge: '{last_user_msg}' + '{current_query}'")
                    rewritten = f"{last_user_msg} {current_query}"
            
            return rewritten
        except Exception as e:
            print(f"Error rewriting query: {e}")
            return current_query

    def generate_answer(self, query: str, context_chunks: list):
        """
        Generate answer using Gemini based on provided context
        """
        if not self.gen_model:
            return "Error: GOOGLE_API_KEY no configurada en el servidor."
            
        context_text = "\n\n---\n\n".join([f"**{c.get('article_ref', 'Documento')}**\n{c['content']}" for c in context_chunks])
        
        # Truncate if context is too long (Gemini has token limits)
        if len(context_text) > MAX_CONTEXT_CHARS:
            print(f"[WARN] Context truncated from {len(context_text)} to {MAX_CONTEXT_CHARS} chars")
            context_text = context_text[:MAX_CONTEXT_CHARS] + "\n\n...[contexto truncado por longitud]"
        
        prompt = f"""Eres un asistente legal especializado en convenios colectivos del sector de Handling Aeroportuario en España.

CONTEXTO PROPORCIONADO:
{context_text}

PREGUNTA:
{query}

INSTRUCCIONES OBLIGATORIAS:
1. Responde SIEMPRE usando la información del contexto anterior
2. Si hay tablas con valores numéricos (ej: en ANEXOS), ÚSALAS.
   - Si la tabla dice "Nivel X - Euros", asume que son los valores económicos base (hora ordinaria o salario base) y úsalos.
   - Si la pregunta requiere un cálculo (ej: hora perentoria = hora ordinaria + 75%), REALIZA EL CÁLCULO usando el valor de la tabla.
   - Ejemplo: Si Tabla Nivel 2 = 10€ y Perentoria = +75%, responde: "El precio base es 10€, por lo que la hora perentoria sería 17,50€".
3. Cita SIEMPRE el Artículo o Anexo de donde sacas el dato.
4. Si la pregunta es sobre un precio (horas, pluses) y hay varios NIVELES o ANTIGÜEDAD en la tabla:
   - Si el usuario NO especifica su nivel, MUESTRA LA TABLA COMPLETA o el rango de precios (ej: "Desde el Nivel 1 (10€) al Nivel 5 (15€)"). NO des un solo valor al azar.
   - Si el usuario especifica nivel, da el valor exacto.
5. Responde con PRECISIÓN y DIRECTAMENTE al grano.

RESPUESTA (directa, con cálculos si es necesario):"""
        try:
            response = self.gen_model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"Error generando respuesta: {str(e)}"

rag_engine = RagEngine()
