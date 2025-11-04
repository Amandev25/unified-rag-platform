"""
Quick test script for the RAG system
"""
import sys
from pathlib import Path

# Add retrieval_generation to path
sys.path.insert(0, str(Path(__file__).parent / "retrieval_generation"))

from retrieval_generation.rag_client import create_rag_client

def main():
    print("Testing RAG Client initialization...")
    
    try:
        # Initialize RAG client
        rag = create_rag_client()
        
        # Get stats
        print("\n✓ RAG Client initialized successfully!")
        print("\nSystem Stats:")
        stats = rag.get_stats()
        for key, value in stats.items():
            print(f"  {key}: {value}")
        
        # Try a simple query if data exists
        if stats['total_items'] > 0:
            print("\n" + "="*60)
            print("Testing a simple query...")
            print("="*60)
            
            result = rag.generate_answer(
                "What information is available?",
                top_k=3
            )
            
            print(f"\nAnswer preview: {result['answer'][:200]}...")
            print(f"Used {result['context_count']} context chunks")
        else:
            print("\n⚠ Database is empty - skipping query test")
            print("  Ingest some documents first to test queries")
        
        print("\n✅ All tests passed!")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())
