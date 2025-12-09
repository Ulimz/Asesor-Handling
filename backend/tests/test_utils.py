"""
Basic test suite for utility functions.
Tests company detection and other utilities.
"""
import pytest
from app.utils.company_detector import detect_company_from_filename, detect_category_from_filename

class TestCompanyDetector:
    """Tests for company detection utility."""
    
    def test_detect_iberia(self):
        assert detect_company_from_filename("iberia_convenio.json") == "iberia"
        assert detect_company_from_filename("IBERIA_2024.json") == "iberia"
    
    def test_detect_azul(self):
        assert detect_company_from_filename("azul_handling.json") == "azul"
    
    def test_detect_groundforce(self):
        assert detect_company_from_filename("groundforce_convenio.json") == "groundforce"
    
    def test_detect_estatuto(self):
        assert detect_company_from_filename("estatuto_trabajadores.json") == "General"
    
    def test_detect_unknown(self):
        assert detect_company_from_filename("unknown_file.json") == "general"
        assert detect_company_from_filename("random.json") == "general"
    
    def test_case_insensitive(self):
        assert detect_company_from_filename("IBERIA.json") == "iberia"
        assert detect_company_from_filename("IbErIa.json") == "iberia"

class TestCategoryDetector:
    """Tests for category detection utility."""
    
    def test_detect_estatuto(self):
        assert detect_category_from_filename("estatuto_trabajadores.json") == "Estatuto"
    
    def test_detect_jurisprudencia(self):
        assert detect_category_from_filename("jurisprudencia_2024.json") == "Jurisprudencia"
    
    def test_detect_convenio(self):
        assert detect_category_from_filename("iberia_convenio.json") == "Convenio"
        assert detect_category_from_filename("azul.json") == "Convenio"
