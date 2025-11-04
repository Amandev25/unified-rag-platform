# Retrieval & Generation Module

This module handles the retrieval and generation components of the Multimodal RAG (Retrieval-Augmented Generation) system.

## Overview

The retrieval_generation module integrates with the ingestion pipeline to provide:
1. **Context Retrieval**: Find relevant chunks from ChromaDB using semantic search
2. **Answer Generation**: Generate grounded answers using Ollama LLM with retrieved context
3. **Unified Interface**: Easy-to-use client that combines ingestion and retrieval

## Architecture

```
retrieval_generation/
├── rag_client.py          # Unified RAG client (main interface)
├── retriever.py           # Retrieval system for context search
├── generator.py           # Answer generation with Ollama
├── app_integrated.py      # Complete application with demos
├── example_usage.py       # Example scripts
├── config.py             # Configuration management
└── app.py                # Simple app (original)
```

## Key Components

### 1. RAGClient (rag_client.py)

The unified client that integrates all RAG functionality:

```python
from rag_client import create_rag_client

# Initialize
rag = create_rag_client()

# Ingest documents
rag.upload_file("document.pdf")
rag.ingest_directory("./documents")

# Query
result = rag.generate_answer("What is this about?", top_k=5)
print(result['answer'])
```

**Key Methods:**
- `upload_file(path)` - Ingest a single file
- `ingest_directory(path)` - Ingest all files in a directory
- `retrieve_context(query, top_k)` - Retrieve relevant context chunks
- `generate_answer(question, top_k)` - Complete RAG pipeline (retrieve + generate)
- `get_stats()` - Get system statistics

### 2. RetrievalSystem (retriever.py)

Handles semantic search and context retrieval:

```python
from retriever import RetrievalSystem

retriever = RetrievalSystem()

# Text query
context = retriever.get_context("Find information about AI", top_k=10)

# Image query
context = retriever.get_context("./image.jpg", query_type='image', top_k=10)
```

**Features:**
- Text embeddings: BAAI/bge-base-en
- Image embeddings: google/siglip-base-patch16-224
- Cross-modal search (text queries can find images and vice versa)
- Formatted results with metadata

### 3. Generator (generator.py)

Generates answers using Ollama LLM:

```python
from generator import get_grounded_answer

result = get_grounded_answer(question, context_chunks)
print(result['answer'])
```

**Features:**
- Enhanced prompts with clear instructions
- Citation support ([Citation N] format)
- Multimodal context handling (text, images, audio)
- Configurable Ollama endpoint

## Quick Start

### Prerequisites

1. **Ingestion Pipeline**: Run the ingestion pipeline first to populate ChromaDB
2. **Ollama**: Install and run Ollama with a model (e.g., phi3:mini)
3. **Models**: Download embedding models (see ingestion_pipeline/setup_offline.py)

### Option 1: Use the Integrated App

```bash
cd retrieval_generation
python app_integrated.py
```

This launches an interactive application with:
- Demo queries
- Interactive Q&A mode
- System statistics

### Option 2: Use Example Scripts

```bash
python example_usage.py
```

Choose from 8 different examples showing various RAG features.

### Option 3: Use in Your Code

```python
from rag_client import create_rag_client

# Initialize
rag = create_rag_client()

# Ask a question
result = rag.generate_answer(
    question="What are the main topics?",
    top_k=5  # Number of context chunks
)

print(f"Answer: {result['answer']}")
print(f"Sources: {len(result['sources'])}")
```

## Configuration

### Environment Variables

Create a `.env` file or set environment variables:

```bash
# Database
CHROMA_DB_PATH=../ingestion_pipeline/chroma_local_db

# Embedding Models
TEXT_MODEL=BAAI/bge-base-en
IMAGE_MODEL=google/siglip-base-patch16-224
OFFLINE_MODE=1

# Ollama
OLLAMA_URL=http://localhost:11434
OLLAMA_MODEL=phi3:mini
OLLAMA_TIMEOUT=60

# Retrieval
DEFAULT_TOP_K=10
```

### Using config.py

```python
from config import RAGConfig

# Print current configuration
RAGConfig.print_config()

# Modify settings
RAGConfig.OLLAMA_MODEL = "llama2"
RAGConfig.DEFAULT_TOP_K = 15
```

## Usage Examples

### Example 1: Basic Query

```python
from rag_client import create_rag_client

rag = create_rag_client()
result = rag.generate_answer("What is this knowledge base about?")
print(result['answer'])
```

### Example 2: Ingest and Query

```python
from rag_client import create_rag_client

rag = create_rag_client()

# Ingest documents
rag.ingest_directory("./my_documents")

# Query
result = rag.generate_answer("Summarize the documents")
print(result['answer'])
```

### Example 3: Multimodal Query

```python
from rag_client import create_rag_client

rag = create_rag_client()

# Query for images only
result = rag.generate_answer(
    "What images are available?",
    filter_type='image',
    top_k=5
)

# Query for text only
result = rag.generate_answer(
    "What text documents exist?",
    filter_type='text',
    top_k=5
)
```

### Example 4: Custom Retrieval

```python
from rag_client import create_rag_client

rag = create_rag_client()

# Retrieve context separately
context = rag.retrieve_context("AI and machine learning", top_k=10)

# Filter or process context
filtered_context = [c for c in context if c['score'] < 0.5]

# Generate with custom context
result = rag.generate_answer_with_custom_context(
    "What is AI?",
    filtered_context
)
```

### Example 5: Batch Processing

```python
from rag_client import create_rag_client

rag = create_rag_client()

questions = [
    "What is the main topic?",
    "What are the key findings?",
    "What conclusions are made?"
]

for question in questions:
    result = rag.generate_answer(question, top_k=5)
    print(f"Q: {question}")
    print(f"A: {result['answer']}\n")
```

## API Reference

### RAGClient

#### Initialization
```python
RAGClient(
    db_path: str = "chroma_local_db",
    text_model: str = "BAAI/bge-base-en",
    image_model: str = "google/siglip-base-patch16-224",
    offline_mode: bool = True
)
```

#### Methods

**Ingestion:**
- `upload_file(file_path: str) -> Dict`
- `ingest_directory(directory_path: str, batch_size: int = 100) -> Dict`

**Retrieval:**
- `retrieve_context(query: Union[str, Image], query_type: str = 'text', top_k: int = 10, filter_type: Optional[str] = None) -> List[Dict]`
- `search_by_text(query_text: str, n_results: int = 10, where: Optional[Dict] = None) -> Dict`

**Generation:**
- `generate_answer(question: str, query_type: str = 'text', top_k: int = 10, filter_type: Optional[str] = None) -> Dict`
- `generate_answer_with_custom_context(question: str, context_chunks: List[Dict]) -> Dict`

**Utilities:**
- `get_collection_info() -> Dict`
- `get_collection_count() -> int`
- `get_stats() -> Dict`
- `health_check() -> Dict`

## Troubleshooting

### Database is Empty
```
⚠️ WARNING: The database is empty!
```
**Solution**: Run the ingestion pipeline first:
```bash
cd ../ingestion_pipeline
python -c "from client import create_client; c = create_client(); c.ingest_directory('./path/to/docs')"
```

### Ollama Connection Error
```
Error: Could not connect to Ollama
```
**Solution**: 
1. Install Ollama: https://ollama.ai
2. Start Ollama: `ollama serve`
3. Pull a model: `ollama pull phi3:mini`
4. Set OLLAMA_URL if using custom endpoint

### Models Not Found
```
RuntimeError: Model not found in local cache
```
**Solution**: Download models first:
```bash
cd ../ingestion_pipeline
python setup_offline.py
```

### Import Errors
```
ImportError: No module named 'client'
```
**Solution**: The code automatically adds ingestion_pipeline to path. Make sure:
1. Directory structure is correct
2. You're running from the retrieval_generation directory

## Performance Tips

1. **Adjust top_k**: Start with 5-10, increase if needed
2. **Use filters**: Filter by type ('text', 'image', 'audio') for faster retrieval
3. **Batch size**: For ingestion, use larger batches (100-200) for better performance
4. **Ollama timeout**: Increase for complex queries or slower systems
5. **Offline mode**: Use offline_mode=True to avoid network delays

## Integration with Ingestion Pipeline

This module is designed to work seamlessly with the ingestion pipeline:

```
ingestion_pipeline/          retrieval_generation/
├── ingest.py               ├── rag_client.py (uses client.py)
├── client.py        ←─────→├── retriever.py (uses ChromaDB)
└── chroma_local_db/   ←───→└── generator.py (generates answers)
```

The RAGClient uses:
- `IngestionClient` from ingestion_pipeline for database operations
- `RetrievalSystem` for semantic search
- `generator` for answer generation with Ollama

## License

Same as parent project.

