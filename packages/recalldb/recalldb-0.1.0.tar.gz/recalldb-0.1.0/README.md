# RecallDB: Multi-User Vector Database

RecallDB is a multi-user vector database that allows independent document access for each user. It supports vector embeddings for semantic search and efficient document retrieval.

## Features

- **Multi-user support**: Each user has their own isolated document space
- **Collection-based organization**: Group related documents into collections
- **Vector search**: Use semantic search to find relevant documents
- **Metadata filtering**: Search and filter using document metadata
- **PyArrow storage**: Efficient data storage using PyArrow's Arrow IPC format
- **Embedding models**: Support for various embedding models
- **Parallel processing**: Asynchronous/batched embeddings for faster processing
- **Chunking support**: Break large documents into manageable chunks
- **Flexible API**: Simple interface for document management and retrieval

## Installation

```bash
pip install recalldb
```

## Quick Start

```python
from recall_db import RecallDB

# Create embedding function
def embedding_function(text):
    # Your embedding logic here
    # Should return a normalized numpy array
    pass

# Initialize RecallDB
db = RecallDB(
    embedding_function=embedding_function,
    storage_path="./recalldb_data"
)

# Add documents for a user
user_id = "user123"
db.add_document(
    user_id=user_id,
    text="This is a sample document about artificial intelligence.",
    collection="ai_docs",
    metadata={"topic": "AI", "type": "introduction"}
)

# Search for documents
results = db.search(
    user_id=user_id,
    query="artificial intelligence concepts",
    collections=["ai_docs"],
    top_k=5
)

# Print results
for result in results:
    print(f"Document ID: {result['id']}")
    print(f"Content: {result['content'][:100]}...")
    print(f"Score: {result['score']}")
    print(f"Metadata: {result['metadata']}")
    print("---")
```

## Core Concepts

### Users and Data Isolation

RecallDB maintains strict data isolation between users. Each user has their own separate database instance, ensuring that:

- User A cannot access documents from User B
- Search queries are scoped to the requesting user's documents only
- Each user's data can be independently managed and persisted

### Collections

Collections in RecallDB are similar to tables in traditional databases:

- Documents are organized into named collections (e.g., "Articles", "Products", "Notes")
- Collections help organize documents logically
- Search can be restricted to specific collections

### Documents and Metadata

Each document in RecallDB consists of:

- Text content that is semantically embedded
- Optional metadata for filtering and organization
- A unique document ID (auto-generated or user-provided)

## Performance

In benchmarks using the GIST-1M dataset, RecallDB demonstrated excellent performance:

- Recall@1: 0.99 with ~6ms latency
- Consistent sub-7ms query times
- See [benchmark results](https://github.com/yourusername/recalldb/blob/main/gist_benchmark.md) for details

## License

MIT 