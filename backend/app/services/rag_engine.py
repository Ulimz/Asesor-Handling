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
from app.prompts import PROMPT_TEMPLATES, IntentType

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

    def detect_intent(self, query: str) -> IntentType:
        """
        Detect user intent based on keywords.
        """
        q = query.lower()
        
        # Salary Keywords
        if any(k in q for k in ['precio', 'salario', 'cobrar', 'retribución', 'paga', 'sueldo', 'plus', 'hora', 'festiva', 'nocturnidad', 'tabla', 'anexo', 'euros', '€']):
            return IntentType.SALARY
            
        # Dismissal Keywords
        if any(k in q for k in ['despido', 'despedi', 'extinción', 'finiquito', 'indemnización', 'disciplinario', 'improcedente', 'baja voluntaria']):
            return IntentType.DISMISSAL
            
        # Leave/Time Keywords
        if any(k in q for k in ['vacaciones', 'permiso', 'día libre', 'boda', 'nacimiento', 'hospitalización', 'excedencia', 'reducción']):
            return IntentType.LEAVE
            
        return IntentType.GENERAL

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

        # --- SPECIFIC ARTICLE RETRIEVAL (Estatuto / Convenio) ---
        # If query explicitly mentions "Artículo X", prioritize searching for that article ref.
        import re
        art_match = re.search(r'art[ií]culo\s+(\d+)', query, re.IGNORECASE)
        estatuto_match = re.search(r'estatuto', query, re.IGNORECASE)
        
        if art_match:
            art_num = art_match.group(1)
            print(f"📜 Article reference detected: {art_num}")
            
            # Base filter for article
            art_filter = DocumentChunk.article_ref.ilike(f'%Art%culo {art_num}%')
            
            # If "Estatuto" is mentioned, restrict to Estatuto docs
            doc_filter = None
            if estatuto_match:
                 print(f"   ⚖️  'Estatuto' detected, narrowing search.")
                 doc_filter = LegalDocument.title.ilike('%Estatuto%')
            elif company_slug:
                 # Otherwise prioritize Company + General
                 doc_filter = (LegalDocument.company == company_slug) | (LegalDocument.company.ilike('general'))
            
            if doc_filter is not None:
                priority_stmt = select(DocumentChunk).join(LegalDocument).filter(
                    doc_filter & art_filter
                ).limit(3)
                
                priority_results = list(db.execute(priority_stmt).scalars().all())
                
                # Add priority results immediately
                existing_ids = {r.id for r in results}
                for pr in priority_results:
                    if pr.id not in existing_ids:
                        print(f"   ⭐⭐ SPECIFIC ARTICLE Force-added: {pr.article_ref} ({pr.document.title})")
                        results.insert(0, pr) # Insert at TOP
                        existing_ids.add(pr.id)

        # --- HYBRID SEARCH: FORCE ANEXOS FOR SALARY QUERIES ---
        # Vector search can miss tables (Anexos). If query is about salary, force fetch Anexos.
        salary_keywords = ['precio', 'salario', 'retribución', 'retribucion', 'paga', 'sueldo', 
                          'complemento', 'plus', 'extraordinaria', 'perentoria',
                          'nocturna', 'festiva', 'tabla', 'anexo', 'euros', '€']
        
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
                "document_title": chunk.document.title if chunk.document else "Unknown",
                "company": chunk.document.company if chunk.document else "Unknown",
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
        
        # FAST PATH: If query clearly indicates continuation, merge immediately without LLM
        clean_q = current_query.strip().lower()
        if clean_q.startswith(("y ", "pero ", "entonces ", "ademas ", "también ")):
             last_user_msg = next((m['content'] for m in reversed(history) if m['role'] == 'user'), None)
             if last_user_msg:
                 merged = f"{last_user_msg} {current_query}"
                 print(f"⚡ Fast-Path Context Merge: '{last_user_msg}' + '{current_query}'")
                 
                 # Apply synonyms on merged result directly here for fast path return
                 merged_lower = merged.lower()
                 
                 # SALARY (Fast Path)
                 salary_keywords = ['precio', 'salario', 'retribución', 'retribucion', 'paga', 'sueldo', 
                                   'complemento', 'plus', 'hora', 'horas', 'extraordinaria', 'perentoria',
                                   'nocturna', 'festiva', 'complementaria', 'tabla', 'anexo', 'cuanto', 'cuánto']
                 if any(k in merged_lower for k in salary_keywords) and 'anexo' not in merged_lower:
                     merged = f"{merged} ANEXO tabla salarial retribución"

                 # FOOD (Fast Path)
                 food_keywords = ['comida', 'comer', 'almuerzo', 'bocadillo', 'merienda', 'cena']
                 if any(k in merged_lower for k in food_keywords) and 'refrigerio' not in merged_lower:
                     merged = f"{merged} refrigerio descanso pausa retribuida"
                     
                 return merged

        rewritten = current_query
        
        if self.gen_model:
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
                rewritten_response = response.text.strip()
                
                # Heuristic Fallback: If LLM failed to change anything but query looks dependent
                if rewritten_response == current_query and history:
                    last_user_msg = next((m['content'] for m in reversed(history) if m['role'] == 'user'), None)
                    if last_user_msg and len(current_query.split()) < 4: # Only merge if query is short
                        pass # merged logic below if needed, but keeping it simple for now
                    
                rewritten = rewritten_response
                
            except Exception as e:
                print(f"Error rewriting query: {e}")
                rewritten = current_query

        # --- POST-REWRITE ENHANCEMENTS (Synonyms & Keywords) ---
        # Apply these on the FINAL rewritten query (or original if no rewrite)
        rewritten_lower = rewritten.lower()

        # SALARY DETECTION
        salary_keywords = ['precio', 'salario', 'retribución', 'retribucion', 'paga', 'sueldo', 
                          'complemento', 'plus', 'extraordinaria', 'perentoria',
                          'nocturna', 'festiva', 'complementaria', 'tabla', 'anexo']
        
        is_salary_query = any(keyword in rewritten_lower for keyword in salary_keywords)
        if is_salary_query and 'anexo' not in rewritten_lower:
            rewritten = f"{rewritten} ANEXO tabla salarial retribución"
            print(f"💰 Salary query detected (post-merge), enhanced to search in ANEXOS")
            rewritten_lower = rewritten.lower() # Update for next check

        # FOOD/BREAK SYNONYMS
        food_keywords = ['comida', 'comer', 'almuerzo', 'bocadillo', 'merienda', 'cena']
        if any(k in rewritten_lower for k in food_keywords):
             if 'refrigerio' not in rewritten_lower:
                 rewritten = f"{rewritten} refrigerio descanso pausa retribuida"
                 print(f"🥪 Food query detected (post-merge), enhanced with synonyms: refrigerio, descanso")

        # REST/SHIFT SYNONYMS (Statute uses 'jornada' not 'turno' often)
        if 'descanso' in rewritten_lower and ('turno' in rewritten_lower or 'turnos' in rewritten_lower):
            rewritten = f"{rewritten} jornada descanso entre jornadas 12 horas doce horas Artículo 34 Estatuto"
            print(f"🛌 Rest/Shift query detected, enhanced with: jornada, 12 horas, doce horas, Artículo 34")

        return rewritten

    def generate_answer(self, query: str, context_chunks: list, intent: IntentType = IntentType.GENERAL, user_context: dict = None):
        """
        Generate answer using Gemini based on provided context and intent
        """
        if not self.gen_model:
            return "Error: GOOGLE_API_KEY no configurada en el servidor."
            
        context_text = "\n\n---\n\n".join([f"**{c.get('article_ref', 'Documento')}**\n{c['content']}" for c in context_chunks])
        
        # Truncate if context is too long (Gemini has token limits)
        if len(context_text) > MAX_CONTEXT_CHARS:
            print(f"[WARN] Context truncated from {len(context_text)} to {MAX_CONTEXT_CHARS} chars")
            context_text = context_text[:MAX_CONTEXT_CHARS] + "\n\n...[contexto truncado por longitud]"
        
        # Select Prompt Template based on Intent
        system_prompt = PROMPT_TEMPLATES.get(intent, PROMPT_TEMPLATES[IntentType.GENERAL])
        
        # Inject User Context if available
        user_info = ""
        if user_context:
            user_info = f"""
DATOS DEL USUARIO (Personaliza la respuesta para este perfil):
- Nombre: {user_context.get('preferred_name', 'Usuario')}
- Grupo Laboral: {user_context.get('job_group', 'No especificado')}
- Nivel Salarial: {user_context.get('salary_level', 'No especificado')}
- Tipo Contrato: {user_context.get('contract_type', 'No especificado')}

                IMPORTANTE: Si la respuesta depende del nivel salarial o grupo, USA EXCLUSIVAMENTE los datos de arriba. Si el usuario es Nivel 3, busca en las tablas el valor para Nivel 3.
                PRIORIDAD: Si el valor exacto (ej: precio hora) aparece en una Tabla o Anexo, UŚALO DIRECTAMENTE. NO realices cálculos manuales si el dato ya está facilitado en la tabla. Solo calcula si NO aparece el valor final.
                """
        
        final_prompt = f"""{system_prompt}

{user_info}

CONTEXTO PROPORCIONADO:
{context_text}

PREGUNTA:
{query}

RESPUESTA (Si es un dato de tabla, dalo directmente sin fórmulas):"""
        try:
            response = self.gen_model.generate_content(final_prompt)
            return response.text
        except Exception as e:
            return f"Error generando respuesta: {str(e)}"

rag_engine = RagEngine()
