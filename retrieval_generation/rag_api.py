"""
RAG API Integration Module

This module provides a unified interface for UI integration with two main functions:
1. retrieve_context - Retrieves relevant context chunks from the knowledge base
2. generate_answer - Generates a grounded answer based on a question and context

This is designed to be the main interface for UI components.
"""

from typing import List, Dict, Union
from PIL import Image

# Import retriever and generator functions
from retriever import get_context as _retrieve_context
from generator import get_grounded_answer as _generate_answer


def retrieve_context(
    query: Union[str, Image.Image],
    query_type: str = 'text',
    top_k: int = 10,
    db_path: str = "chroma_local_db",
    collection_name: str = "multimodal_collection",
    offline_mode: bool = True
) -> List[Dict]:
    """
    Retrieve relevant context chunks from the knowledge base.
    
    This function wraps the retriever module to provide a clean interface for UI integration.
    
    Args:
        query: Text string or image (path or PIL Image object)
        query_type: Type of query - 'text' or 'image' (default: 'text')
        top_k: Number of top results to return (default: 10)
        db_path: Path to ChromaDB database directory (default: "chroma_local_db")
        collection_name: Name of the collection in ChromaDB (default: "multimodal_collection")
        offline_mode: If True, only use cached models (default: True)
    
    Returns:
        List of formatted context chunks with structure:
        [
            {
                "id": "document_chunk_1",
                "score": 0.85,
                "source": "document.pdf",
                "type": "text",
                "content": "...",
                "metadata": {...}
            },
            ...
        ]
    
    Example:
        >>> results = retrieve_context("What is machine learning?", top_k=5)
        >>> print(f"Found {len(results)} relevant chunks")
    """
    return _retrieve_context(
        query=query,
        query_type=query_type,
        top_k=top_k,
        db_path=db_path,
        collection_name=collection_name,
        offline_mode=offline_mode
    )


def generate_answer(
    question: str,
    context_chunks: List[Dict],
    top_k: int = None
) -> Dict:
    """
    Generate a grounded answer based on a question and context chunks.
    
    This function wraps the generator module to provide a clean interface for UI integration.
    It takes a question and context chunks, builds a prompt, and generates an answer using Ollama.
    
    Args:
        question: The user's question as a string
        context_chunks: List of context chunks retrieved from the knowledge base.
                       Each chunk should be a dict with keys: id, score, source, type, content, metadata
        top_k: Optional parameter to limit context chunks (if None, uses all provided chunks)
    
    Returns:
        Dictionary with structure:
        {
            "answer": "Generated answer text with citations...",
            "sources": [
                {
                    "id": "document_chunk_1",
                    "score": 0.85,
                    "source": "document.pdf",
                    "type": "text",
                    "content": "...",
                    "metadata": {...}
                },
                ...
            ]
        }
    
    Example:
        >>> context = retrieve_context("What is machine learning?", top_k=5)
        >>> result = generate_answer("What is machine learning?", context)
        >>> print(result["answer"])
    """
    # Optionally limit context chunks if top_k is specified
    if top_k is not None and top_k > 0:
        context_chunks = context_chunks[:top_k]
    
    return _generate_answer(question=question, context_chunks=context_chunks)


# Convenience function for end-to-end RAG pipeline
def rag_query(
    question: str,
    query_type: str = 'text',
    top_k: int = 10,
    db_path: str = "chroma_local_db",
    collection_name: str = "multimodal_collection",
    offline_mode: bool = True
) -> Dict:
    """
    Complete RAG pipeline: retrieve context and generate answer in one call.
    
    This is a convenience function that combines retrieval and generation for simple use cases.
    
    Args:
        question: The user's question as a string
        query_type: Type of query - 'text' or 'image' (default: 'text')
        top_k: Number of top results to retrieve (default: 10)
        db_path: Path to ChromaDB database directory (default: "chroma_local_db")
        collection_name: Name of the collection in ChromaDB (default: "multimodal_collection")
        offline_mode: If True, only use cached models (default: True)
    
    Returns:
        Dictionary with structure:
        {
            "answer": "Generated answer text with citations...",
            "sources": [...]
        }
    
    Example:
        >>> result = rag_query("What is machine learning?", top_k=5)
        >>> print(result["answer"])
    """
    # Step 1: Retrieve context
    context_chunks = retrieve_context(
        query=question,
        query_type=query_type,
        top_k=top_k,
        db_path=db_path,
        collection_name=collection_name,
        offline_mode=offline_mode
    )
    
    # Step 2: Generate answer
    result = generate_answer(question=question, context_chunks=context_chunks)
    
    return result


if __name__ == "__main__":
    # Example usage
    print("=" * 60)
    print("RAG API Integration Module - Example Usage")
    print("=" * 60)
    
    # Example 1: Separate retrieval and generation
    print("\nExample 1: Separate retrieval and generation")
    print("-" * 60)
    try:
        question = "What is machine learning?"
        print(f"Question: {question}")
        
        # Retrieve context
        print("\nStep 1: Retrieving context...")
        context = retrieve_context(question, top_k=5)
        print(f"Found {len(context)} context chunks")
        
        # Generate answer
        print("\nStep 2: Generating answer...")
        result = generate_answer(question, context)
        print(f"\nAnswer:\n{result['answer']}")
        print(f"\nSources: {len(result['sources'])} chunks")
        
    except Exception as e:
        print(f"Error: {e}")
        print("Make sure the database is set up and Ollama is running.")
    
    # Example 2: End-to-end RAG query
    print("\n" + "=" * 60)
    print("Example 2: End-to-end RAG query")
    print("-" * 60)
    try:
        question = "Explain the main concepts"
        print(f"Question: {question}")
        
        result = rag_query(question, top_k=5)
        print(f"\nAnswer:\n{result['answer']}")
        print(f"\nSources: {len(result['sources'])} chunks")
        
    except Exception as e:
        print(f"Error: {e}")
        print("Make sure the database is set up and Ollama is running.")

