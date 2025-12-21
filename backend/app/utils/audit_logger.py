import os
import json
import logging
from datetime import datetime
import hashlib

# Configure logging to a file in the root 'logs' directory
# Assuming this file is in backend/app/utils/
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.join(current_dir, '..', '..', '..') # Go up to Asistente_Handling
log_dir = os.path.join(project_root, 'logs')
os.makedirs(log_dir, exist_ok=True)
log_file = os.path.join(log_dir, 'audit.jsonl')

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("audit_logger")

def log_audit_event(query: str, intent: str, response: str, context: str, auditor_result: dict):
    """
    Logs the RAG interaction and Audit result to a JSONL file.
    Hashes the context to ensure data integrity without storing massive text blobs.
    """
    try:
        # Create a hash of the context to track what the model "saw"
        # This is useful for debugging: "Why did it say X? Because Context Hash was Y"
        context_hash = hashlib.sha256(context.encode('utf-8', errors='ignore')).hexdigest()
        
        event = {
            "timestamp": datetime.now().isoformat(),
            "query": query,
            "intent": intent,
            "response_snippet": response[:500] + "..." if len(response) > 500 else response,
            "context_hash": context_hash,
            "auditor_verdict": {
                "approved": auditor_result.get("aprobado", False),
                "reason": auditor_result.get("razon", "Unknown"),
                "risk": auditor_result.get("nivel_riesgo", "UNKNOWN")
            }
        }
        
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(event, ensure_ascii=False) + '\n')
            
    except Exception as e:
        logger.error(f"Failed to log audit event: {e}")
