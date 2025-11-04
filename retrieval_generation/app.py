"""
Simple RAG Application
This is the simple version - for more features, see app_integrated.py

This file demonstrates basic RAG pipeline:
1. Retrieve context from ChromaDB
2. Generate answer using Ollama
"""

from retriever import get_context
from generator import get_grounded_answer
import json

# --- Configuration ---

# Option 1: Text query
my_question = "What information is available in the knowledge base?"
my_query_type = "text"

# Option 2: Image query (uncomment to use)
# my_question = "./my_documents/image.jpg"
# my_query_type = "image"

# Number of context chunks to retrieve
top_k = 5

# --- Main Application ---

print("=" * 80)
print("SIMPLE RAG APPLICATION")
print("=" * 80)
print(f"\nQuery: {my_question}")
print(f"Type: {my_query_type}")
print(f"Top-K: {top_k}")

print("\n" + "-" * 80)
print("STEP 1: Retrieving Context")
print("-" * 80)

# Retrieve context using the retriever
try:
    context_chunks = get_context(query=my_question, query_type=my_query_type, top_k=top_k)
    
    if not context_chunks:
        print("⚠️  No context found. The LLM may not be able to answer.")
        print("\nPossible reasons:")
        print("  1. The database is empty (run ingestion pipeline first)")
        print("  2. No relevant content matches your query")
        print("  3. The query type might not match available content")
    else:
        print(f"✓ Found {len(context_chunks)} context chunks")
        
        # Show preview of retrieved chunks
        print("\nContext Preview:")
        for i, chunk in enumerate(context_chunks[:3], 1):  # Show first 3
            source = chunk.get('source', 'Unknown')
            chunk_type = chunk.get('type', 'unknown')
            score = chunk.get('score', 'N/A')
            score_str = f"{score:.4f}" if isinstance(score, (int, float)) else str(score)
            print(f"  {i}. {source} ({chunk_type}) - score: {score_str}")
        
        if len(context_chunks) > 3:
            print(f"  ... and {len(context_chunks) - 3} more")

except Exception as e:
    print(f"❌ Error during retrieval: {e}")
    print("\nMake sure:")
    print("  1. ChromaDB database exists (../ingestion_pipeline/chroma_local_db)")
    print("  2. The database has been populated with documents")
    print("  3. Embedding models are downloaded")
    exit(1)

# Only proceed with generation if we have context
if context_chunks:
    print("\n" + "-" * 80)
    print("STEP 2: Generating Answer")
    print("-" * 80)
    
    try:
        final_response = get_grounded_answer(my_question, context_chunks)
        
        print("\n" + "=" * 80)
        print("FINAL ANSWER")
        print("=" * 80)
        print(f"\n{final_response['answer']}")
        
        print("\n" + "=" * 80)
        print("SOURCES")
        print("=" * 80)
        print(f"\nUsed {len(final_response['sources'])} source(s):")
        for i, source in enumerate(final_response['sources'], 1):
            print(f"  [{i}] {source.get('source', 'Unknown')} ({source.get('type', 'unknown')})")
        
        print("\n" + "=" * 80)
        
        # Optionally save the full response to a file
        # with open("response.json", "w") as f:
        #     json.dump(final_response, f, indent=2)
        # print("\n✓ Full response saved to response.json")
        
    except Exception as e:
        print(f"❌ Error during generation: {e}")
        print("\nMake sure:")
        print("  1. Ollama is running (ollama serve)")
        print("  2. A model is available (ollama pull phi3:mini)")
        print("  3. OLLAMA_URL environment variable is set correctly")
        exit(1)

print("\n" + "=" * 80)
print("Done!")
print("\nFor more features, try: python app_integrated.py")
print("=" * 80)