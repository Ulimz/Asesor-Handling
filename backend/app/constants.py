"""
Constants for the RAG engine and data processing.
"""

# Embedding model configuration
EMBEDDING_MODEL_NAME = 'all-MiniLM-L6-v2'
EMBEDDING_DIMENSION = 384  # Output dimension of all-MiniLM-L6-v2

# Context and history limits
HISTORY_CONTEXT_MESSAGES = 3  # Number of previous messages to include in context
MAX_CONTEXT_CHARS = 8000  # Maximum characters for Gemini context (~2000 tokens)

# Valid company slugs
VALID_COMPANIES = [
    'azul',
    'iberia', 
    'groundforce',
    'swissport',
    'menzies',
    'wfs',
    'aviapartner',
    'easyjet'
]

# Semantic enrichment keywords
SALARY_KEYWORDS = "salario, sueldo, nómina, cobro, retribución, tablas salariales"
