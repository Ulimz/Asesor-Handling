"""
Constants for the RAG engine and data processing.
"""

# Embedding model configuration
EMBEDDING_MODEL_NAME = 'all-MiniLM-L6-v2'
EMBEDDING_DIMENSION = 384  # Output dimension of all-MiniLM-L6-v2

# Context and history limits
HISTORY_CONTEXT_MESSAGES = 3  # Number of previous messages to include in context
MAX_CONTEXT_CHARS = 60000  # Maximum characters for Gemini context (increased to support large tables)

# Valid company slugs
VALID_COMPANIES = [
    'azul',
    'azul-handling',
    'iberia', 
    'groundforce',
    'swissport',
    'menzies',
    'wfs',
    'aviapartner',
    'easyjet',
    'convenio-sector',
    'jet2',
    'norwegian',
    'south'
]

# Companies that adhere to the Convenio Sector (General Agreement)
# These companies don't have their own specific agreements and use the sector-wide terms
SECTOR_COMPANIES = ['jet2', 'norwegian', 'south']

# Semantic enrichment keywords
SALARY_KEYWORDS = "salario, sueldo, nómina, cobro, retribución, tablas salariales"
