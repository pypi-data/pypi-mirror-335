"""
Basic usage example for EmbedDB.

This script demonstrates how to use EmbedDB for vector storage and search.
"""

from embeddb import EmbedDB

# Create a vector database (with fixed dimension)
db = EmbedDB(dimension=3)

# Add some vectors with metadata
db.add("vec1", [1.0, 0.0, 0.0], {"description": "First basis vector"})
db.add("vec2", [0.0, 1.0, 0.0], {"description": "Second basis vector"})
db.add("vec3", [0.0, 0.0, 1.0], {"description": "Third basis vector"})
db.add("vec4", [0.7, 0.7, 0.0], {"description": "Vector in first quadrant"})

# Search for similar vectors
query_vector = [0.8, 0.6, 0.0]
results = db.search(query_vector, top_k=2)

# Print results
print(f"Query: {query_vector}")
print("\nResults:")
for i, result in enumerate(results):
    print(f"{i+1}. {result['id']} - {result['metadata']['description']} (Similarity: {result['similarity']:.4f})")

# Save the database
db.save("example_db.json")
print("\nDatabase saved to example_db.json")

# Load the database
loaded_db = EmbedDB.load("example_db.json")
print(f"Loaded database with {loaded_db.count()} vectors") 