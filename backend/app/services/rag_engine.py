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
from app.services.calculator_service import CalculatorService
from app.schemas.salary import CalculationRequest
from sqlalchemy.orm import Session # Typed typing

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
            # Use 2.0-flash and direct REST call for grounding to bypass SDK tool validation issues
            self.gen_model = genai.GenerativeModel('gemini-2.0-flash')

    # --- TOOL DEFINITIONS ---
    @property
    def calculator_tool_schema(self):
        """
        Defines the schema for the calculate_payroll tool for Gemini.
        """
        return {
            "name": "calculate_payroll",
            "description": "Calculates the estimated monthly net salary based on gross annual salary or specific payroll variables.",
            "parameters": {
                "type": "object",
                "properties": {
                    "gross_annual_salary": {
                        "type": "number",
                        "description": "The gross annual salary of the employee. If unknown, use 0."
                    },
                    "extra_hours": {
                        "type": "number",
                        "description": "Number of extra hours worked (optional)."
                    },
                    "night_hours": {
                        "type": "number",
                        "description": "Number of night hours worked (optional)."
                    },
                    "holiday_hours": {
                        "type": "number",
                        "description": "Number of holiday hours works (optional)."
                    },
                    "force_days": {
                        "type": "number",
                        "description": "Number of 'force majeure' hours if applicable (optional)."
                    },
                    "payments": {
                        "type": "integer",
                        "description": "Number of annual payments (12 or 14). Default to 14 if not specified."
                    }
                },
                "required": ["gross_annual_salary"]
            }
        }
    
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
            # Fallback to old Elasticsearch if no DB session provided
            from app.services.elasticsearch_service import search_documents
            results = search_documents("salary-index", query, {"company_slug": company_slug} if company_slug else None)
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

    def generate_answer(self, query: str, context_chunks: list, intent: IntentType = IntentType.GENERAL, user_context: dict = None, structured_data: str = None, history: list = [], db: Session = None):
        """
        Generate answer using Gemini based on provided context and intent
        """
        if not self.gen_model:
            return {"text": "Error: GOOGLE_API_KEY no configurada en el servidor.", "audit": None}

        # --- KINSHIP TABLE INJECTION ---
        # If query contains family keywords, inject the official table
        from app.data.kinship import KINSHIP_KEYWORDS, get_kinship_table_markdown
        
        normalized_q = query.lower()
        is_family_related = any(k in normalized_q for k in KINSHIP_KEYWORDS)
        
        kinship_context = ""
        if is_family_related:
            kinship_context = get_kinship_table_markdown()
            print("👨‍👩‍👧‍👦 Family intent detected: Injecting Kinship Table into context")
            
        # Build XML sections for RAG documents
        xml_chunks = []
        for c in context_chunks:
             # Basic cleanup to avoid breaking XML
             safe_content = c['content'].replace('<', '&lt;').replace('>', '&gt;')
             xml_chunks.append(f"<documento source='{c.get('article_ref', 'Documento')}'>\n{safe_content}\n</documento>")
        
        docs_xml = "\n".join(xml_chunks)
        
        # Assemble <contexto_interno>
        context_text = "<contexto_interno>\n"
        
        if structured_data:
             # Extract metadata for XML attributes
             # Default to 2025 as dynamic retrieval is complex without deeper refactoring
             # Ideally this comes from the CalculatorService, but user_context is a good proxy for intent.
             safe_year = "2025" 
             safe_group = user_context.get('job_group', 'Generico') if user_context else 'Generico'
             safe_level = user_context.get('salary_level', 'Generico') if user_context else 'Generico'
             
             context_text += f"<tabla_salarial año='{safe_year}' grupo='{safe_group}' nivel='{safe_level}'>\n{structured_data}\n</tabla_salarial>\n"

        if kinship_context:
            context_text += f"<tabla_parentesco>\n{kinship_context}\n</tabla_parentesco>\n"
            
        context_text += f"<documentos_rag>\n{docs_xml}\n</documentos_rag>\n"
        context_text += "</contexto_interno>"

        
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
        
        # --- HISTORY FORMATTING ---
        history_text = ""
        if history:
            # Take last 6 messages to update context
            recent_history = history[-6:] 
            history_text = "HISTORIAL DE CONVERSACIÓN RECIENTE:\n"
            for msg in recent_history:
                role = "User" if msg.get('role') == 'user' else "Assistant"
                content = msg.get('content', '').replace('\n', ' ')
                history_text += f"- {role}: {content}\n"
            history_text += "\n"

        # Assemble <contexto_interno>
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
        
        # Prompt más flexible que permite usar búsqueda externa HÍBRIDA
        final_prompt = f"""
            {system_prompt}

            {user_info}
            
            {history_text}
            
            CONTEXTO INTERNO (Prioridad MÁXIMA - "La Biblia"):
            {context_text}
            
            PREGUNTA DEL USUARIO:
            {query}
            
            INSTRUCCIONES DE BÚSQUEDA Y JERARQUÍA (Modo "Mini-GPT"):
            1. **PRIORIDAD CONDICIONAL**:
               - Para **NORMATIVA INTERNA** (Salarios, Parentescos, Artículos del Convenio vigentes): TUs documentos ("Contexto Interno") son la autoridad máxima.
               - Para **ACTUALIDAD Y NOVEDADES** (Huelgas, nuevos convenios en negociación, noticias, leyes recién aprobadas): **GOOGLE SEARCH MANDA**. Si buscas y encuentras algo nuevo, ÚSALO.
            
            2. **MECANISMO DE RESPUESTA**: 
               - Si buscas fuera y encuentras información (ej: "Huelga desconvocada ayer"), **dilo claramente**. NO digas "no aparece en mis documentos", di "Según últimas noticias...".
               - Si tu contexto interno habla del "V Convenio" y el usuario pregunta por el "Sexto", USA GOOGLE para saber si existe. Si Google dice que se está negociando, ÉSA ES LA RESPUESTA.
            
            3. **FORMATO**: 
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
                    "tools": [
                        {"google_search": {}},
                        # {"function_declarations": [self.calculator_tool_schema]}
                    ],
                    "safetySettings": [
                        {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_ONLY_HIGH"},
                        {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_ONLY_HIGH"},
                        {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_ONLY_HIGH"},
                        {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_ONLY_HIGH"},
                    ]
                }
                
                # Make the request
                headers = {'Content-Type': 'application/json'}
                response = requests.post(url, headers=headers, data=json.dumps(payload))
                
                if response.status_code == 200:
                    result = response.json()
                    candidates = result.get('candidates', [])
                    if candidates:
                        content_parts = candidates[0].get('content', {}).get('parts', [])
                        
                        # Check for function call
                        function_call = None
                        for part in content_parts:
                            if 'functionCall' in part:
                                function_call = part['functionCall']
                                break
                        
                        if function_call:
                             # ... function call logic ...
                             pass 
                             
                        # Get text response
                        try:
                            text_response = content_parts[0].get('text', '')
                            
                            # Clean up
                            if not text_response:
                                text_response = "Lo siento, no he podido generar una respuesta."
                            
                            # --- AUDIT PHASE ---
                            from app.services.auditor_service import auditor_service
                            from app.utils.audit_logger import log_audit_event
                            
                            print("🕵️ Auditing response...")
                            audit_result = auditor_service.audit_response(
                                query=query,
                                response_text=text_response,
                                context_text=context_text
                            )
                            
                            is_approved = audit_result.get("aprobado", False)
                            risk_level = audit_result.get("nivel_riesgo", "UNKNOWN")
                            
                            # Log it
                            log_audit_event(
                                query=query,
                                intent=intent,
                                response=text_response,
                                context=context_text,
                                auditor_result=audit_result
                            )
                            
                            # Enforce Block
                            if not is_approved and risk_level == "ALTO":
                                print(f"🛑 REJECTED by Auditor: {audit_result.get('razon')}")
                                return {
                                    "text": "Lo siento, mi auditor interno ha bloqueado esta respuesta por seguridad jurídica (Posible inexactitud detectada). Por favor, reformula la pregunta o contacta con RRHH.",
                                    "audit": {"verified": False, "risk_level": "ALTO", "reason": audit_result.get("razon", "Blocked")}
                                }
                            
                            # Return structured object
                            return {
                                "text": text_response,
                                "audit": {
                                    "verified": is_approved,
                                    "risk_level": risk_level,
                                    "reason": audit_result.get("razon", "OK")
                                }
                            }
                            
                        except (KeyError, IndexError) as e:
                             print(f"Error parsing Gemini response: {e}")
                             return {"text": "Error interno al procesar la respuesta.", "audit": None}
                             
            except Exception as e:
                print(f"API Error: {e}")
                return {"text": "Error de conexión con el servicio de IA.", "audit": None}
        
        return {"text": "No se ha configurado la API Key de Google.", "audit": None}

rag_engine = RagEngine()
