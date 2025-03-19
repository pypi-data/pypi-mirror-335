"""
Tests for the text embedding functionality of EmbedDB.

These tests will be skipped if sentence-transformers is not installed.
"""
import os
import unittest
from unittest import mock

from embeddb import EmbedDB
from embeddb.embeddb import DEFAULT_MODEL_PATH

# Check if sentence-transformers is available
try:
    import sentence_transformers
    HAVE_EMBEDDINGS = True
except ImportError:
    HAVE_EMBEDDINGS = False


@unittest.skipIf(not HAVE_EMBEDDINGS, "sentence-transformers not installed")
class TestEmbeddings(unittest.TestCase):
    """Test cases for EmbedDB's text embedding functionality."""

    def setUp(self):
        """Set up a test database with embedding support."""
        # Mock the SentenceTransformer to avoid actual downloads/loading
        self.model_path_patcher = mock.patch('sentence_transformers.SentenceTransformer')
        self.mock_model_class = self.model_path_patcher.start()
        
        # Setup mock model
        self.mock_model = mock.MagicMock()
        self.mock_model_class.return_value = self.mock_model
        
        # Configure mock to return embeddings of dimension 4
        self.mock_model.encode.return_value = [0.1, 0.2, 0.3, 0.4]
        
        # Create database
        self.db = EmbedDB()
        
    def tearDown(self):
        """Tear down the test environment."""
        self.model_path_patcher.stop()
        
    def test_embed_text_with_default_model(self):
        """Test embedding text with the default model."""
        # Test embedding generation
        text = "This is a test"
        vector = self.db.embed_text(text)
        
        # Check that the model was called with the correct text
        self.mock_model.encode.assert_called_with(text, convert_to_numpy=False)
        
        # Check that we got a vector of the right dimension
        self.assertEqual(len(vector), 4)
        self.assertEqual(vector, [0.1, 0.2, 0.3, 0.4])
        
        # Check that the model was loaded with either the local path or the default model name
        # The order of checks depends on whether DEFAULT_MODEL_PATH exists
        if os.path.exists(DEFAULT_MODEL_PATH):
            self.mock_model_class.assert_called_with(DEFAULT_MODEL_PATH)
        else:
            self.mock_model_class.assert_called_with('all-MiniLM-L6-v2')

    def test_embed_text_with_custom_model(self):
        """Test embedding text with a custom model path."""
        # Create database with custom model path
        custom_db = EmbedDB(model_path="/path/to/model")
        
        # Test embedding generation
        text = "Custom model test"
        vector = custom_db.embed_text(text)
        
        # Check that the model was loaded with the custom path
        self.mock_model_class.assert_called_with('/path/to/model')

    def test_add_text(self):
        """Test adding text documents to the database."""
        # Configure mock to return predictable embeddings
        self.mock_model.encode.return_value = [0.5, 0.5, 0.5, 0.5]
        
        # Add a text document
        text = "Test document"
        self.db.add_text("doc1", text)
        
        # Check that the document was added with the correct embedding
        vector, metadata = self.db.get("doc1")
        self.assertEqual(vector, [0.5, 0.5, 0.5, 0.5])
        self.assertEqual(metadata["text"], text)
        
        # Check that the model was called to embed the text
        self.mock_model.encode.assert_called_with(text, convert_to_numpy=False)
        
        # Test adding text with custom metadata
        custom_metadata = {"text": text, "category": "test"}
        self.db.add_text("doc2", text, metadata=custom_metadata)
        
        # Check that the custom metadata was used
        _, metadata = self.db.get("doc2")
        self.assertEqual(metadata["category"], "test")
        
        # Test that text is added to metadata if not present
        self.db.add_text("doc3", text, metadata={"category": "test"})
        _, metadata = self.db.get("doc3")
        self.assertEqual(metadata["text"], text)
        self.assertEqual(metadata["category"], "test")

    def test_search_text(self):
        """Test searching for documents with a text query."""
        # First add test documents with fixed embeddings
        self.mock_model.encode.return_value = [1.0, 0.0, 0.0, 0.0]
        self.db.add_text("doc1", "First test document")
        
        self.mock_model.encode.return_value = [0.0, 1.0, 0.0, 0.0]
        self.db.add_text("doc2", "Second test document")
        
        # Now configure the mock for the search query
        self.mock_model.encode.return_value = [0.1, 0.9, 0.0, 0.0]
        
        # Search with a text query
        query = "Similar to second document"
        results = self.db.search_text(query, top_k=2)
        
        # Check that we got the expected results
        self.assertEqual(len(results), 2)
        self.assertEqual(results[0]["id"], "doc2")  # Most similar to doc2
        self.assertEqual(results[1]["id"], "doc1")

    def test_import_error(self):
        """Test that an ImportError is raised when sentence-transformers is not installed."""
        # Mock import to simulate sentence-transformers not being available
        with mock.patch.dict('sys.modules', {'sentence_transformers': None}):
            with self.assertRaises(ImportError):
                # Create a new instance to avoid using the mocked model
                db = EmbedDB()
                db.embed_text("This should fail")


if __name__ == "__main__":
    unittest.main() 