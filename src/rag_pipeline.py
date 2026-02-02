"""
RAG Pipeline Module
Orchestrates the complete RAG workflow
"""

import os
from typing import List, Dict
from pathlib import Path

from pdf_loader import PDFLoader
from chunker import Chunker
from embeddings import EmbeddingGenerator
from endee_store import EndeeClient


class RAGPipeline:
    """End-to-end RAG pipeline for research paper Q&A"""
    
    def __init__(self):
        """Initialize RAG pipeline with all components"""
        print("🔧 Initializing RAG Pipeline...")
        
        # Initialize components
        self.pdf_loader = PDFLoader()
        
        chunk_size = int(os.getenv('CHUNK_SIZE', 500))
        chunk_overlap = int(os.getenv('CHUNK_OVERLAP', 50))
        self.chunker = Chunker(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
        
        self.embedding_generator = EmbeddingGenerator()
        self.vector_store = EndeeClient()
        
        # Configuration
        self.collection_name = 'research_papers'
        self.top_k = int(os.getenv('TOP_K', 5))
        self.similarity_threshold = float(os.getenv('SIMILARITY_THRESHOLD', 0.7))
        
        # Initialize LLM
        self._initialize_llm()
        
        # Create collection in vector store
        self.vector_store.create_collection(
            name=self.collection_name,
            dimension=self.embedding_generator.get_dimension()
        )
        
        print("✅ RAG Pipeline initialized!\n")
    
    def _initialize_llm(self):
        """Initialize LLM for answer generation"""
        llm_provider = os.getenv('LLM_PROVIDER', 'gemini')
        
        if llm_provider == 'openai':
            try:
                from openai import OpenAI
                self.llm_client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
                self.llm_model = os.getenv('LLM_MODEL', 'gpt-3.5-turbo')
                self.llm_provider = 'openai'
                print(f"✓ LLM configured: {self.llm_model}")
            except Exception as e:
                print(f"⚠️  Warning: OpenAI LLM not available: {e}")
                print("   Answers will only show retrieved context")
                self.llm_client = None
        
        elif llm_provider == 'gemini':
            try:
                from google import genai
                self.genai_client = genai.Client(api_key=os.getenv('GEMINI_API_KEY'))
                self.llm_model = os.getenv('LLM_MODEL', 'gemini-1.5-flash')
                self.llm_client = self.genai_client
                self.llm_provider = 'gemini'
                print(f"✓ LLM configured: {self.llm_model}")
            except Exception as e:
                print(f"⚠️  Warning: Gemini LLM not available: {e}")
                print("   Answers will only show retrieved context")
                self.llm_client = None
        
        else:
            print("⚠️  Only retrieval will be performed (no LLM generation)")
            self.llm_client = None
            self.llm_provider = None
    
    def ingest_papers(self, pdf_paths: List[str]):
        """
        Ingest research papers into the system
        
        Args:
            pdf_paths: List of paths to PDF files
        """
        print(f"\n{'='*60}")
        print("📥 INGESTION PIPELINE")
        print(f"{'='*60}\n")
        
        all_chunks = []
        
        for pdf_path in pdf_paths:
            print(f"Processing: {Path(pdf_path).name}")
            
            try:
                # 1. Extract text with structure
                print("  └─ Extracting text...")
                document = self.pdf_loader.extract_text_with_structure(pdf_path)
                print(f"     ✓ Found {len(document['sections'])} sections")
                
                # 2. Chunk document
                print("  └─ Chunking document...")
                chunks = self.chunker.chunk_document(document)
                print(f"     ✓ Created {len(chunks)} chunks")
                
                all_chunks.extend(chunks)
                
            except Exception as e:
                print(f"  └─ ❌ Error: {e}")
                continue
        
        if not all_chunks:
            print("\n❌ No chunks created. Ingestion failed.")
            return
        
        print(f"\n📊 Total chunks to embed: {len(all_chunks)}")
        
        # 3. Generate embeddings
        print("\n🧮 Generating embeddings...")
        texts = [chunk['text'] for chunk in all_chunks]
        embeddings = self.embedding_generator.embed_batch(texts)
        print(f"✓ Generated {len(embeddings)} embeddings")
        
        # 4. Store in vector database
        print("\n💾 Storing in Endee...")
        metadatas = [
            {
                'text': chunk['text'],
                'paper_name': chunk['paper_name'],
                'section_name': chunk['section_name'],
                'page_number': chunk['page_number'],
                'chunk_index': chunk['chunk_index']
            }
            for chunk in all_chunks
        ]
        
        success = self.vector_store.insert_vectors(
            vectors=embeddings,
            metadatas=metadatas,
            collection=self.collection_name
        )
        
        if success:
            print("✓ Successfully stored in vector database")
        else:
            print("⚠️  Warning: Some vectors may not have been stored")
        
        print(f"\n{'='*60}")
        print("✅ INGESTION COMPLETE")
        print(f"{'='*60}\n")
    
    def query(self, question: str) -> Dict:
        """
        Query the RAG system
        
        Args:
            question: User's question
            
        Returns:
            Dictionary with answer and sources
        """
        # 1. Embed the question
        question_embedding = self.embedding_generator.embed_text(question)
        print(f"   📏 Question embedding dimension: {len(question_embedding)}")
        
        # 2. Retrieve relevant chunks (try without threshold first for debugging)
        results = self.vector_store.search(
            query_vector=question_embedding,
            top_k=self.top_k,
            collection=self.collection_name,
            threshold=0.0  # DEBUG: Set to 0 to see all results with scores
        )
        
        print(f"   🔎 Found {len(results)} results from search")
        if results:
            print(f"   📊 Top similarity scores: {[f'{r['similarity']:.3f}' for r in results[:3]]}")
            print(f"   ⚙️  Similarity threshold: {self.similarity_threshold}")
        
        # Filter by threshold
        filtered_results = [r for r in results if r['similarity'] >= self.similarity_threshold]
        
        if not filtered_results:
            if results:
                print(f"   ⚠️  All {len(results)} results below threshold {self.similarity_threshold}")
                print(f"   💡 Highest similarity was: {results[0]['similarity']:.3f}")
            return {
                'answer': "I couldn't find relevant information in the papers to answer this question.",
                'sources': []
            }
        
        # 3. Prepare context and sources
        context_chunks = []
        sources = []
        
        for result in filtered_results:
            metadata = result['metadata']
            similarity = result['similarity']
            
            context_chunks.append(
                f"[From: {metadata['paper_name']} - {metadata['section_name']}]\n{metadata['text']}"
            )
            
            sources.append({
                'paper': metadata['paper_name'],
                'section': metadata['section_name'],
                'page': metadata['page_number'],
                'excerpt': metadata['text'][:200],
                'similarity_score': similarity
            })
        
        context = "\n\n".join(context_chunks)
        
        # 4. Generate answer using LLM
        if self.llm_client:
            answer = self._generate_answer(question, context)
        else:
            # Fallback: return context directly
            answer = f"Based on the retrieved documents:\n\n{context[:500]}..."
        
        return {
            'answer': answer,
            'sources': sources
        }
    
    def _generate_answer(self, question: str, context: str) -> str:
        """
        Generate answer using LLM
        
        Args:
            question: User's question
            context: Retrieved context
            
        Returns:
            Generated answer
        """
        system_prompt = """You are a helpful and knowledgeable research assistant. Your goal is to provide useful insights from research papers.

GUIDELINES:
1. ALWAYS try to provide a helpful answer based on the available context
2. Synthesize information from the context to answer the question as best as you can
3. Use bullet points or numbered lists for clarity
4. Quote specific findings, methods, or contributions when they're explicitly mentioned
5. If the context has partial or related information, use it! Don't refuse to answer
6. Be conversational and friendly, not overly cautious
7. Only say you cannot answer if there is truly ZERO relevant information in the context
8. Base all answers strictly on the provided context - no external knowledge"""

        user_prompt = f"""Question: {question}

Context from research papers:
{context}

Based on the context above, please provide a helpful answer to the question. 
Synthesize the information and present it clearly using bullet points or numbered lists when appropriate.
Be specific and quote relevant findings when they're explicitly stated.

Answer:"""

        try:
            if self.llm_provider == 'openai':
                response = self.llm_client.chat.completions.create(
                    model=self.llm_model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    temperature=0.3,  # Lower temperature for more focused answers
                    max_tokens=500
                )
                return response.choices[0].message.content.strip()
            
            elif self.llm_provider == 'gemini':
                # Combine system and user prompts for Gemini
                full_prompt = f"{system_prompt}\n\n{user_prompt}"
                
                response = self.llm_client.models.generate_content(
                    model=self.llm_model,
                    contents=full_prompt,
                    config={
                        'temperature': 0.3,
                        'max_output_tokens': 500,
                    }
                )
                return response.text.strip()
        
        except Exception as e:
            print(f"Error generating answer: {e}")
            return f"Retrieved context:\n\n{context[:500]}..."


# Example usage
if __name__ == "__main__":
    pipeline = RAGPipeline()
    
    # Ingest papers
    papers = ['paper1.pdf', 'paper2.pdf']
    pipeline.ingest_papers(papers)
    
    # Query
    result = pipeline.query("What is the main methodology?")
    print(f"Answer: {result['answer']}")
    print(f"Sources: {len(result['sources'])} documents")
