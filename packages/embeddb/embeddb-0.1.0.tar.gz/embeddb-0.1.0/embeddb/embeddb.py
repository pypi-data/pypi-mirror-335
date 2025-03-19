"""
EmbedDB - Tiny semantic search DB in one file. Zero config. Instant prototyping.

This single file contains the entire implementation of EmbedDB, an ultra-lightweight
vector database designed for rapid prototyping of semantic search and RAG applications.
"""

import json
import math
import os
from typing import Dict, List, Optional, Tuple, Union, Any

# Default path to the pre-downloaded embedding model
DEFAULT_MODEL_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
                                 "embedding_models_cached/sentence-transformers_all-MiniLM-L6-v2")


class EmbedDB:
    """
    An ultra-lightweight vector database for semantic search.
    
    EmbedDB stores vectors along with metadata, allowing for quick semantic search operations.
    The entire implementation is contained within this single class for simplicity.
    """

    def __init__(self, dimension: Optional[int] = None, model_path: Optional[str] = None):
        """
        Initialize a new EmbedDB instance.
        
        Args:
            dimension: The dimension of the vectors to be stored.
                       If None, it will be set based on the first vector added.
            model_path: Path to a pre-downloaded sentence transformers model for embeddings.
                       If not provided but embedding functionality is used, 
                       it will use the default local model path if available.
        """
        self._vectors: Dict[str, List[float]] = {}
        self._metadata: Dict[str, Any] = {}
        self._dimension = dimension
        self._model = None
        self._model_path = model_path
        
    def add(self, id: str, vector: List[float], metadata: Optional[Any] = None) -> None:
        """
        Add a vector to the database with an associated ID and optional metadata.
        
        Args:
            id: A unique identifier for the vector.
            vector: The vector to store, as a list of floats.
            metadata: Optional metadata to associate with the vector.
                     Can be any JSON-serializable object.
                     
        Raises:
            ValueError: If the vector dimension doesn't match the database dimension.
        """
        if id in self._vectors:
            raise ValueError(f"ID '{id}' already exists in the database")
            
        if self._dimension is None:
            self._dimension = len(vector)
        elif len(vector) != self._dimension:
            raise ValueError(f"Vector dimension ({len(vector)}) does not match database dimension ({self._dimension})")
            
        # Normalize the vector for cosine similarity
        normalized_vector = self._normalize_vector(vector)
        
        self._vectors[id] = normalized_vector
        self._metadata[id] = metadata if metadata is not None else {}
        
    def _normalize_vector(self, vector: List[float]) -> List[float]:
        """
        Normalize a vector to unit length for cosine similarity calculation.
        
        Args:
            vector: The vector to normalize.
            
        Returns:
            The normalized vector.
        """
        magnitude = math.sqrt(sum(x*x for x in vector))
        if magnitude == 0:
            return [0.0] * len(vector)
        return [x/magnitude for x in vector]
        
    def get(self, id: str) -> Tuple[List[float], Any]:
        """
        Retrieve a vector and its metadata by ID.
        
        Args:
            id: The ID of the vector to retrieve.
            
        Returns:
            A tuple of (vector, metadata).
            
        Raises:
            KeyError: If the ID doesn't exist in the database.
        """
        if id not in self._vectors:
            raise KeyError(f"ID '{id}' not found in the database")
        
        return self._vectors[id], self._metadata[id]
        
    def delete(self, id: str) -> None:
        """
        Delete a vector and its metadata from the database.
        
        Args:
            id: The ID of the vector to delete.
            
        Raises:
            KeyError: If the ID doesn't exist in the database.
        """
        if id not in self._vectors:
            raise KeyError(f"ID '{id}' not found in the database")
            
        del self._vectors[id]
        del self._metadata[id]
        
    def count(self) -> int:
        """
        Get the number of vectors in the database.
        
        Returns:
            The number of vectors.
        """
        return len(self._vectors)
        
    def search(self, query_vector: List[float], top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Search for the most similar vectors to the query vector.
        
        Args:
            query_vector: The query vector to search for.
            top_k: The number of results to return.
            
        Returns:
            A list of dictionaries, each containing 'id', 'similarity', and 'metadata'.
            Results are sorted by similarity in descending order.
            
        Raises:
            ValueError: If the query vector dimension doesn't match the database dimension.
        """
        if len(query_vector) != self._dimension:
            raise ValueError(f"Query vector dimension ({len(query_vector)}) does not match database dimension ({self._dimension})")
            
        query_vector = self._normalize_vector(query_vector)
        
        results = []
        for id, vector in self._vectors.items():
            # Calculate cosine similarity
            similarity = sum(a*b for a, b in zip(query_vector, vector))
            results.append({
                'id': id,
                'similarity': similarity,
                'metadata': self._metadata[id]
            })
            
        # Sort by similarity (descending)
        results.sort(key=lambda x: x['similarity'], reverse=True)
        
        # Return top_k results
        return results[:top_k]
        
    def save(self, filepath: str) -> None:
        """
        Save the database to a JSON file.
        
        Args:
            filepath: The path to save the database to.
        """
        data = {
            'dimension': self._dimension,
            'vectors': self._vectors,
            'metadata': self._metadata
        }
        
        with open(filepath, 'w') as f:
            json.dump(data, f)
            
    @classmethod
    def load(cls, filepath: str) -> 'EmbedDB':
        """
        Load a database from a JSON file.
        
        Args:
            filepath: The path to load the database from.
            
        Returns:
            A new EmbedDB instance loaded from the file.
            
        Raises:
            FileNotFoundError: If the file doesn't exist.
        """
        with open(filepath, 'r') as f:
            data = json.load(f)
            
        db = cls(dimension=data['dimension'])
        db._vectors = data['vectors']
        db._metadata = data['metadata']
        
        return db
        
    def embed_text(self, text: str) -> List[float]:
        """
        Generate an embedding vector for a text string.
        
        Args:
            text: The text to embed.
            
        Returns:
            The embedding vector as a list of floats.
            
        Raises:
            ImportError: If sentence-transformers is not installed.
        """
        if self._model is None:
            try:
                from sentence_transformers import SentenceTransformer
            except ImportError:
                raise ImportError(
                    "To use text embedding functionality, you need to install the 'embeddings' extras: "
                    "pip install embeddb[embeddings]"
                )
                
            # Load the model
            if self._model_path:
                self._model = SentenceTransformer(self._model_path)
            else:
                # Check if default local model exists
                if os.path.exists(DEFAULT_MODEL_PATH):
                    self._model = SentenceTransformer(DEFAULT_MODEL_PATH)
                else:
                    # Fallback to downloading the model
                    self._model = SentenceTransformer('all-MiniLM-L6-v2')
                
            # Set dimension based on model if not already set
            if self._dimension is None:
                # Get dimension by encoding a simple test string
                self._dimension = len(self._model.encode("test", convert_to_numpy=False))
        
        # Generate embeddings
        vector = self._model.encode(text, convert_to_numpy=False)
        
        return vector.tolist() if hasattr(vector, 'tolist') else list(vector)
        
    def add_text(self, id: str, text: str, metadata: Optional[Any] = None) -> None:
        """
        Add a text document to the database, automatically generating its embedding.
        
        Args:
            id: A unique identifier for the document.
            text: The text to embed and store.
            metadata: Optional metadata to associate with the document.
                     If None, a default metadata with the text will be used.
                     
        Raises:
            ImportError: If sentence-transformers is not installed.
        """
        # Generate embedding
        vector = self.embed_text(text)
        
        # Create default metadata if none provided
        if metadata is None:
            metadata = {'text': text}
        elif isinstance(metadata, dict) and 'text' not in metadata:
            # Add text to metadata if it's a dict and doesn't already have 'text'
            metadata['text'] = text
            
        # Add to database
        self.add(id, vector, metadata)
        
    def search_text(self, query_text: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Search for the most similar documents to a text query.
        
        Args:
            query_text: The text query to search for.
            top_k: The number of results to return.
            
        Returns:
            A list of dictionaries, each containing 'id', 'similarity', and 'metadata'.
            Results are sorted by similarity in descending order.
            
        Raises:
            ImportError: If sentence-transformers is not installed.
        """
        # Generate embedding for the query
        query_vector = self.embed_text(query_text)
        
        # Search using the query vector
        return self.search(query_vector, top_k=top_k) 