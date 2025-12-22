from sentence_transformers import SentenceTransformer
from sqlalchemy import select, func
from sqlalchemy.orm import Session
from app.db.models import DocumentChunk, LegalDocument
import numpy as np
import google.generativeai as genai
import os
import requests
import json
import logging
from datetime import datetime
from app.constants import (
    EMBEDDING_MODEL_NAME,
    EMBEDDING_DIMENSION,
    HISTORY_CONTEXT_MESSAGES,
    MAX_CONTEXT_CHARS
)
from app.prompts import PROMPT_TEMPLATES, IntentType
from app.services.calculator_service import CalculatorService
from app.services.query_expander import QueryExpander
from app.services.legal_anchors import LegalAnchors
from app.services.hybrid_calculator import HybridSalaryCalculator, SalaryData, CalculationResult
from app.schemas.salary import CalculationRequest
from sqlalchemy.orm import Session # Typed typing
import re

logger = logging.getLogger(__name__)

# ✅ MEJORA EXPERTA: Keywords para pre-clasificación laboral
LEGAL_KEYWORDS = {
    "vacaciones", "permiso", "permisos", "rotacion", "rotación",
    "turnos", "turno", "jornada", "festivos", "festivo",
    "horas", "hora", "bajas", "baja", "licencias", "licencia",
    "antiguedad", "antigüedad", "pluses", "plus",
    "categoria", "categoría", "nivel", "salario", "nomina", "nómina",
    "retribucion", "retribuciones", "convenio", "estatuto", "tabla"
}

class RagEngine:
    def __init__(self):
        # Lazy loading: model will be loaded on first use
        self._model = None
        
        # Initialize Query Expander (Capa 1: Hybrid RAG)
        self.query_expander = QueryExpander()
        
        # Initialize Legal Anchors (Capa 2: Hybrid RAG)
        self.legal_anchors = LegalAnchors()
        
        # Initialize Gemini (free tier) if key is present
        api_key = os.getenv("GOOGLE_API_KEY")
        self.gen_model = None
        if api_key:
            genai.configure(api_key=api_key)
            # Use 2.0-flash and direct REST call for grounding to bypass SDK tool validation issues
            self.gen_model = genai.GenerativeModel('gemini-2.0-flash')
            
            # ✅ FASE 2: Initialize Hybrid Calculator
            self.hybrid_calculator = HybridSalaryCalculator(
                gemini_model=genai.GenerativeModel('gemini-2.0-flash-exp')
            )
        else:
            self.hybrid_calculator = None

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

    def detect_intent(self, query: str, company_slug: str = None) -> IntentType:
        """
        Detect user intent based on keywords.
        Now includes Profile-Based Pre-classification to prevent 'GENERAL' intent degradation.
        """
        # 0. Pre-classification by Profile
        pre_classification = None
        if company_slug:
             pre_classification = self._preclassify_by_profile(query, company_slug)
             # Note: We don't return early here because we want to check standard intents too
             # but we save the result to use it as an override layer at step 4.

        q = query.lower()
        
        # 1. Dismissal / Resignation (baja voluntaria)
        if any(k in q for k in ['despido', 'despedi', 'extinción', 'finiquito', 'indemnización', 'disciplinario', 'improcedente', 'baja voluntaria']):
            return IntentType.DISMISSAL
            
        # 2. Leave / Tine / Sickness (Incapacidad Temporal)
        if any(k in q for k in ['vacaciones', 'permiso', 'día libre', 'boda', 'nacimiento', 'hospitalización', 'excedencia', 'reducción', 'baja', 'enfermedad', 'accidente', 'médico', 'it', 'incapacidad']):
            return IntentType.LEAVE
            
        # 3. Salary / Money (Only if not already categorized above)
        if any(k in q for k in ['precio', 'salario', 'cobrar', 'retribución', 'paga', 'sueldo', 'plus', 'hora', 'festiva', 'nocturnidad', 'tabla', 'anexo', 'euros', '€']):
            return IntentType.SALARY

        # 4. Profile-Based Override for ambiguous cases (e.g. "rotacion 4x4", "jornada")
        if pre_classification:
             logger.info(f"🛡️ detect_intent: Override GENERAL -> LEAVE/SALARY due to Employment Profile")
             if "salario" in q or "nomina" in q or "cobrar" in q or "plus" in q:
                 return IntentType.SALARY
             return IntentType.LEAVE
            
        return IntentType.GENERAL

    def _preclassify_by_profile(self, query: str, company_slug: str) -> dict | None:
        """
        Pre-clasifica la query usando perfil del usuario (company_slug) y keywords.
        Si el usuario tiene empresa asignada y pregunta sobre temas laborales,
        forzamos el contexto laboral ANTES de que el LLM decida.
        """
        if not company_slug:
            return None

        # Normalización robusta (palabras + patrones tipo 4x4)
        q = query.lower()
        tokens = set(re.findall(r"[a-záéíóúüñ]+|\d+|\d+x\d+", q))
        
        # Intersección
        matched = tokens & LEGAL_KEYWORDS
        
        if matched:
            logger.info(f"⚡ Pre-clasificación Laboral activada: {matched}")
            return {
                "intent_override": True,
                "requiere_tablas": True,
                "domain": "LABORAL",
                "matched_keywords": list(matched),
                "trigger": "keyword_match"
            }
        return None

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
        
        # ===== CAPA 1: QUERY EXPANSION (Hybrid RAG) =====
        # Expand query to legal keywords using Gemini Flash
        expansion = self.query_expander.expand(query)
        expanded_query = self.query_expander.get_expanded_query_text(expansion)
        intent = expansion['intent']
        requiere_tablas = expansion['requiere_tablas']
        
        print(f"🔍 Query Expansion:")
        print(f"   Original: '{query}'")
        print(f"   Intent: {intent}")
        print(f"   Requiere tablas: {requiere_tablas}")
        print(f"   Expanded: '{expanded_query}'")
        
        # ✨ FASE 2: Detectar si es query de cálculo
        is_calculation = self._is_calculation_query(query)
        if is_calculation:
            print(f"🧮 Calculation query detected!")
        # 3. Legal Anchors (Capa 2) - Determinista
        anchor_results = []
        if expansion.get("requiere_tablas") or expansion.get("domain") == "LABORAL" or intent in ["LEAVE", "SALARY", "DISMISSAL"]:
            # ✅ MEJORA: Pasar SIEMPRE company_slug para filtrar por convenio del usuario
            logger.info(f"Legal Anchors: buscando anchors para {expansion['intent']} en {company_slug}")
            anchor_results = self.legal_anchors.get_anchors(
                intent=expansion['intent'],
                db=db,
                company_slug=company_slug, # Clave: el usuario define el contexto
                limit=3
            )
            
            # Si encontramos anchors, añadirlos al contexto para RAG
            if anchor_results:
                logger.info(f"✅ Anchors encontrados: {len(anchor_results)}")
                
                # Detectar cálculo si tenemos anchors
                if self._is_calculation_query(query):
                    calc = self._handle_calculation(
                        query=query,
                        expansion=expansion,
                        anchor_results=anchor_results,
                        company_slug=company_slug
                    )
                    
                    if calc.get("calculation"):
                         return [{
                            "id": anchor_results[0].id,
                            "content": calc["answer"],
                            "article_ref": "Cálculo",
                            "document": anchor_results[0].document,
                            "calculation": calc["calculation"],
                            'score': 1.0  # Perfect score for calculations
                        }]
                else:
                    print("   ⚠️ Calculation failed, falling back to standard RAG")
            else:
                print("   ⚠️ No anchor tables found, falling back to standard RAG")
        
        # FILTRO CHIT-CHAT: Ahorra costes de embeddings y retrieval
        if intent == "GENERAL" and not requiere_tablas and len(query.split()) < 2:
             print("💬 Chit-chat detectado (muy corto). Saltando retriever.")
             return []

        search_text = expanded_query if expanded_query else query
        query_embedding = self.generate_embedding(search_text)
        
        # Búsqueda Vectorial Base
        from sqlalchemy.orm import joinedload
        stmt = select(DocumentChunk).join(LegalDocument).options(
            joinedload(DocumentChunk.document)  # Eager load to prevent N+1 queries
        ).order_by(
            DocumentChunk.embedding.cosine_distance(query_embedding)
        )
        
        if company_slug:
            stmt = stmt.filter(
                (LegalDocument.company == company_slug) | 
                (LegalDocument.company.is_(None)) |
                (LegalDocument.company.ilike('general'))
            )

        stmt = stmt.limit(limit)
        base_results = list(db.execute(stmt).scalars().all())

        # Lista final acumulativa para mantener orden
        final_results_list = []
        seen_ids = set()

        # 1. Búsqueda de Artículo Específico (Prioridad Alta)
        import re
        art_match = re.search(r'art[ií]culo\s+(\d+)', query, re.IGNORECASE)
        estatuto_match = re.search(r'estatuto', query, re.IGNORECASE)
        
        if art_match:
            art_num = art_match.group(1)
            print(f"📜 Article reference detected: {art_num}")
            art_filter = DocumentChunk.article_ref.ilike(f'%Art%culo {art_num}%')
            doc_filter = None
            if estatuto_match:
                 print(f"   ⚖️  'Estatuto' detected, narrowing search.")
                 doc_filter = LegalDocument.title.ilike('%Estatuto%')
            elif company_slug:
                 doc_filter = (LegalDocument.company == company_slug) | (LegalDocument.company.ilike('general'))
            
            if doc_filter is not None:
                priority_stmt = select(DocumentChunk).join(LegalDocument).filter(doc_filter & art_filter).limit(3)
                priority_results = list(db.execute(priority_stmt).scalars().all())
                
                # Añadimos directamente a lista final
                for pr in priority_results:
                    if pr.id not in seen_ids:
                        print(f"   ⭐⭐ SPECIFIC ARTICLE Force-added: {pr.article_ref}")
                        final_results_list.append(pr)
                        seen_ids.add(pr.id)

        # 2. Búsqueda Híbrida de Tablas/Anexos (Si es Salario)
        salary_keywords = ['precio', 'salario', 'retribución', 'retribucion', 'paga', 'sueldo', 
                          'complemento', 'plus', 'extraordinaria', 'perentoria',
                          'nocturna', 'festiva', 'tabla', 'anexo', 'euros', '€']
        
        is_salary_query = any(k in query.lower() for k in salary_keywords)
        
        if is_salary_query and company_slug:
            print(f"💰 Salary intent detected in search: forcing retrieval of ANEXOs/Tablas")
            
            priority_stmt = select(DocumentChunk).join(LegalDocument).filter(
                (LegalDocument.company == company_slug) &
                ((DocumentChunk.article_ref.ilike('%ANEXO%')) | (DocumentChunk.article_ref.ilike('%TABLA%')))
            ).order_by(
                func.length(DocumentChunk.content).desc()
            )
            
            if "pmr" not in query.lower():
                 priority_stmt = priority_stmt.filter(
                     ~DocumentChunk.article_ref.ilike('%PMR%'),
                     ~DocumentChunk.content.ilike('%PMR%')
                 )

            priority_stmt = priority_stmt.limit(3)
            anexo_results = list(db.execute(priority_stmt).scalars().all())
            
            for ar in anexo_results:
                if ar.id not in seen_ids:
                    print(f"   ⭐⭐ PRIORITY Force-added: {ar.article_ref}")
                    final_results_list.append(ar)
                    seen_ids.add(ar.id)
            
            # General Fallback
            anexo_stmt = select(DocumentChunk).join(LegalDocument).filter(
                (LegalDocument.company == company_slug) &
                ((DocumentChunk.article_ref.ilike('%ANEXO%')) | (DocumentChunk.article_ref.ilike('%TABLA%')))
            )
            if "pmr" not in query.lower():
                 anexo_stmt = anexo_stmt.filter(~DocumentChunk.article_ref.ilike('%PMR%'))
            
            anexo_fallback_results = db.execute(anexo_stmt.limit(5)).scalars().all()
            for ar in anexo_fallback_results:
                if ar.id not in seen_ids:
                     final_results_list.append(ar)
                     seen_ids.add(ar.id)

        # 3. Anchors (Determinista)
        anchor_results = []
        if requiere_tablas or intent in ["LEAVE", "SALARY", "DISMISSAL"] or expansion.get("domain") == "LABORAL":
            print(f"⚓ Inyectando Legal Anchors para Intent: {intent}")
            anchor_results = self.legal_anchors.get_anchors(intent, db, company_slug, limit=2)
            
             # Insert anchors AT THE TOP if we have them
            for ar in reversed(anchor_results): # Reverse to keep order when inserting at 0
                 if ar.id not in seen_ids:
                     print(f"   ⚓ ANCHOR Injected: {ar.article_ref}")
                     final_results_list.insert(0, ar)
                     seen_ids.add(ar.id)
            
            # Detectar cálculo si tenemos anchors
            if anchor_results and self._is_calculation_query(query):
                calc = self._handle_calculation(
                    query=query,
                    expansion=expansion,
                    anchor_results=anchor_results,
                    company_slug=company_slug
                )
                if calc.get("calculation"):
                        return [{
                        "id": anchor_results[0].id,
                        "content": calc["answer"],
                        "article_ref": "Cálculo",
                        "document": anchor_results[0].document,
                        "calculation": calc["calculation"],
                        'score': 1.0
                    }]

        # 4. Añadir resultados vectoriales base (relleno)
        for br in base_results:
            if br.id not in seen_ids:
                final_results_list.append(br)
                seen_ids.add(br.id)
        
        # Limitar al número solicitado
        unique_chunks = final_results_list[:limit]
        
        print(f"📊 Resultados finales: {len(unique_chunks)} chunks únicos")

        # Format results
        formatted_results = []
        for chunk in unique_chunks:
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
        # ✅ CORRECCIÓN: Evitar crash si history es None
        history = history or []
        
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
        
        # FIX: Permitir enriquecimiento SIMULTÁNEO (Dinero + Baja)
        if is_salary_query and 'anexo' not in rewritten_lower:
            rewritten = f"{rewritten} ANEXO tabla salarial retribución"
            print(f"💰 Salary query detected (post-merge), enhanced to search in ANEXOS")
            rewritten_lower = rewritten.lower() # Update for next check
            
        if is_it_query:
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
        try:
            response = self.gen_model.generate_content(final_prompt)
            return {"text": response.text, "audit": None}
        except Exception as e:
            print(f"API Error: {e}")
            return {"text": "Error de conexión con el servicio de IA.", "audit": None}
        
        return {"text": "No se ha configurado la API Key de Google.", "audit": None}
    
    # ✅ FASE 2: Métodos de Calculadora Híbrida
    
    def _normalize_text(self, text: str) -> str:
        """Quita tildes y pasa a minúsculas para comparación robusta."""
        import unicodedata
        return ''.join(
            c for c in unicodedata.normalize('NFD', text)
            if unicodedata.category(c) != 'Mn'
        ).lower()
    
    def _is_calculation_query(self, query: str) -> bool:
        """
        Detecta si la query requiere cálculo.
        
        Mejora del experto: Requiere (Operación) Y (Contexto o Números)
        Mejora adicional: Requiere mención de DOS niveles para comparación
        
        Ejemplos que SÍ detecta:
        - "diferencia salarial nivel 3 y 4"
        - "incremento entre nivel 2 y nivel 3"
        - "comparar nivel 1 vs nivel 2"
        
        Ejemplos que NO detecta:
        - "cuanto cobra nivel 4" (solo un nivel)
        - "diferencia entre vacaciones" (sin contexto salarial)
        """
        # Normalizar query (quitar tildes: cuánto -> cuanto)
        q = self._normalize_text(query)
        
        # 1. Keywords de operación (Intención de cálculo) - SIN TILDES
        op_keywords = [
            'diferencia', 'cuanto mas', 'cuanto menos',  # sin tildes
            'incremento', 'aumento', 'reduccion',  # sin tildes
            'comparar', 'vs', 'versus', 'calcular', 'calcula', 'entre'
        ]
        
        # 2. Keywords de contexto (Sobre qué calculamos) - SIN TILDES
        context_keywords = [
            'nivel', 'grupo', 'salario', 'sueldo', 'cobrar', 'paga', 'plus', 
            'retribucion', 'bruto', 'neto', 'anual', 'mensual'  # sin tildes
        ]
        
        # 3. Verificar que menciona DOS niveles/grupos
        # Buscar patrones como "nivel 3 y 4", "nivel 3 y nivel 4", "grupo A y B"
        import re
        
        # Patrones de comparación explícita
        comparison_patterns = [
            r'nivel\s+\d+\s+y\s+\d+',  # "nivel 3 y 4"
            r'nivel\s+\d+\s+y\s+nivel\s+\d+',  # "nivel 3 y nivel 4"
            r'grupo\s+\w+\s+y\s+\w+',  # "grupo A y B"
            r'nivel\s+\d+\s+vs\s+\d+',  # "nivel 3 vs 4"
            r'nivel\s+\d+\s+versus\s+\d+',  # "nivel 3 versus 4"
            r'entre\s+nivel\s+\d+\s+y\s+\d+',  # "entre nivel 3 y 4"
        ]
        
        has_comparison = any(re.search(pattern, q) for pattern in comparison_patterns)
        
        # Lógica: Debe tener (Operación) Y (Contexto o Números) Y (Comparación explícita)
        has_op = any(kw in q for kw in op_keywords)
        has_context = any(kw in q for kw in context_keywords)
        has_numbers = any(char.isdigit() for char in q)  # "nivel 3" tiene dígito
        
        # Solo disparamos cálculo si hay:
        # - Intención de operar
        # - Contexto financiero O números
        # - Comparación explícita de dos niveles
        return has_op and (has_context or has_numbers) and has_comparison
    
    def _handle_calculation(
        self,
        query: str,
        expansion: dict,
        anchor_results: list,
        company_slug: str,
    ) -> dict:
        """Maneja queries de cálculo con calculadora híbrida."""
        
        if not self.hybrid_calculator:
            logger.warning("Hybrid calculator not initialized")
            return {"calculation": None}

        if not anchor_results:
            logger.warning("No hay tablas para calcular")
            return {
                "answer": "No encontré tablas salariales para realizar el cálculo.",
                "sources": [],
                "calculation": None,
            }

        # FIX ROBUSTO: Iterar sobre anchors y PROBAR si podemos extraer datos
        # No basta con que parezca una tabla, tiene que contener los niveles que buscamos.
        salary_data = None
        target_chunk = None

        for anchor in anchor_results:
            # Filtro básico de tipo (ya existente)
            is_table = anchor.chunk_metadata.get("type") == "table"
            is_anexo = "anexo" in anchor.article_ref.lower() or "tabla" in anchor.article_ref.lower()
            
            if not (is_table or is_anexo):
                continue

            # Intentar extracción con este anchor
            try:
                chunk_year = anchor.chunk_metadata.get("year")
                year = chunk_year if isinstance(chunk_year, int) else datetime.now().year
                
                logger.info(f"🔎 Probando extracción en anchor: {anchor.article_ref}")
                
                candidate_data = self.hybrid_calculator.extract_salary_data(
                    table_content=anchor.content,
                    query=query,
                    company=company_slug or "general",
                    year=year,
                )
                
                if candidate_data:
                    logger.info(f"✅ Extracción exitosa en: {anchor.article_ref}")
                    salary_data = candidate_data
                    target_chunk = anchor
                    break # ÉXITO
                else:
                    logger.warning(f"❌ Falló extracción en: {anchor.article_ref} (probablemente faltan niveles)")

            except Exception as e:
                logger.error(f"Error parseando anchor {anchor.id}: {e}")
                continue
        
        # Si después del loop nada funcionó, intentamos el fallback del primero (por si acaso)
        if not salary_data:
            logger.warning("Ningún anchor permitió la extracción. Fallback a lógica original con [0]")
            target_chunk = anchor_results[0]
            # (Aquí podríamos reintentar o simplemente fallar, pero mantenemos el flujo para que devuelva el error estándar)
            # Re-run extraction execution to generate the failure logs/return cleanly
            chunk_year = target_chunk.chunk_metadata.get("year")
            year = chunk_year if isinstance(chunk_year, int) else datetime.now().year
            salary_data = self.hybrid_calculator.extract_salary_data(
                table_content=target_chunk.content,
                query=query,
                company=company_slug or "general",
                year=year,
            )

        if not salary_data:
            logger.error("No se pudieron extraer datos de ninguna tabla")
            return {
                "answer": "No pude extraer los datos necesarios de la tabla disponible.",
                "sources": [target_chunk] if target_chunk else [],
                "calculation": None,
            }

        result = self.hybrid_calculator.calculate(salary_data)

        if not result:
            logger.error("Error en cálculo")
            return {
                "answer": "Hubo un error al realizar el cálculo.",
                "sources": [target_chunk],
                "calculation": None,
            }

        if not self.hybrid_calculator.validate_result(salary_data, result):
            logger.error("Validación falló")
            return {
                "answer": "El cálculo no pasó la validación de coherencia.",
                "sources": [table_chunk],
                "calculation": None,
            }

        answer = self._format_calculation_answer(salary_data, result)

        return {
            "answer": answer,
            "sources": [table_chunk],
            "calculation": result.to_dict(),
        }

    def _format_calculation_answer(
        self,
        data: SalaryData,
        result: CalculationResult,
    ) -> str:
        """Formatea la respuesta del cálculo."""
        
        # MEJORA 4: Formato diferente para consultas simples
        if data.is_simple_query:
            # MEJORA CRÍTICA: Default 14 pagas para sector handling España
            monthly_14 = result.level_destination_value / 14
            monthly_12 = result.level_destination_value / 12
            
            return f"""El {data.level_destination_label} cobra **{result.level_destination_value:,.2f}€** anuales.

📊 **Detalle:**
- Salario base anual: {result.level_destination_value:,.2f}€
- Salario mensual (14 pagas): {monthly_14:,.2f}€
- Salario mensual (12 pagas): {monthly_12:,.2f}€

Campo: {result.field_name}
Empresa: {data.company}
Año: {data.year}
"""
        
        # Formato para comparaciones
        return f"""La diferencia salarial es de **{result.difference:,.2f}€** anuales.

📊 **Detalle:**
- {data.level_origin_label}: {result.level_origin_value:,.2f}€/año
- {data.level_destination_label}: {result.level_destination_value:,.2f}€/año
- Diferencia: {result.difference:,.2f}€
- Incremento: {result.percentage:.2f}%

Campo comparado: {result.field_name}
Empresa: {data.company}
Año: {data.year}
"""


rag_engine = RagEngine()
