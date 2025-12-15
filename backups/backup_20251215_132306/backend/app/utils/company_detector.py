"""
Utility for detecting company from filename.
Centralizes company detection logic used across multiple seed scripts.
"""
from typing import Dict

COMPANY_KEYWORDS: Dict[str, str] = {
    'iberia': 'iberia',
    'groundforce': 'groundforce',
    'swissport': 'swissport',
    'aviapartner': 'aviapartner',
    'azul': 'azul',
    'easyjet': 'easyjet',
    'menzies': 'menzies',
    'wfs': 'wfs',
    'clece': 'clece',
    'talher': 'clece',
    'acciona': 'acciona',
    'estatuto': 'General',
}

def detect_company_from_filename(filename: str) -> str:
    """
    Detect company from filename using keyword matching.
    
    Args:
        filename: The filename to analyze (case-insensitive)
        
    Returns:
        Company identifier string, defaults to 'general' if no match
        
    Examples:
        >>> detect_company_from_filename("iberia_convenio.json")
        'iberia'
        >>> detect_company_from_filename("unknown_file.json")
        'general'
    """
    filename_lower = filename.lower()
    
    for keyword, company in COMPANY_KEYWORDS.items():
        if keyword in filename_lower:
            return company
    
    return 'general'

def detect_category_from_filename(filename: str) -> str:
    """
    Detect document category from filename.
    
    Args:
        filename: The filename to analyze
        
    Returns:
        Category string: 'Estatuto', 'Jurisprudencia', or 'Convenio'
    """
    filename_lower = filename.lower()
    
    if 'estatuto' in filename_lower:
        return 'Estatuto'
    elif 'jurisprudencia' in filename_lower:
        return 'Jurisprudencia'
    else:
        return 'Convenio'
