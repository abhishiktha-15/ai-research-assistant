"""
AI Research Paper Assistant with RAG
Main entry point for the application
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Add src to path
sys.path.append(str(Path(__file__).parent / 'src'))

from rag_pipeline import RAGPipeline


def setup_environment():
    """Check environment setup and dependencies"""
    load_dotenv()
    
    # Check for data/papers directory
    papers_dir = Path('data/papers')
    if not papers_dir.exists():
        papers_dir.mkdir(parents=True, exist_ok=True)
        print("✓ Created data/papers directory")
    
    # Check for Endee connection
    endee_host = os.getenv('ENDEE_HOST', 'localhost')
    endee_port = os.getenv('ENDEE_PORT', '8000')
    print(f"✓ Endee configured at {endee_host}:{endee_port}")
    
    return True


def ingest_papers(pipeline):
    """Ingest all PDFs from data/papers directory"""
    papers_dir = Path('data/papers')
    pdf_files = list(papers_dir.glob('*.pdf'))
    
    if not pdf_files:
        print("⚠️  No PDF files found in data/papers/")
        print("   Please add research papers to data/papers/ and run again")
        return False
    
    print(f"\n📚 Found {len(pdf_files)} paper(s) to ingest:")
    for pdf in pdf_files:
        print(f"   - {pdf.name}")
    
    print("\n🔄 Starting ingestion pipeline...")
    pipeline.ingest_papers([str(p) for p in pdf_files])
    print("✅ Ingestion complete!\n")
    
    return True


def interactive_query(pipeline):
    """Interactive question-answering loop"""
    print("\n" + "="*60)
    print("  AI Research Paper Assistant - Interactive Mode")
    print("="*60)
    print("\nAsk questions about your research papers.")
    print("Type 'exit' or 'quit' to end the session.\n")
    
    while True:
        try:
            question = input("❓ Question: ").strip()
            
            if question.lower() in ['exit', 'quit', 'q']:
                print("\n👋 Goodbye!\n")
                break
            
            if not question:
                continue
            
            print("\n🔍 Searching papers...")
            result = pipeline.query(question)
            
            # Print answer
            print("\n" + "─"*60)
            print("💡 Answer:")
            print("─"*60)
            print(f"\n{result['answer']}\n")
            
            # Print sources
            if result['sources']:
                print("📖 Sources:")
                print("─"*60)
                for i, source in enumerate(result['sources'], 1):
                    print(f"\n{i}. {source['paper']} - {source['section']}")
                    print(f"   Page: {source.get('page', 'N/A')} | Similarity: {source['similarity_score']:.3f}")
                    print(f"   Excerpt: \"{source['excerpt'][:150]}...\"")
            
            print("\n" + "="*60 + "\n")
            
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!\n")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}\n")


def main():
    """Main application flow"""
    print("\n" + "="*60)
    print("  🤖 AI Research Paper Assistant with RAG")
    print("="*60 + "\n")
    
    # Setup
    if not setup_environment():
        print("❌ Setup failed. Please check your configuration.")
        return
    
    # Initialize pipeline
    print("🚀 Initializing RAG pipeline...")
    pipeline = RAGPipeline()
    
    # Check command line arguments
    if len(sys.argv) > 1:
        if sys.argv[1] == '--ingest':
            ingest_papers(pipeline)
            return
        elif sys.argv[1] == '--query':
            interactive_query(pipeline)
            return
    
    # Default: ingest then query
    if ingest_papers(pipeline):
        interactive_query(pipeline)


if __name__ == "__main__":
    main()
