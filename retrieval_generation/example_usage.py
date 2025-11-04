"""
Example Usage Scripts for the RAG System
Demonstrates various ways to use the integrated RAG pipeline
"""

from rag_client import create_rag_client
from pathlib import Path


def example_1_basic_query():
    """
    Example 1: Basic Query
    Shows how to initialize the client and ask a simple question
    """
    print("\n" + "=" * 80)
    print("EXAMPLE 1: Basic Query")
    print("=" * 80)
    
    # Initialize RAG client
    rag = create_rag_client()
    
    # Ask a question
    question = "What is this knowledge base about?"
    print(f"\nQuestion: {question}")
    
    result = rag.generate_answer(question, top_k=5)
    
    print(f"\nAnswer:\n{result['answer']}")
    print(f"\nSources used: {result['context_count']}")


def example_2_ingest_and_query():
    """
    Example 2: Ingest Documents and Query
    Shows how to add documents to the database and then query them
    """
    print("\n" + "=" * 80)
    print("EXAMPLE 2: Ingest Documents and Query")
    print("=" * 80)
    
    # Initialize RAG client
    rag = create_rag_client()
    
    # Check if you have documents to ingest
    doc_dir = Path("./my_documents")
    
    if doc_dir.exists():
        print(f"\nIngesting documents from: {doc_dir}")
        result = rag.ingest_directory(str(doc_dir))
        print(f"✓ Ingested {result['chunks_processed']} chunks from {len(result['files_processed'])} files")
    else:
        print(f"\n⚠ Directory {doc_dir} not found")
        print("  Create this directory and add some PDF, DOCX, image, or audio files")
        print("  Or use: rag.upload_file('path/to/your/document.pdf')")
    
    # Query the knowledge base
    question = "Summarize the key information from the documents"
    print(f"\nQuestion: {question}")
    
    result = rag.generate_answer(question, top_k=7)
    print(f"\nAnswer:\n{result['answer']}")


def example_3_upload_single_file():
    """
    Example 3: Upload a Single File
    Shows how to upload and ingest a single file
    """
    print("\n" + "=" * 80)
    print("EXAMPLE 3: Upload Single File")
    print("=" * 80)
    
    # Initialize RAG client
    rag = create_rag_client()
    
    # Example file path (replace with your actual file)
    file_path = "./my_documents/sample.pdf"
    
    if Path(file_path).exists():
        print(f"\nUploading file: {file_path}")
        result = rag.upload_file(file_path)
        print(f"✓ {result['message']}")
        print(f"  Chunks processed: {result['chunks_processed']}")
        print(f"  Total items in collection: {result['total_items_in_collection']}")
    else:
        print(f"\n⚠ File not found: {file_path}")
        print("  Update the file_path variable to point to your document")


def example_4_multimodal_query():
    """
    Example 4: Multimodal Query (Text, Images, Audio)
    Shows how to query across different content types
    """
    print("\n" + "=" * 80)
    print("EXAMPLE 4: Multimodal Query")
    print("=" * 80)
    
    # Initialize RAG client
    rag = create_rag_client()
    
    # Query for different types
    print("\n--- Query 1: Find text documents ---")
    result = rag.generate_answer(
        "What text documents are available?",
        top_k=5,
        filter_type='text'
    )
    print(f"Answer: {result['answer'][:200]}...")
    
    print("\n--- Query 2: Find images ---")
    result = rag.generate_answer(
        "What images are available?",
        top_k=5,
        filter_type='image'
    )
    print(f"Answer: {result['answer'][:200]}...")
    
    print("\n--- Query 3: Find audio transcripts ---")
    result = rag.generate_answer(
        "What audio transcripts are available?",
        top_k=5,
        filter_type='audio'
    )
    print(f"Answer: {result['answer'][:200]}...")


def example_5_custom_retrieval():
    """
    Example 5: Custom Retrieval
    Shows how to retrieve context separately and generate with custom context
    """
    print("\n" + "=" * 80)
    print("EXAMPLE 5: Custom Retrieval")
    print("=" * 80)
    
    # Initialize RAG client
    rag = create_rag_client()
    
    # Step 1: Retrieve context
    question = "What are the main topics covered?"
    print(f"\nQuestion: {question}")
    print("\nStep 1: Retrieving context...")
    
    context = rag.retrieve_context(
        query=question,
        query_type='text',
        top_k=10
    )
    
    print(f"Retrieved {len(context)} chunks:")
    for i, chunk in enumerate(context[:3], 1):  # Show first 3
        print(f"  {i}. {chunk['source']} ({chunk['type']}) - score: {chunk['score']:.4f}")
    
    # Step 2: Generate answer with custom context (e.g., filtered or processed)
    # You can filter, rerank, or process the context here
    filtered_context = context[:5]  # Use only top 5
    
    print(f"\nStep 2: Generating answer with top {len(filtered_context)} chunks...")
    result = rag.generate_answer_with_custom_context(question, filtered_context)
    
    print(f"\nAnswer:\n{result['answer']}")


def example_6_system_stats():
    """
    Example 6: System Statistics
    Shows how to get information about the RAG system
    """
    print("\n" + "=" * 80)
    print("EXAMPLE 6: System Statistics")
    print("=" * 80)
    
    # Initialize RAG client
    rag = create_rag_client()
    
    # Get stats
    print("\n--- Collection Info ---")
    info = rag.get_collection_info()
    print(f"Collection Name: {info['name']}")
    print(f"Total Items: {info['count']}")
    print(f"Metadata: {info['metadata']}")
    
    print("\n--- Detailed Stats ---")
    stats = rag.get_stats()
    for key, value in stats.items():
        print(f"{key}: {value}")
    
    print("\n--- Health Check ---")
    health = rag.health_check()
    print(f"Status: {health['status']}")
    print(f"Collection Count: {health['collection_count']}")


def example_7_direct_search():
    """
    Example 7: Direct Database Search
    Shows how to use the direct search function (alternative to retrieval)
    """
    print("\n" + "=" * 80)
    print("EXAMPLE 7: Direct Database Search")
    print("=" * 80)
    
    # Initialize RAG client
    rag = create_rag_client()
    
    # Direct search (returns raw ChromaDB results)
    query = "development projects"
    print(f"\nSearching for: '{query}'")
    
    results = rag.search_by_text(
        query_text=query,
        n_results=5,
        where={"type": "text"}  # Filter by type
    )
    
    print(f"\nFound {len(results['ids'][0])} results:")
    for i, (doc_id, doc, metadata, distance) in enumerate(
        zip(results['ids'][0], results['documents'][0], 
            results['metadatas'][0], results['distances'][0]), 1
    ):
        print(f"\n{i}. ID: {doc_id}")
        print(f"   Source: {metadata.get('source_file', 'Unknown')}")
        print(f"   Type: {metadata.get('type', 'Unknown')}")
        print(f"   Distance: {distance:.4f}")
        print(f"   Preview: {doc[:100]}...")


def example_8_batch_operations():
    """
    Example 8: Batch Operations
    Shows how to perform batch operations
    """
    print("\n" + "=" * 80)
    print("EXAMPLE 8: Batch Operations")
    print("=" * 80)
    
    # Initialize RAG client
    rag = create_rag_client()
    
    # Multiple questions
    questions = [
        "What is the main topic?",
        "What are the key findings?",
        "What conclusions are drawn?"
    ]
    
    print("\nProcessing multiple questions:")
    for i, question in enumerate(questions, 1):
        print(f"\n--- Question {i} ---")
        print(f"Q: {question}")
        
        result = rag.generate_answer(question, top_k=5)
        
        # Print shortened answer
        answer = result['answer']
        if len(answer) > 150:
            answer = answer[:150] + "..."
        print(f"A: {answer}")


def main():
    """Run all examples"""
    print("=" * 80)
    print("RAG SYSTEM - EXAMPLE USAGE")
    print("=" * 80)
    print("\nSelect an example to run:")
    print("  1. Basic Query")
    print("  2. Ingest Documents and Query")
    print("  3. Upload Single File")
    print("  4. Multimodal Query (Text, Images, Audio)")
    print("  5. Custom Retrieval")
    print("  6. System Statistics")
    print("  7. Direct Database Search")
    print("  8. Batch Operations")
    print("  9. Run all examples")
    print("  0. Exit")
    
    choice = input("\nEnter your choice (0-9): ").strip()
    
    examples = {
        "1": example_1_basic_query,
        "2": example_2_ingest_and_query,
        "3": example_3_upload_single_file,
        "4": example_4_multimodal_query,
        "5": example_5_custom_retrieval,
        "6": example_6_system_stats,
        "7": example_7_direct_search,
        "8": example_8_batch_operations
    }
    
    try:
        if choice == "9":
            # Run all examples
            for func in examples.values():
                func()
                print("\n")
        elif choice in examples:
            examples[choice]()
        elif choice == "0":
            print("Goodbye!")
        else:
            print("Invalid choice")
    except Exception as e:
        print(f"\n❌ Error running example: {e}")
        print("\nMake sure:")
        print("  1. The ChromaDB database exists and has data")
        print("  2. Ollama is running (for generation)")
        print("  3. All required models are downloaded")


if __name__ == "__main__":
    main()

