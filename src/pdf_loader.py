"""
PDF Loader Module
Extracts text from research papers while preserving document structure
"""

import re
from pathlib import Path
from typing import Dict, List
import fitz  # PyMuPDF


class PDFLoader:
    """Extract text from PDFs with structure preservation"""
    
    # Common section headers in research papers
    SECTION_PATTERNS = [
        r'^abstract\s*$',
        r'^introduction\s*$',
        r'^background\s*$',
        r'^related\s+work\s*$',
        r'^methodology\s*$',
        r'^methods\s*$',
        r'^approach\s*$',
        r'^experiments?\s*$',
        r'^results?\s*$',
        r'^evaluation\s*$',
        r'^discussion\s*$',
        r'^conclusion\s*$',
        r'^future\s+work\s*$',
        r'^references\s*$',
        r'^bibliography\s*$',
        r'^\d+\.?\s+[A-Z][a-z]+',  # Numbered sections like "1. Introduction"
    ]
    
    def __init__(self):
        self.section_regex = re.compile('|'.join(self.SECTION_PATTERNS), re.IGNORECASE)
    
    def extract_text_with_structure(self, pdf_path: str) -> Dict:
        """
        Extract text from PDF with section detection
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            Dictionary with metadata and sections:
            {
                'metadata': {
                    'title': str,
                    'filename': str,
                    'pages': int
                },
                'sections': [
                    {
                        'section_name': str,
                        'text': str,
                        'page_start': int,
                        'page_end': int
                    }
                ]
            }
        """
        pdf_path = Path(pdf_path)
        
        try:
            doc = fitz.open(str(pdf_path))
        except Exception as e:
            raise Exception(f"Failed to open PDF {pdf_path}: {e}")
        
        # Extract metadata
        metadata = {
            'title': self._extract_title(doc),
            'filename': pdf_path.stem,
            'pages': len(doc)
        }
        
        # Extract text with page numbers
        page_texts = []
        for page_num in range(len(doc)):
            page = doc[page_num]
            text = page.get_text()
            page_texts.append({
                'page_num': page_num + 1,
                'text': text
            })
        
        doc.close()
        
        # Detect sections
        sections = self._detect_sections(page_texts)
        
        return {
            'metadata': metadata,
            'sections': sections
        }
    
    def _extract_title(self, doc) -> str:
        """
        Extract title from first page
        Uses heuristic: largest font size text on first page
        """
        try:
            first_page = doc[0]
            blocks = first_page.get_text("dict")["blocks"]
            
            # Find text with largest font size
            max_size = 0
            title = ""
            
            for block in blocks:
                if "lines" in block:
                    for line in block["lines"]:
                        for span in line["spans"]:
                            if span["size"] > max_size:
                                max_size = span["size"]
                                title = span["text"].strip()
            
            return title if title else "Unknown Title"
        except:
            return "Unknown Title"
    
    def _detect_sections(self, page_texts: List[Dict]) -> List[Dict]:
        """
        Detect sections in the document
        
        Args:
            page_texts: List of dicts with page_num and text
            
        Returns:
            List of sections with metadata
        """
        sections = []
        current_section = {
            'section_name': 'Introduction',
            'text': '',
            'page_start': 1,
            'page_end': 1
        }
        
        for page_data in page_texts:
            page_num = page_data['page_num']
            text = page_data['text']
            lines = text.split('\n')
            
            for line in lines:
                line_stripped = line.strip()
                
                # Check if line is a section header
                if self._is_section_header(line_stripped):
                    # Save current section if it has content
                    if current_section['text'].strip():
                        current_section['page_end'] = page_num
                        sections.append(current_section)
                    
                    # Start new section
                    current_section = {
                        'section_name': self._normalize_section_name(line_stripped),
                        'text': '',
                        'page_start': page_num,
                        'page_end': page_num
                    }
                else:
                    # Add to current section
                    current_section['text'] += line + '\n'
                    current_section['page_end'] = page_num
        
        # Add last section
        if current_section['text'].strip():
            sections.append(current_section)
        
        # If no sections detected, treat entire document as one section
        if not sections:
            all_text = '\n'.join([p['text'] for p in page_texts])
            sections = [{
                'section_name': 'Full Document',
                'text': all_text,
                'page_start': 1,
                'page_end': len(page_texts)
            }]
        
        return sections
    
    def _is_section_header(self, line: str) -> bool:
        """Check if a line is likely a section header"""
        if not line or len(line) > 100:  # Headers are usually short
            return False
        
        # Check against known patterns
        if self.section_regex.match(line):
            return True
        
        # Additional heuristic: All caps and short
        if line.isupper() and len(line.split()) <= 5:
            return True
        
        return False
    
    def _normalize_section_name(self, header: str) -> str:
        """Normalize section header to standard name"""
        header_lower = header.lower().strip()
        
        # Remove numbering
        header_lower = re.sub(r'^\d+\.?\s*', '', header_lower)
        
        # Map to standard names
        if 'abstract' in header_lower:
            return 'Abstract'
        elif 'introduction' in header_lower or 'intro' in header_lower:
            return 'Introduction'
        elif 'background' in header_lower:
            return 'Background'
        elif 'related' in header_lower:
            return 'Related Work'
        elif 'method' in header_lower or 'approach' in header_lower:
            return 'Methodology'
        elif 'experiment' in header_lower:
            return 'Experiments'
        elif 'result' in header_lower:
            return 'Results'
        elif 'evaluation' in header_lower:
            return 'Evaluation'
        elif 'discussion' in header_lower:
            return 'Discussion'
        elif 'conclusion' in header_lower:
            return 'Conclusion'
        elif 'future' in header_lower:
            return 'Future Work'
        elif 'reference' in header_lower or 'bibliography' in header_lower:
            return 'References'
        else:
            # Capitalize first letter of each word
            return header.title()


# Example usage
if __name__ == "__main__":
    loader = PDFLoader()
    result = loader.extract_text_with_structure("sample.pdf")
    print(f"Title: {result['metadata']['title']}")
    print(f"Pages: {result['metadata']['pages']}")
    print(f"Sections found: {len(result['sections'])}")
    for section in result['sections']:
        print(f"  - {section['section_name']} (pages {section['page_start']}-{section['page_end']})")
