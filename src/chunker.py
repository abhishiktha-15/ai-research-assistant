"""
Chunker Module
Splits documents into semantic chunks with metadata preservation
"""

from typing import Dict, List
import re


class Chunker:
    """Section-aware document chunking"""
    
    def __init__(self, chunk_size: int = 500, chunk_overlap: int = 50):
        """
        Initialize chunker
        
        Args:
            chunk_size: Target size of chunks in characters
            chunk_overlap: Overlap between chunks in characters
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
    
    def chunk_document(self, document: Dict) -> List[Dict]:
        """
        Chunk a document into smaller pieces with metadata
        
        Args:
            document: Document dict from PDFLoader with 'metadata' and 'sections'
            
        Returns:
            List of chunks with metadata:
            [
                {
                    'text': str,
                    'paper_name': str,
                    'section_name': str,
                    'page_number': int,
                    'chunk_index': int
                }
            ]
        """
        chunks = []
        chunk_index = 0
        
        paper_name = document['metadata']['filename']
        
        for section in document['sections']:
            section_name = section['section_name']
            section_text = section['text'].strip()
            page_start = section['page_start']
            page_end = section['page_end']
            
            # Calculate average page for section
            avg_page = (page_start + page_end) // 2
            
            # If section is small enough, keep as single chunk
            if len(section_text) <= self.chunk_size:
                if section_text:  # Only add non-empty chunks
                    chunks.append({
                        'text': section_text,
                        'paper_name': paper_name,
                        'section_name': section_name,
                        'page_number': avg_page,
                        'chunk_index': chunk_index
                    })
                    chunk_index += 1
            else:
                # Split large sections with sliding window
                section_chunks = self._split_text_with_overlap(
                    section_text,
                    self.chunk_size,
                    self.chunk_overlap
                )
                
                for chunk_text in section_chunks:
                    if chunk_text.strip():  # Only add non-empty chunks
                        chunks.append({
                            'text': chunk_text,
                            'paper_name': paper_name,
                            'section_name': section_name,
                            'page_number': avg_page,
                            'chunk_index': chunk_index
                        })
                        chunk_index += 1
        
        return chunks
    
    def _split_text_with_overlap(self, text: str, chunk_size: int, overlap: int) -> List[str]:
        """
        Split text into overlapping chunks
        
        Args:
            text: Text to split
            chunk_size: Size of each chunk
            overlap: Overlap between chunks
            
        Returns:
            List of text chunks
        """
        chunks = []
        start = 0
        text_len = len(text)
        
        while start < text_len:
            end = start + chunk_size
            
            # Try to break at sentence boundary
            if end < text_len:
                # Look for sentence ending
                chunk_text = text[start:end]
                
                # Find last period, exclamation, or question mark
                last_sentence_end = max(
                    chunk_text.rfind('. '),
                    chunk_text.rfind('! '),
                    chunk_text.rfind('? ')
                )
                
                if last_sentence_end > chunk_size * 0.5:  # At least 50% of chunk size
                    end = start + last_sentence_end + 1
            
            chunk = text[start:end].strip()
            if chunk:
                chunks.append(chunk)
            
            # Move start forward with overlap
            start = end - overlap if end < text_len else text_len
        
        return chunks
    
    def chunk_multiple_documents(self, documents: List[Dict]) -> List[Dict]:
        """
        Chunk multiple documents
        
        Args:
            documents: List of document dicts
            
        Returns:
            List of all chunks from all documents
        """
        all_chunks = []
        
        for doc in documents:
            doc_chunks = self.chunk_document(doc)
            all_chunks.extend(doc_chunks)
        
        return all_chunks


# Example usage
if __name__ == "__main__":
    # Sample document structure
    sample_doc = {
        'metadata': {
            'filename': 'sample_paper',
            'pages': 10
        },
        'sections': [
            {
                'section_name': 'Abstract',
                'text': 'This is a sample abstract. ' * 50,
                'page_start': 1,
                'page_end': 1
            },
            {
                'section_name': 'Introduction',
                'text': 'This is the introduction section. ' * 100,
                'page_start': 2,
                'page_end': 3
            }
        ]
    }
    
    chunker = Chunker(chunk_size=500, chunk_overlap=50)
    chunks = chunker.chunk_document(sample_doc)
    
    print(f"Created {len(chunks)} chunks")
    for i, chunk in enumerate(chunks[:3]):
        print(f"\nChunk {i}:")
        print(f"  Section: {chunk['section_name']}")
        print(f"  Page: {chunk['page_number']}")
        print(f"  Text length: {len(chunk['text'])}")
