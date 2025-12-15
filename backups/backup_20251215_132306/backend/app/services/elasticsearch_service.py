from elasticsearch import Elasticsearch
import os
from dotenv import load_dotenv

load_dotenv()

ES_HOST = os.getenv("ELASTICSEARCH_HOST", "localhost")
ES_PORT = os.getenv("ELASTICSEARCH_PORT", "9200")

es = Elasticsearch(f"http://{ES_HOST}:{ES_PORT}")

def index_document(index: str, doc_id: str, body: dict):
    es.index(index=index, id=doc_id, body=body)

def search_documents(index: str, query: str, filters: dict = None, size: int = 10):
    body = {
        "query": {
            "bool": {
                "must": [
                    {
                        "multi_match": {
                            "query": query,
                            "fields": ["title^2", "content", "tags^1.5"]
                        }
                    }
                ],
                "filter": []
            }
        }
    }

    if filters:
        for key, value in filters.items():
            if value:
                body["query"]["bool"]["filter"].append({"term": {key: value}})

    res = es.search(index=index, body=body, size=size)
    return res["hits"]["hits"]
