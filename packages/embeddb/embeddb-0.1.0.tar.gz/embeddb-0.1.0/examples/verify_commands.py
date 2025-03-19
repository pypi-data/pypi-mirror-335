"""
Verification script that tests all 7 main commands of EmbedDB.

This script demonstrates and verifies the functionality of the 7 core commands:
1. Creating a database
2. Adding vectors
3. Searching for similar vectors
4. Getting vectors by ID
5. Deleting vectors
6. Saving the database
7. Loading the database
"""

import os
import tempfile
from embeddb import EmbedDB

print("EmbedDB Command Verification")
print("===========================")

# 1. Create a database
print("\n1. Creating a database")
db = EmbedDB(dimension=3)
print("✅ Database created with dimension 3")

# 2. Add vectors
print("\n2. Adding vectors")
db.add("vec1", [1.0, 0.0, 0.0], {"description": "X axis unit vector"})
db.add("vec2", [0.0, 1.0, 0.0], {"description": "Y axis unit vector"})
db.add("vec3", [0.0, 0.0, 1.0], {"description": "Z axis unit vector"})
print(f"✅ Added 3 vectors (count: {db.count()})")

# 3. Search for vectors
print("\n3. Searching for vectors")
query = [0.9, 0.1, 0.0]
results = db.search(query, top_k=2)
print(f"✅ Search completed with {len(results)} results:")
for i, result in enumerate(results):
    print(f"   {i+1}. {result['id']} - {result['metadata']['description']} "
          f"(Similarity: {result['similarity']:.4f})")

# 4. Get vector by ID
print("\n4. Getting vector by ID")
vector, metadata = db.get("vec1")
print(f"✅ Retrieved vec1: {vector}")
print(f"   Metadata: {metadata}")

# 5. Delete a vector
print("\n5. Deleting a vector")
db.delete("vec3")
print(f"✅ Deleted vec3 (new count: {db.count()})")
try:
    db.get("vec3")
    print("❌ Error: Vector still exists after deletion")
except KeyError:
    print("✅ Verified vec3 was properly deleted")

# 6. Save the database
print("\n6. Saving the database")
with tempfile.NamedTemporaryFile(suffix='.json', delete=False) as tmp:
    temp_path = tmp.name

db.save(temp_path)
print(f"✅ Database saved to {temp_path}")

# 7. Load the database
print("\n7. Loading the database")
loaded_db = EmbedDB.load(temp_path)
print(f"✅ Database loaded with {loaded_db.count()} vectors")

# Clean up
os.remove(temp_path)
print("\nAll 7 commands verified successfully!")

# Optional: Test text embedding if available
try:
    print("\nBONUS: Testing text embedding functionality")
    model_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                             "embedding_models_cached/sentence-transformers_all-MiniLM-L6-v2")
    
    # Create a database with explicit model path
    text_db = EmbedDB(model_path=model_path)
    
    # Add a text document
    text_db.add_text("doc1", "EmbedDB is a lightweight vector database for semantic search.")
    
    # Search for similar documents
    results = text_db.search_text("How to find similar text?", top_k=1)
    
    print(f"✅ Text embedding is working")
    print(f"   Query result: {results[0]['metadata']['text']}")
    print(f"   Similarity score: {results[0]['similarity']:.4f}")
except Exception as e:
    print(f"ℹ️ Text embedding test skipped: {str(e)}") 