"""
Unit tests for Query Expander
"""
import pytest
from unittest.mock import patch, Mock
from app.services.query_expander import QueryExpander

class TestQueryExpander:
    """Test suite for QueryExpander service."""
    
    def test_fallback_when_no_api_key(self):
        """Test that expander falls back gracefully when API key is missing."""
        with patch.dict('os.environ', {}, clear=True):
            expander = QueryExpander()
            result = expander.expand("test query")
            
            assert result["intent"] == "GENERAL"
            assert "test query" in result["keywords_busqueda"]
            assert result["grado_parentesco"] is None
    
    def test_parse_json_with_markdown(self):
        """Test JSON parsing from markdown code blocks."""
        expander = QueryExpander()
        
        text = '''```json
{
  "intent": "LEAVE",
  "keywords_busqueda": ["permiso"],
  "entidades": ["tío"],
  "grado_parentesco": 3
}
```'''
        
        result = expander._parse_json_response(text)
        assert result["intent"] == "LEAVE"
        assert result["grado_parentesco"] == 3
    
    def test_parse_plain_json(self):
        """Test JSON parsing without markdown."""
        expander = QueryExpander()
        
        text = '{"intent": "SALARY", "keywords_busqueda": ["salario"], "entidades": [], "grado_parentesco": null}'
        
        result = expander._parse_json_response(text)
        assert result["intent"] == "SALARY"
    
    @patch('requests.post')
    def test_successful_expansion(self, mock_post):
        """Test successful query expansion with mocked API."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "candidates": [{
                "content": {
                    "parts": [{
                        "text": '{"intent": "LEAVE", "keywords_busqueda": ["permiso retribuido", "tercer grado"], "entidades": ["tío"], "grado_parentesco": 3}'
                    }]
                }
            }]
        }
        mock_post.return_value = mock_response
        
        with patch.dict('os.environ', {'GOOGLE_API_KEY': 'test_key'}):
            expander = QueryExpander()
            result = expander.expand("mi tío está malo")
            
            assert result["intent"] == "LEAVE"
            assert "tercer grado" in result["keywords_busqueda"]
            assert result["grado_parentesco"] == 3
    
    @patch('requests.post')
    def test_api_error_fallback(self, mock_post):
        """Test fallback when API returns error."""
        mock_post.side_effect = Exception("API Error")
        
        with patch.dict('os.environ', {'GOOGLE_API_KEY': 'test_key'}):
            expander = QueryExpander()
            result = expander.expand("test query")
            
            # Should fallback gracefully
            assert result["intent"] == "GENERAL"
            assert "test query" in result["keywords_busqueda"]
    
    def test_get_expanded_query_text(self):
        """Test conversion of expansion to search text."""
        expander = QueryExpander()
        
        expansion = {
            "intent": "LEAVE",
            "keywords_busqueda": ["permiso retribuido", "enfermedad grave"],
            "entidades": ["tío"],
            "grado_parentesco": 3
        }
        
        text = expander.get_expanded_query_text(expansion)
        assert text == "permiso retribuido enfermedad grave"

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
