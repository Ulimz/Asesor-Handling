import os
import json
import requests
import google.generativeai as genai
from app.prompts import AUDITOR_INSTRUCTIONS

class AuditorService:
    def __init__(self):
        self.api_key = os.getenv("GOOGLE_API_KEY")
        # Use a lightweight model for auditing to keep latency low
        self.audit_model_name = "gemini-2.0-flash" 

    def audit_response(self, query: str, response_text: str, context_text: str) -> dict:
        """
        Verifies if the response is faithful to the context and query.
        Returns a dict: {"aprobado": bool, "razon": str, "nivel_riesgo": str}
        """
        if not self.api_key:
            print("⚠️ Auditor skipped: No API Key")
            return {"aprobado": True, "razon": "No API Key", "nivel_riesgo": "UNKNOWN"}

        # Construct the specialized audit prompt
        prompt = f"""{AUDITOR_INSTRUCTIONS}

        --- DATOS A VERIFICAR ---
        [PREGUNTA]: {query}

        [CONTEXTO DOCUMENTAL (Fuente de Verdad)]:
        {context_text[:15000]}  # Truncate context to avoid token limits in audit

        [RESPUESTA GENERADA]:
        {response_text}
        
        --- DICTAMEN (JSON) ---
        """

        try:
            # Direct REST call for speed and consistency
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.audit_model_name}:generateContent?key={self.api_key}"
            payload = {
                "contents": [{"parts": [{"text": prompt}]}],
                "generationConfig": {"response_mime_type": "application/json"} # Valid for newer Gemini models
            }
            
            resp = requests.post(url, json=payload, headers={'Content-Type': 'application/json'}, timeout=10)
            
            if resp.status_code == 200:
                result_json = resp.json()
                try:
                    text_content = result_json['candidates'][0]['content']['parts'][0]['text']
                    # Clean markdown code blocks if present
                    text_content = text_content.replace('```json', '').replace('```', '').strip()
                    audit_result = json.loads(text_content)
                    return audit_result
                except Exception as e:
                    print(f"⚠️ Auditor JSON parsing failed: {e}. Raw: {text_content}")
                    # Fail open or closed? Let's strictly fail closed for safety, or open for MVP?
                    # Let's Fail Closed (Reject) if we can't parse, just to be safe.
                    return {"aprobado": False, "razon": "Audit Parsing Error", "nivel_riesgo": "MEDIUM"}
                    
            else:
                 print(f"⚠️ Auditor API Error: {resp.status_code} - {resp.text}")
                 return {"aprobado": True, "razon": "Audit API Error", "nivel_riesgo": "UNKNOWN"}

        except Exception as e:
            print(f"⚠️ Auditor Exec Error: {e}")
            return {"aprobado": True, "razon": "Auditor Exception", "nivel_riesgo": "UNKNOWN"}

# Singleton instance
auditor_service = AuditorService()
