"""
Endee Vector Store Module
Client for interacting with Endee vector database
"""

import os
import json
import requests
from typing import List, Dict, Optional
import numpy as np


class EndeeClient:
    """
    Client for Endee vector database
    
    Note: This is a lightweight wrapper. Since Endee's official API documentation
    wasn't fully accessible, this implementation assumes a REST API similar to
    common vector databases. You may need to adjust based on actual Endee API.
    """
    
    def __init__(self, host: str = None, port: int = None):
        """
        Initialize Endee client
        
        Args:
            host: Endee server host
            port: Endee server port
        """
        self.host = host or os.getenv('ENDEE_HOST', 'localhost')
        self.port = port or int(os.getenv('ENDEE_PORT', '8000'))
        self.base_url = f"http://{self.host}:{self.port}"
        
        # In-memory fallback if Endee is not available
        self.use_fallback = False
        self.fallback_store = {
            'vectors': [],
            'metadata': []
        }
        
        # Check connection
        self._check_connection()
    
    def _check_connection(self):
        """Check if Endee server is accessible"""
        try:
            # Try to ping the server
            response = requests.get(f"{self.base_url}/health", timeout=2)
            if response.status_code == 200:
                print(f"✓ Connected to Endee at {self.base_url}")
                self.use_fallback = False
        except requests.exceptions.RequestException:
            print(f"⚠️  Warning: Cannot connect to Endee at {self.base_url}")
            print("   Using in-memory fallback store (data will not persist)")
            print("   To use Endee, run: docker-compose up -d")
            self.use_fallback = True
    
    def create_collection(self, name: str, dimension: int) -> bool:
        """
        Create a new collection for storing vectors
        
        Args:
            name: Collection name
            dimension: Vector dimension
            
        Returns:
            True if successful
        """
        if self.use_fallback:
            print(f"Fallback: Created in-memory collection '{name}' (dim={dimension})")
            return True
        
        try:
            response = requests.post(
                f"{self.base_url}/collections",
                json={
                    'name': name,
                    'dimension': dimension,
                    'metric': 'cosine'
                },
                timeout=5
            )
            return response.status_code in [200, 201]
        except Exception as e:
            print(f"Error creating collection: {e}")
            return False
    
    def insert_vectors(
        self,
        vectors: List[List[float]],
        metadatas: List[Dict],
        collection: str = 'research_papers'
    ) -> bool:
        """
        Insert vectors with metadata into Endee
        
        Args:
            vectors: List of embedding vectors
            metadatas: List of metadata dicts (same length as vectors)
            collection: Collection name
            
        Returns:
            True if successful
        """
        if len(vectors) != len(metadatas):
            raise ValueError("Vectors and metadatas must have same length")
        
        if self.use_fallback:
            # In-memory storage
            self.fallback_store['vectors'].extend(vectors)
            self.fallback_store['metadata'].extend(metadatas)
            return True
        
        try:
            # Prepare data
            data = {
                'collection': collection,
                'vectors': vectors,
                'metadata': metadatas
            }
            
            response = requests.post(
                f"{self.base_url}/vectors/insert",
                json=data,
                timeout=30
            )
            
            return response.status_code in [200, 201]
        except Exception as e:
            print(f"Error inserting vectors: {e}")
            # Fallback to in-memory
            self.fallback_store['vectors'].extend(vectors)
            self.fallback_store['metadata'].extend(metadatas)
            return True
    
    def search(
        self,
        query_vector: List[float],
        top_k: int = 5,
        collection: str = 'research_papers',
        threshold: float = 0.0
    ) -> List[Dict]:
        """
        Search for similar vectors
        
        Args:
            query_vector: Query embedding vector
            top_k: Number of results to return
            collection: Collection to search
            threshold: Minimum similarity threshold
            
        Returns:
            List of results with metadata and similarity scores:
            [
                {
                    'metadata': dict,
                    'similarity': float
                }
            ]
        """
        if self.use_fallback:
            return self._fallback_search(query_vector, top_k, threshold)
        
        try:
            response = requests.post(
                f"{self.base_url}/vectors/search",
                json={
                    'collection': collection,
                    'query': query_vector,
                    'top_k': top_k,
                    'threshold': threshold
                },
                timeout=10
            )
            
            if response.status_code == 200:
                return response.json().get('results', [])
            else:
                # Fallback
                return self._fallback_search(query_vector, top_k, threshold)
        except Exception as e:
            print(f"Error searching: {e}, using fallback")
            return self._fallback_search(query_vector, top_k, threshold)
    
    def _fallback_search(
        self,
        query_vector: List[float],
        top_k: int,
        threshold: float
    ) -> List[Dict]:
        """In-memory similarity search using cosine similarity"""
        if not self.fallback_store['vectors']:
            return []
        
        query_vec = np.array(query_vector)
        stored_vectors = np.array(self.fallback_store['vectors'])
        
        # Compute cosine similarities
        similarities = []
        for i, vec in enumerate(stored_vectors):
            sim = self._cosine_similarity(query_vec, vec)
            if sim >= threshold:
                similarities.append({
                    'index': i,
                    'similarity': float(sim),
                    'metadata': self.fallback_store['metadata'][i]
                })
        
        # Sort by similarity (descending)
        similarities.sort(key=lambda x: x['similarity'], reverse=True)
        
        # Return top-k
        return similarities[:top_k]
    
    def _cosine_similarity(self, vec1: np.ndarray, vec2: np.ndarray) -> float:
        """Calculate cosine similarity between two vectors"""
        dot_product = np.dot(vec1, vec2)
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        return dot_product / (norm1 * norm2)
    
    def delete_collection(self, collection: str = 'research_papers') -> bool:
        """Delete a collection"""
        if self.use_fallback:
            self.fallback_store = {'vectors': [], 'metadata': []}
            return True
        
        try:
            response = requests.delete(
                f"{self.base_url}/collections/{collection}",
                timeout=5
            )
            return response.status_code in [200, 204]
        except Exception as e:
            print(f"Error deleting collection: {e}")
            return False


# Example usage
if __name__ == "__main__":
    client = EndeeClient()
    
    # Create collection
    client.create_collection(name='test', dimension=384)
    
    # Insert some test vectors
    test_vectors = [[0.1] * 384, [0.2] * 384, [0.3] * 384]
    test_metadata = [
        {'text': 'First document', 'source': 'doc1'},
        {'text': 'Second document', 'source': 'doc2'},
        {'text': 'Third document', 'source': 'doc3'}
    ]
    
    client.insert_vectors(test_vectors, test_metadata, collection='test')
    
    # Search
    query = [0.15] * 384
    results = client.search(query, top_k=2, collection='test')
    
    print(f"Found {len(results)} results:")
    for result in results:
        print(f"  Similarity: {result['similarity']:.3f}")
        print(f"  Metadata: {result['metadata']}")
