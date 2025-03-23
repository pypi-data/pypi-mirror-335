"""
RecallDB: A multi-user vector database for efficient document storage and retrieval.

RecallDB supports:
- Multiple users with isolated document access
- Flexible embedding models
- Document storage and retrieval by similarity
- Metadata filtering
- Persistent storage with PyArrow
"""

__version__ = "0.1.0"

from recall_db.recall_db import RecallDB
from recall_db.flexible_htrag import FlexibleHTRAG

# For convenience, import embedding adapters if present
try:
    from recall_db.embeddings import create_openai_adapter, create_sentence_transformer_adapter
except ImportError:
    # These might not be available if optional dependencies aren't installed
    pass

__all__ = ["RecallDB", "FlexibleHTRAG", "__version__"] 