# EmbedDB
> Tiny semantic search DB in one file. Zero config. Instant prototyping.

![License](https://img.shields.io/badge/license-MIT-blue)
![Python Versions](https://img.shields.io/badge/python-3.9%2B-blue)
![Build Status](https://img.shields.io/badge/build-passing-brightgreen)



**EmbedDB** is an ultra-lightweight vector database designed for rapid prototyping of semantic search and RAG applications. The entire implementation is contained in a single Python file with minimal dependencies.

[![a-minimalist-logo-design-for-embed-db-th-DWEWPgle-SR6o-L6-Qfi-RTnj-A-Pd-n0a-Ww-Sl-OZHIO2h-Jm-Q0g.png](https://i.postimg.cc/tT6Zw9SQ/a-minimalist-logo-design-for-embed-db-th-DWEWPgle-SR6o-L6-Qfi-RTnj-A-Pd-n0a-Ww-Sl-OZHIO2h-Jm-Q0g.png)](https://postimg.cc/Q9XdWZZ0)

## Why EmbedDB?

- **⚡ 2-Minute Integration:** From `pip install` to working code in under 2 minutes
- **📄 Single File:** Entire implementation in one readable Python file (<500 lines)
- **🔍 Simple API:** Just 7 intuitive commands to learn
- **🛠️ Zero Config:** No accounts, API keys, or complex setup
- **💾 JSON Persistence:** Simple file-based storage with human-readable format
- **🧩 Extensible:** Easy to modify or extend for your specific needs
- **🤖 Optional Embeddings:** Built-in text embedding support (when you need it)

## Installation

Basic installation (vector storage only):
```bash
pip install embeddb
```

With built-in embedding support:
```bash
pip install embeddb[embeddings]
```

*That's it. No compilation. No complex dependencies.*

## Quickstart

### Working with Vectors

```python
from embeddb import EmbedDB

# Create a vector database
db = EmbedDB(dimension=384)  # Set to your embedding dimension

# Add vectors with metadata
db.add("doc1", [0.1, 0.2, ...], {"text": "EmbedDB is easy to use"})
db.add("doc2", [0.3, 0.1, ...], {"text": "Vector databases for everyone"})

# Search for similar vectors
results = db.search([0.2, 0.3, ...], top_k=2)
for result in results:
    print(f"Match: {result['metadata']['text']} (Score: {result['similarity']})")

# Save for later
db.save("my_database.json")

# Load back when needed
db = EmbedDB.load("my_database.json")
```

### Working with Text (with built-in embeddings)

```python
from embeddb import EmbedDB

# Create a database with built-in embedding support
db = EmbedDB()

# Add documents with automatic embedding
db.add_text("doc1", "EmbedDB makes vector search easy")
db.add_text("doc2", "Semantic search finds related content")

# Search with a text query
results = db.search_text("How do I find similar documents?")

for result in results:
    print(f"Match: {result['metadata']['text']}")
```

## Complete RAG Example

Here's a complete Retrieval-Augmented Generation implementation in under 30 lines:

```python
from embeddb import EmbedDB

# Initialize EmbedDB with built-in embedding support
db = EmbedDB()  # Uses all-MiniLM-L6-v2 under the hood

# Add some documents (automatic embedding)
documents = [
    "EmbedDB is a lightweight vector database for prototyping.",
    "Vector databases store embeddings for semantic search.",
    "RAG systems enhance LLMs with relevant document retrieval."
]

# Add documents to EmbedDB
for i, doc in enumerate(documents):
    db.add_text(f"doc{i}", doc)

# Perform a search with text query
query = "How can I use vector search in my project?"
results = db.search_text(query, top_k=2)

# Display results
print(f"Query: {query}")
print("Relevant documents:")
for i, result in enumerate(results):
    print(f"{i+1}. {result['metadata']['text']} (Score: {result['similarity']:.4f})")
```

## API Reference

**Core Vector Database Functions:**

```python
# Create a database
db = EmbedDB(dimension=None)  # Dimension optional, set on first add

# Add a vector
db.add(id, vector, metadata)  # metadata can be any JSON-serializable object

# Search for similar vectors
results = db.search(query_vector, top_k=5)  # Returns list of {id, similarity, metadata}

# Get a vector by ID
vector, metadata = db.get(id)

# Delete a vector
db.delete(id)

# Save database to file
db.save(filepath)

# Load database from file
db = EmbedDB.load(filepath)

# Count vectors
count = db.count()
```

**Text Embedding Functions (with `embeddb[embeddings]`):**

```python
# Generate embeddings for text
vector = db.embed_text(text)

# Add text directly (auto-generates embedding)
db.add_text(id, text, metadata=None)

# Search using text query
results = db.search_text(query_text, top_k=5)
```

## When to Use EmbedDB

✅ **Perfect for:**
- Rapid prototyping of semantic search applications
- Learning and education about vector databases
- Small to medium-sized RAG implementations
- Projects where simplicity is more important than scale
- Quick demos and proofs of concept

❌ **Not designed for:**
- Production systems with millions of vectors
- High-throughput applications
- Advanced filtering and hybrid search
- Multi-user environments requiring access control

## How It Works

EmbedDB uses in-memory storage with cosine similarity for vector search. Vectors are automatically normalized on insertion for optimal similarity calculation. Persistence is handled through simple JSON serialization.

The optional text embedding functionality uses the all-MiniLM-L6-v2 model from sentence-transformers, which provides an excellent balance between size, speed, and quality for most prototyping needs.

The database has virtually no learning curve - if you know how to call functions in Python, you know how to use EmbedDB.

## Contributing

Contributions are welcome! The goal of this project is to remain extremely simple while being useful for developers. Before adding features, please consider whether they align with the project's minimalist philosophy.

## License

MIT License

---

Made for developers who want to go from idea to prototype in minutes, not days.
