from sentence_transformers import SentenceTransformer
from sqlalchemy import select, func
from sqlalchemy.orm import Session
from app.db.models import DocumentChunk, LegalDocument
import numpy as np
import google.generativeai as genai
import os
import requests
import json
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
            # Use 2.0-flash and direct REST call for grounding to bypass SDK tool validation issues
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
        
        # 1. Dismissal / Resignation (baja voluntaria)
        if any(k in q for k in ['despido', 'despedi', 'extinción', 'finiquito', 'indemnización', 'disciplinario', 'improcedente', 'baja voluntaria']):
            return IntentType.DISMISSAL
            
        # 2. Leave / Tine / Sickness (Incapacidad Temporal)
        if any(k in q for k in ['vacaciones', 'permiso', 'día libre', 'boda', 'nacimiento', 'hospitalización', 'excedencia', 'reducción', 'baja', 'enfermedad', 'accidente', 'médico', 'it', 'incapacidad']):
            # Exception: if it's explicitly "baja voluntaria", it was already caught by DISMISSAL
            return IntentType.LEAVE
            
        # 3. Salary / Money (Only if not already categorized above)
        if any(k in q for k in ['precio', 'salario', 'cobrar', 'retribución', 'paga', 'sueldo', 'plus', 'hora', 'festiva', 'nocturnidad', 'tabla', 'anexo', 'euros', '€']):
            return IntentType.SALARY
            
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
            )
            
            # EXCLUSION LOGIC: Avoid PMR tables unless user asks for them
            if "pmr" not in query.lower():
                 priority_stmt = priority_stmt.filter(
                     ~DocumentChunk.article_ref.ilike('%PMR%'),
                     ~DocumentChunk.content.ilike('%PMR%')
                 )

            priority_stmt = priority_stmt.limit(3)
            
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
            )

            if "pmr" not in query.lower():
                 anexo_stmt = anexo_stmt.filter(
                     ~DocumentChunk.article_ref.ilike('%PMR%'),
                     ~DocumentChunk.content.ilike('%PMR%')
                 )

            anexo_stmt = anexo_stmt.limit(10) 
            
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
                 
                 # SALARY (Fast Path) - Only enhance if NOT about sick leave (baja)
                 salary_keywords = ['precio', 'salario', 'retribución', 'retribucion', 'paga', 'sueldo', 
                                   'complemento', 'plus', 'hora', 'horas', 'extraordinaria', 'perentoria',
                                   'nocturna', 'festiva', 'complementaria', 'tabla', 'anexo', 'cuanto', 'cuánto']
                 it_keywords = ['baja', 'it', 'enfermedad', 'incapacidad', 'médico']
                 
                 if any(k in merged_lower for k in salary_keywords) and \
                    not any(k in merged_lower for k in it_keywords) and \
                    'anexo' not in merged_lower:
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

        # SALARY DETECTION - Only enhance if NOT about sick leave (baja)
        salary_keywords = ['precio', 'salario', 'retribución', 'retribucion', 'paga', 'sueldo', 
                          'complemento', 'plus', 'extraordinaria', 'perentoria',
                          'nocturna', 'festiva', 'complementaria', 'tabla', 'anexo']
        it_keywords = ['baja', 'it', 'enfermedad', 'incapacidad', 'médico']
        
        is_salary_query = any(keyword in rewritten_lower for keyword in salary_keywords)
        is_it_query = any(keyword in rewritten_lower for keyword in it_keywords)
        
        if is_salary_query and not is_it_query and 'anexo' not in rewritten_lower:
            rewritten = f"{rewritten} ANEXO tabla salarial retribución"
            print(f"💰 Salary query detected (post-merge), enhanced to search in ANEXOS")
            rewritten_lower = rewritten.lower() # Update for next check
        elif is_it_query:
            rewritten = f"{rewritten} incapacidad temporal IT complemento baja"
            print(f"🏥 Sickness query detected, enhanced with synonyms: IT, incapacidad, complemento")
            rewritten_lower = rewritten.lower()

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

        return rewritten

    def generate_answer(self, query: str, context_chunks: list, intent: IntentType = IntentType.GENERAL, user_context: dict = None, structured_data: str = None):
        """
        Generate answer using Gemini based on provided context and intent
        """
        if not self.gen_model:
            return "Error: GOOGLE_API_KEY no configurada en el servidor."

        # --- KINSHIP TABLE INJECTION ---
        # If query contains family keywords, inject the official table
        from app.data.kinship import KINSHIP_KEYWORDS, get_kinship_table_markdown
        
        normalized_q = query.lower()
        is_family_related = any(k in normalized_q for k in KINSHIP_KEYWORDS)
        
        kinship_context = ""
        if is_family_related:
            kinship_context = get_kinship_table_markdown()
            print("👨‍👩‍👧‍👦 Family intent detected: Injecting Kinship Table into context")
            
        context_text = "\n\n---\n\n".join([f"**{c.get('article_ref', 'Documento')}**\n{c['content']}" for c in context_chunks])
        
        # Prepend Structured Data (Highest Priority)
        if structured_data:
             context_text = f"{structured_data}\n\n{context_text}"
        
        # Prepend Kinship Table if relevant
        if kinship_context:
            context_text = f"{kinship_context}\n\n{context_text}"

        
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

                REGLA DE ORO DE DINERO (PRIORIDAD MÁXIMA): 
                Los datos bajo el título 'DATOS OFICIALES DE TABLA SALARIAL' son 100% CORRECTOS y provienen de la calculadora oficial.
                SÍ hay cualquier contradicción entre el texto de los artículos (Convenio) y los valores de la tabla oficial, PREVALECE SIEMPRE LA TABLA.
                Usa el valor exacto de la tabla para el Nivel {user_context.get('salary_level')} y Grupo {user_context.get('job_group')} del usuario.
                """
        
        final_prompt = f"""{system_prompt}

{user_info}

        ADVERTENCIA DE SEGURIDAD Y PRIVACIDAD (PII):
        1. Este sistema procesa consultas de usuarios reales. Si en el CONTEXTO o la PREGUNTA aparecen nombres reales, DNI, números de teléfono o datos personales identificables, IGNÓRALOS y NO los incluyas en la respuesta.
        2. Si el usuario te da su propio nombre, puedes usarlo para dirigirte a él, pero NO almacenes ni repitas otros datos sensibles.
        3. Mantén la respuesta centrada en la normativa laboral.

CONTEXTO PROPORCIONADO:
{context_text}

PREGUNTA:
{query}

RESPUESTA (Si es un dato de tabla, dalo directmente sin fórmulas):"""
        try:
            # Lógica Híbrida REAL:
            # Siempre pasamos el contexto local, pero habilitamos la herramienta de búsqueda
            # para que el modelo decida si necesita complementar la información.
            
            # Prompt más flexible que permite usar búsqueda externa HÍBRIDA
            final_prompt = f"""
            {system_prompt}

            {user_info}
            
            CONTEXTO INTERNO (Prioridad MÁXIMA - "La Biblia"):
            {context_text}
            
            PREGUNTA DEL USUARIO:
            {query}
            
            INSTRUCCIONES DE BÚSQUEDA Y JERARQUÍA (Modo "Mini-GPT"):
            1. **PRIORIDAD ABSOLUTA**: Si la respuesta está en el CONTEXTO INTERNO (Convenios, Tablas), ÚSALO y NO busques fuera. Tu base de datos es la verdad absoluta para temas laborales internos.
            2. **MECANISMO DE FALLBACK (Mini-GPT)**: 
               - Si el Contexto Interno está VACÍO o NO responde a la pregunta (ej: noticias, huelgas actuales, leyes nuevas)...
               - ...ENTONCES: ¡USA TU HERRAMIENTA `google_search`!
               - Busca la información en internet y responde como un experto laboralista actualizado.
            
            3. **JERARQUÍA NORMATIVA**:
               - Si encuentras una LEY nueva en Google que contradice al Convenio antiguo -> La LEY gana. (Avisa de esto).
               - Para TABLAS SALARIALES y PARENTESCO: Usa SOLO los datos internos (son oficiales).

            4. **FORMATO**: 
               - Si usas info de fuera, sé conciso.
               - Si usas info interna, cita el artículo.
            """

            # Use Direct REST call for ALL generations to ensure Tool availability
            # This bypasses the SDK validation issues we faced.
            api_key = os.getenv("GOOGLE_API_KEY")
            if api_key:
                try:
                    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={api_key}"
                    payload = {
                        "contents": [{
                            "parts": [{"text": final_prompt}]
                        }],
                        "tools": [{"google_search": {}}],
                        "safetySettings": [
                            {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_ONLY_HIGH"},
                            {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_ONLY_HIGH"},
                            {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_ONLY_HIGH"},
                            {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_ONLY_HIGH"}
                        ]
                    }
                    headers = {'Content-Type': 'application/json'}
                    response = requests.post(url, headers=headers, data=json.dumps(payload))
                    
                    if response.status_code == 200:
                        result = response.json()
                        try:
                            # Try to get text from the first candidate
                            text_response = result['candidates'][0]['content']['parts'][0]['text']
                            
                            # Check for grounding metadata (citations) to confirm search usage
                            grounding_metadata = result['candidates'][0].get('groundingMetadata', {})
                            if grounding_metadata:
                                # Append a small indicator if external search was used
                                text_response += "\n\n(ℹ️ Información complementada con búsqueda externa)"
                            
                            return text_response
                        except (KeyError, IndexError):
                             # Fallback if structure is unexpected
                             return "Error interpretando respuesta de la IA."
                    else:
                        print(f"⚠️ API Error: {response.text}")
                        # Fallback to pure SDK generation (no tools) if REST fails
                        return self.gen_model.generate_content(final_prompt).text
                        
                except Exception as e:
                    print(f"⚠️ Exception in REST call: {e}")
                    return f"Error procesando la solicitud: {str(e)}"

            return "Error de configuración: API Cloud no disponible."
        except Exception as e:
            return f"Error generando respuesta: {str(e)}"

rag_engine = RagEngine()
