"""
Integrated RAG Application
Combines ingestion pipeline client with retrieval and generation systems

This is the main application file that demonstrates the complete RAG pipeline:
1. Document ingestion (optional - if you have new documents)
2. Context retrieval (from ChromaDB using proper embeddings)
3. Answer generation (using Ollama LLM with retrieved context)
"""

import os
import sys
import json
from pathlib import Path

# Import the unified RAG client
from rag_client import create_rag_client


def print_separator(title: str = "", char: str = "=", width: int = 80):
    """Print a nice separator line with optional title"""
    if title:
        side_len = (width - len(title) - 2) // 2
        print(f"{char * side_len} {title} {char * side_len}")
    else:
        print(char * width)


def format_answer_output(result: dict):
    """Format and print the answer in a nice way"""
    print_separator("ANSWER", "=")
    print(result['answer'])
    print_separator()
    
    print(f"\n📊 Context Used: {result['context_count']} chunks")
    
    if result.get('sources'):
        print("\n📚 Sources:")
        for i, source in enumerate(result['sources'], 1):
            source_name = source.get('source', 'Unknown')
            source_type = source.get('type', 'unknown')
            score = source.get('score')
            
            score_str = f" (relevance: {score:.4f})" if score is not None else ""
            print(f"  [{i}] {source_name} ({source_type}){score_str}")


def demo_basic_query(rag_client):
    """Demonstrate a basic text query"""
    print_separator("DEMO 1: Basic Text Query")
    
    question = "What information is available in the knowledge base?"
    print(f"Question: {question}\n")
    
    try:
        result = rag_client.generate_answer(
            question=question,
            query_type='text',
            top_k=5
        )
        format_answer_output(result)
    except Exception as e:
        print(f"❌ Error: {e}")


def demo_specific_query(rag_client):
    """Demonstrate a more specific query"""
    print_separator("DEMO 2: Specific Query")
    
    question = "Tell me about development activities or projects mentioned in the documents"
    print(f"Question: {question}\n")
    
    try:
        result = rag_client.generate_answer(
            question=question,
            query_type='text',
            top_k=7
        )
        format_answer_output(result)
    except Exception as e:
        print(f"❌ Error: {e}")


def demo_filtered_query(rag_client):
    """Demonstrate a query with type filtering"""
    print_separator("DEMO 3: Filtered Query (Text Only)")
    
    question = "What text documents are available?"
    print(f"Question: {question}")
    print(f"Filter: Only text documents\n")
    
    try:
        result = rag_client.generate_answer(
            question=question,
            query_type='text',
            top_k=5,
            filter_type='text'
        )
        format_answer_output(result)
    except Exception as e:
        print(f"❌ Error: {e}")


def demo_image_query(rag_client):
    """Demonstrate an image-based query"""
    print_separator("DEMO 4: Image Query")
    
    # Check if we have any images in the collection
    print("Checking for images in the collection...")
    
    try:
        # Search for images
        results = rag_client.search_by_text(
            query_text="",
            n_results=10,
            where={"type": "image"}
        )
        
        if results['ids'][0]:
            print(f"✓ Found {len(results['ids'][0])} image(s) in the collection")
            question = "Find images related to the topic"
            print(f"\nQuestion: {question}\n")
            
            result = rag_client.generate_answer(
                question=question,
                query_type='text',
                top_k=5,
                filter_type='image'
            )
            format_answer_output(result)
        else:
            print("⚠ No images found in the collection")
            print("  Tip: Use rag_client.upload_file('path/to/image.jpg') to add images")
    except Exception as e:
        print(f"❌ Error: {e}")


def interactive_mode(rag_client):
    """Interactive Q&A mode"""
    print_separator("INTERACTIVE MODE")
    print("Enter your questions (type 'quit' or 'exit' to stop)")
    print("Commands:")
    print("  - 'stats' : Show system statistics")
    print("  - 'help'  : Show this help")
    print_separator()
    
    while True:
        try:
            question = input("\n❓ Your question: ").strip()
            
            if not question:
                continue
            
            if question.lower() in ['quit', 'exit', 'q']:
                print("👋 Goodbye!")
                break
            
            if question.lower() == 'stats':
                stats = rag_client.get_stats()
                print("\n📊 System Statistics:")
                for key, value in stats.items():
                    print(f"  {key}: {value}")
                continue
            
            if question.lower() == 'help':
                print("\nCommands:")
                print("  - 'stats' : Show system statistics")
                print("  - 'help'  : Show this help")
                print("  - 'quit'  : Exit interactive mode")
                continue
            
            # Generate answer
            result = rag_client.generate_answer(
                question=question,
                query_type='text',
                top_k=5
            )
            
            format_answer_output(result)
            
        except KeyboardInterrupt:
            print("\n\n👋 Interrupted. Goodbye!")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}")


def main():
    """Main application entry point"""
    
    print_separator("MULTIMODAL RAG SYSTEM", "=")
    print("Integrated Retrieval-Augmented Generation Pipeline")
    print_separator()
    
    # Check for configuration
    print("\n🔧 Configuration:")
    print(f"  OLLAMA_URL: {os.getenv('OLLAMA_URL', 'http://cp://0.tcp.in.ngrok.io:17997')}")
    print(f"  OLLAMA_MODEL: {os.getenv('OLLAMA_MODEL', 'phi3:mini')}")
    print(f"  Database: {os.getenv('CHROMA_DB_PATH', '../ingestion_pipeline/chroma_local_db')}")
    
    # Initialize RAG client
    print("\n🚀 Initializing RAG System...")
    try:
        rag_client = create_rag_client()
    except Exception as e:
        print(f"\n❌ Failed to initialize RAG system: {e}")
        print("\nTroubleshooting:")
        print("  1. Make sure you've run the ingestion pipeline first")
        print("  2. Check that the ChromaDB database exists")
        print("  3. Verify all required models are downloaded")
        return
    
    # Show system stats
    print("\n📊 System Statistics:")
    stats = rag_client.get_stats()
    for key, value in stats.items():
        print(f"  {key}: {value}")
    
    # Check if database has data
    if stats['total_items'] == 0:
        print("\n⚠️  WARNING: The database is empty!")
        print("  You need to ingest some documents first.")
        print("\n  To ingest documents:")
        print("    from rag_client import create_rag_client")
        print("    rag = create_rag_client()")
        print("    rag.ingest_directory('path/to/documents')")
        print("    # or")
        print("    rag.upload_file('path/to/document.pdf')")
        return
    
    # Choose mode
    print("\n" + "=" * 80)
    print("Select mode:")
    print("  1. Run demos (shows various query examples)")
    print("  2. Interactive mode (ask your own questions)")
    print("  3. Both (run demos first, then interactive)")
    print("=" * 80)
    
    mode = input("\nEnter choice (1/2/3) [default: 2]: ").strip()
    
    if mode == "1":
        # Run demos
        print("\n")
        demo_basic_query(rag_client)
        print("\n")
        demo_specific_query(rag_client)
        print("\n")
        demo_filtered_query(rag_client)
        print("\n")
        demo_image_query(rag_client)
    
    elif mode == "3":
        # Run demos then interactive
        print("\n")
        demo_basic_query(rag_client)
        print("\n")
        demo_specific_query(rag_client)
        print("\n\n")
        interactive_mode(rag_client)
    
    else:
        # Interactive mode (default)
        interactive_mode(rag_client)
    
    print("\n" + "=" * 80)
    print("Thank you for using the Multimodal RAG System!")
    print("=" * 80)


if __name__ == "__main__":
    main()

