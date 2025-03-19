"""
Tests for the core vector functionality of EmbedDB.
"""
import json
import math
import os
import tempfile
import unittest
from typing import List

from embeddb import EmbedDB


class TestEmbedDB(unittest.TestCase):
    """Test cases for EmbedDB's core vector functionality."""

    def setUp(self):
        """Set up a test database with some vectors."""
        self.db = EmbedDB(dimension=3)
        
        # Add some test vectors
        self.db.add("vec1", [1.0, 0.0, 0.0], {"name": "Vector 1"})
        self.db.add("vec2", [0.0, 1.0, 0.0], {"name": "Vector 2"})
        self.db.add("vec3", [0.0, 0.0, 1.0], {"name": "Vector 3"})
        self.db.add("vec4", [0.5, 0.5, 0.0], {"name": "Vector 4"})

    def test_init(self):
        """Test initialization with and without dimension."""
        # Test with dimension
        db = EmbedDB(dimension=5)
        self.assertEqual(db._dimension, 5)
        
        # Test without dimension
        db = EmbedDB()
        self.assertIsNone(db._dimension)
        
        # Test dimension is set on first add
        db.add("test", [1.0, 2.0, 3.0])
        self.assertEqual(db._dimension, 3)

    def test_add(self):
        """Test adding vectors to the database."""
        db = EmbedDB(dimension=2)
        
        # Test adding a vector
        db.add("test1", [1.0, 2.0], {"name": "Test 1"})
        self.assertEqual(db.count(), 1)
        
        # Test normalization
        vector, _ = db.get("test1")
        magnitude = math.sqrt(sum(x*x for x in vector))
        self.assertAlmostEqual(magnitude, 1.0, places=6)
        
        # Test adding with no metadata
        db.add("test2", [3.0, 4.0])
        self.assertEqual(db.count(), 2)
        _, metadata = db.get("test2")
        self.assertEqual(metadata, {})
        
        # Test adding with wrong dimension
        with self.assertRaises(ValueError):
            db.add("test3", [1.0, 2.0, 3.0])
            
        # Test adding duplicate ID
        with self.assertRaises(ValueError):
            db.add("test1", [5.0, 6.0])

    def test_get(self):
        """Test retrieving vectors from the database."""
        # Test getting an existing vector
        vector, metadata = self.db.get("vec1")
        self.assertEqual(len(vector), 3)
        self.assertEqual(metadata["name"], "Vector 1")
        
        # Test getting a non-existent vector
        with self.assertRaises(KeyError):
            self.db.get("nonexistent")

    def test_delete(self):
        """Test deleting vectors from the database."""
        # Test deleting an existing vector
        self.assertEqual(self.db.count(), 4)
        self.db.delete("vec1")
        self.assertEqual(self.db.count(), 3)
        
        # Test that the vector is actually gone
        with self.assertRaises(KeyError):
            self.db.get("vec1")
            
        # Test deleting a non-existent vector
        with self.assertRaises(KeyError):
            self.db.delete("nonexistent")

    def test_count(self):
        """Test counting vectors in the database."""
        self.assertEqual(self.db.count(), 4)
        
        self.db.delete("vec1")
        self.assertEqual(self.db.count(), 3)
        
        db = EmbedDB()
        self.assertEqual(db.count(), 0)

    def test_normalize_vector(self):
        """Test vector normalization."""
        # Test normal vector
        vector = [3.0, 4.0]
        normalized = self.db._normalize_vector(vector)
        self.assertAlmostEqual(normalized[0], 0.6, places=6)
        self.assertAlmostEqual(normalized[1], 0.8, places=6)
        
        # Test zero vector
        vector = [0.0, 0.0, 0.0]
        normalized = self.db._normalize_vector(vector)
        self.assertEqual(normalized, [0.0, 0.0, 0.0])

    def test_search(self):
        """Test searching for similar vectors."""
        # Search for a vector similar to [1, 0, 0]
        results = self.db.search([1.0, 0.0, 0.0], top_k=2)
        self.assertEqual(len(results), 2)
        self.assertEqual(results[0]["id"], "vec1")  # Most similar is itself
        self.assertAlmostEqual(results[0]["similarity"], 1.0, places=6)
        
        # Search with a vector of wrong dimension
        with self.assertRaises(ValueError):
            self.db.search([1.0, 0.0], top_k=2)
            
        # Test that sorting works correctly
        results = self.db.search([0.7, 0.7, 0.0], top_k=4)
        self.assertEqual(len(results), 4)
        
        # First result should be most similar to the query
        for i in range(len(results) - 1):
            self.assertGreaterEqual(
                results[i]["similarity"],
                results[i+1]["similarity"]
            )
            
        # Test top_k limiting
        results = self.db.search([1.0, 0.0, 0.0], top_k=1)
        self.assertEqual(len(results), 1)

    def test_save_and_load(self):
        """Test saving and loading the database."""
        # Create a temporary file for testing
        with tempfile.NamedTemporaryFile(suffix='.json', delete=False) as tmp:
            filepath = tmp.name
            
        try:
            # Save the database
            self.db.save(filepath)
            self.assertTrue(os.path.exists(filepath))
            
            # Load the database
            loaded_db = EmbedDB.load(filepath)
            
            # Check that the loaded database has the same vectors
            self.assertEqual(loaded_db.count(), self.db.count())
            self.assertEqual(loaded_db._dimension, self.db._dimension)
            
            # Check that we can retrieve the same vectors and metadata
            for id in ["vec1", "vec2", "vec3", "vec4"]:
                original_vector, original_metadata = self.db.get(id)
                loaded_vector, loaded_metadata = loaded_db.get(id)
                
                # Check that vectors are almost equal (account for floating point differences)
                for a, b in zip(original_vector, loaded_vector):
                    self.assertAlmostEqual(a, b)
                    
                # Check that metadata is equal
                self.assertEqual(original_metadata, loaded_metadata)
                
            # Test search works on loaded database
            results = loaded_db.search([1.0, 0.0, 0.0], top_k=1)
            self.assertEqual(results[0]["id"], "vec1")
            
        finally:
            # Clean up
            if os.path.exists(filepath):
                os.remove(filepath)
                
    def test_load_nonexistent(self):
        """Test loading from a nonexistent file."""
        with self.assertRaises(FileNotFoundError):
            EmbedDB.load("nonexistent.json")


if __name__ == "__main__":
    unittest.main() 