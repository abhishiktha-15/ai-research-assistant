"""
Embeddings Module
Generate vector embeddings from text chunks
"""

import os
from typing import List, Union
from sentence_transformers import SentenceTransformer
import numpy as np


class EmbeddingGenerator:
    """Generate embeddings using Sentence Transformers or OpenAI"""
    
    def __init__(self, provider: str = None, model_name: str = None):
        """
        Initialize embedding generator
        
        Args:
            provider: 'sentence-transformers', 'openai', or 'gemini'
            model_name: Specific model to use
        """
        self.provider = provider or os.getenv('EMBEDDING_MODEL', 'sentence-transformers')
        
        if self.provider == 'sentence-transformers':
            self.model_name = model_name or os.getenv(
                'SENTENCE_TRANSFORMER_MODEL',
                'all-MiniLM-L6-v2'
            )
            print(f"Loading embedding model: {self.model_name}...")
            self.model = SentenceTransformer(self.model_name)
            self.dimension = self.model.get_sentence_embedding_dimension()
            print(f"✓ Model loaded. Embedding dimension: {self.dimension}")
            
        elif self.provider == 'openai':
            try:
                from openai import OpenAI
                self.client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
                self.model_name = model_name or 'text-embedding-3-small'
                self.dimension = 1536  # Default for OpenAI embeddings
                print(f"✓ OpenAI embeddings configured: {self.model_name}")
            except ImportError:
                raise Exception("OpenAI library not installed. Run: pip install openai")
            except Exception as e:
                raise Exception(f"Failed to initialize OpenAI client: {e}")
        
        elif self.provider == 'gemini':
            try:
                from google import genai
                from google.genai import types
                self.genai_client = genai.Client(api_key=os.getenv('GEMINI_API_KEY'))
                self.model_name = model_name or 'text-embedding-004'
                self.dimension = 768  # Gemini text-embedding-004 dimension
                print(f"✓ Gemini embeddings configured: {self.model_name}")
            except ImportError:
                raise Exception("Google GenAI library not installed. Run: pip install google-genai")
            except Exception as e:
                raise Exception(f"Failed to initialize Gemini client: {e}")
        
        else:
            raise ValueError(f"Unsupported embedding provider: {self.provider}")
    
    def embed_text(self, text: str) -> List[float]:
        """
        Generate embedding for a single text
        
        Args:
            text: Text to embed
            
        Returns:
            List of floats representing the embedding vector
        """
        if self.provider == 'sentence-transformers':
            embedding = self.model.encode(text, convert_to_numpy=True)
            return embedding.tolist()
        
        elif self.provider == 'openai':
            response = self.client.embeddings.create(
                input=text,
                model=self.model_name
            )
            return response.data[0].embedding
        
        elif self.provider == 'gemini':
            result = self.genai_client.models.embed_content(
                model=self.model_name,
                content=text
            )
            return result.embeddings[0].values
    
    def embed_batch(self, texts: List[str], batch_size: int = 32) -> List[List[float]]:
        """
        Generate embeddings for multiple texts efficiently
        
        Args:
            texts: List of texts to embed
            batch_size: Batch size for processing
            
        Returns:
            List of embedding vectors
        """
        if not texts:
            return []
        
        if self.provider == 'sentence-transformers':
            # Sentence Transformers handles batching internally
            embeddings = self.model.encode(
                texts,
                batch_size=batch_size,
                show_progress_bar=True,
                convert_to_numpy=True
            )
            return embeddings.tolist()
        
        elif self.provider == 'openai':
            # OpenAI API batch processing
            embeddings = []
            for i in range(0, len(texts), batch_size):
                batch = texts[i:i+batch_size]
                response = self.client.embeddings.create(
                    input=batch,
                    model=self.model_name
                )
                batch_embeddings = [item.embedding for item in response.data]
                embeddings.extend(batch_embeddings)
            return embeddings
        
        elif self.provider == 'gemini':
            # Gemini API batch processing
            from tqdm import tqdm
            embeddings = []
            for i in tqdm(range(0, len(texts), batch_size), desc="Embedding"):
                batch = texts[i:i+batch_size]
                for text in batch:
                    result = self.genai_client.models.embed_content(
                        model=self.model_name,
                        content=text
                    )
                    embeddings.append(result.embeddings[0].values)
            return embeddings
    
    def get_dimension(self) -> int:
        """Get the dimension of embeddings produced by this generator"""
        return self.dimension
    
    def cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """
        Calculate cosine similarity between two vectors
        
        Args:
            vec1: First vector
            vec2: Second vector
            
        Returns:
            Similarity score between -1 and 1
        """
        v1 = np.array(vec1)
        v2 = np.array(vec2)
        
        dot_product = np.dot(v1, v2)
        norm1 = np.linalg.norm(v1)
        norm2 = np.linalg.norm(v2)
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        return float(dot_product / (norm1 * norm2))


# Example usage
if __name__ == "__main__":
    # Test with sentence transformers
    generator = EmbeddingGenerator(provider='sentence-transformers')
    
    # Single text
    text = "This is a sample research paper about machine learning."
    embedding = generator.embed_text(text)
    print(f"Single embedding dimension: {len(embedding)}")
    
    # Batch
    texts = [
        "First research paper about AI.",
        "Second paper on deep learning.",
        "Third paper on neural networks."
    ]
    embeddings = generator.embed_batch(texts)
    print(f"Batch embeddings: {len(embeddings)} vectors")
    
    # Similarity
    similarity = generator.cosine_similarity(embeddings[0], embeddings[1])
    print(f"Similarity between first two: {similarity:.3f}")
