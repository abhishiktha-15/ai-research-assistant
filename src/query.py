"""
Query Interface Module
Simple CLI for querying the RAG system
"""

import sys
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent))

from rag_pipeline import RAGPipeline


def print_formatted_answer(result: dict):
    """Pretty print the        # Display answer
        print("\n" + "─"*60)
        print("💡 Answer:")
        print("─"*60)
        print(f"\n{result['answer']}\n")
        
        # Display sources with more detail
        if result['sources']:
            print("\n" + "─"*60)
            print("📚 Sources Used (Retrieved Context):")
            print("─"*60)
            for i, source in enumerate(result['sources'], 1):
                print(f"\n[{i}] 📄 {source['paper']}")
                print(f"    ├─ Section: {source['section']}")
                print(f"    ├─ Page: {source['page']}")
                print(f"    ├─ Relevance: {source['similarity_score']:.1%}")
                print(f"    └─ Context: \"{source['excerpt']}...\"")
        
        print("\n" + "="*60 + "\n")


def main():
    """Interactive query interface"""
    print("\n" + "="*60)
    print("  🔍 AI Research Paper Assistant - Query Interface")
    print("="*60)
    print("\nAsk questions about your research papers.")
    print("Type 'exit', 'quit', or 'q' to end.\n")
    
    # Initialize pipeline
    try:
        pipeline = RAGPipeline()
    except Exception as e:
        print(f"❌ Error initializing pipeline: {e}")
        return
    
    # Interactive loop
    while True:
        try:
            question = input("❓ Your question: ").strip()
            
            if question.lower() in ['exit', 'quit', 'q', '']:
                print("\n👋 Goodbye!\n")
                break
            
            print("\n🔍 Searching papers...")
            result = pipeline.query(question)
            print_formatted_answer(result)
            
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!\n")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}\n")


if __name__ == "__main__":
    main()
