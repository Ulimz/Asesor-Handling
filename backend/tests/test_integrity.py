import pytest
import os
import json
import sys
from sqlalchemy import text

# Add backend to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db.database import SessionLocal
from app.db.models import LegalDocument, DocumentChunk

class TestDataIntegrity:
    
    def setup_method(self):
        self.db = SessionLocal()
        # Path to parsed XMLs
        self.json_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "xml_parsed")

    def teardown_method(self):
        self.db.close()

    def test_json_structure(self):
        """Verify all JSON files have required fields"""
        if not os.path.exists(self.json_dir):
            pytest.skip(f"JSON directory {self.json_dir} not found")
            
        json_files = [f for f in os.listdir(self.json_dir) if f.endswith('.json')]
        assert len(json_files) > 0, "No JSON files found to test"
        
        for json_file in json_files:
            file_path = os.path.join(self.json_dir, json_file)
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            # Check Critical Fields
            assert 'title' in data, f"{json_file} missing 'title'"
            assert 'articles' in data, f"{json_file} missing 'articles'"
            assert isinstance(data['articles'], list), f"{json_file} 'articles' must be a list"
            assert len(data['articles']) > 0, f"{json_file} has 0 articles"
            
            # Check Article Structure
            for idx, article in enumerate(data['articles']):
                assert 'article' in article, f"{json_file} article {idx} missing 'article' name"
                assert 'content' in article, f"{json_file} article {idx} missing 'content'"
                assert len(article['content'].strip()) > 0, f"{json_file} article {idx} has empty content"

    def test_database_documents_have_chunks(self):
        """Verify every LegalDocument in DB has at least one DocumentChunk"""
        # Get all documents
        docs = self.db.query(LegalDocument).all()
        if not docs:
            pytest.skip("No documents in database")
            
        for doc in docs:
            chunk_count = self.db.query(DocumentChunk).filter(DocumentChunk.document_id == doc.id).count()
            assert chunk_count > 0, f"Document ID {doc.id} ({doc.title}) has 0 chunks"

    def test_no_orphan_chunks(self):
        """Verify no chunks exist without a parent document"""
        orphans = self.db.query(DocumentChunk).filter(DocumentChunk.document_id.is_(None)).count()
        assert orphans == 0, f"Found {orphans} chunks without document_id"
        
        # Also check referential integrity (id points to non-existent doc)
        # This is strictly handled by FK, but good to verify if logical del happened
        # (Assuming physical FK exists, this test might raise error or return 0)
        
    def test_versioning_columns_exist(self):
        """Verify updated_at and version columns are queryable"""
        try:
            self.db.execute(text("SELECT updated_at, version FROM legal_documents LIMIT 1"))
        except Exception as e:
            pytest.fail(f"Could not query new columns: {e}")
