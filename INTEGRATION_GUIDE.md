# RAG System Integration Guide

This document explains how the `retrieval_generation` module has been integrated with the `ingestion_pipeline` to create a complete, unified RAG (Retrieval-Augmented Generation) system.

## Overview

The integration combines:
- **Ingestion Pipeline** (`ingestion_pipeline/`) - Document processing and database population
- **Retrieval & Generation** (`retrieval_generation/`) - Context retrieval and answer generation

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         RAG SYSTEM                               │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────────────┐         ┌──────────────────────┐     │
│  │  Ingestion Pipeline  │         │ Retrieval Generation │     │
│  ├──────────────────────┤         ├──────────────────────┤     │
│  │                      │         │                      │     │
│  │  • ingest.py         │         │  • rag_client.py     │     │
│  │  • client.py         │◄────────┤  • retriever.py      │     │
│  │  • parsers.py        │         │  • generator.py      │     │
│  │  • db_setup.py       │         │  • config.py         │     │
│  │                      │         │                      │     │
│  └──────────┬───────────┘         └──────────┬───────────┘     │
│             │                                 │                 │
│             └────────────┬────────────────────┘                 │
│                          │                                      │
│                   ┌──────▼──────┐                              │
│                   │  ChromaDB   │                              │
│                   │  (Vector    │                              │
│                   │   Store)    │                              │
│                   └─────────────┘                              │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

## Key Integration Points

### 1. RAGClient (retrieval_generation/rag_client.py)

The **RAGClient** is the main integration point that combines:

- **IngestionClient** (from `ingestion_pipeline/client.py`)
  - Upload files
  - Ingest directories
  - Database operations (get, delete, search)
  
- **RetrievalSystem** (from `retrieval_generation/retriever.py`)
  - Semantic search with proper embeddings
  - Cross-modal retrieval
  - Context formatting

- **Generator** (from `retrieval_generation/generator.py`)
  - Answer generation with Ollama
  - Citation support
  - Enhanced prompts

### 2. Shared Resources

Both modules share:

1. **ChromaDB Database**
   - Location: `ingestion_pipeline/chroma_local_db/`
   - Collection: `multimodal_collection`
   - Stores embeddings and metadata

2. **Embedding Models**
   - Text: `BAAI/bge-base-en` (SentenceTransformer)
   - Image: `google/siglip-base-patch16-224` (SigLIP)
   - Both cached locally for offline use

3. **Configuration**
   - Environment variables
   - Consistent model names and paths

## Complete Workflow

### Phase 1: Ingestion (ingestion_pipeline)

```python
from ingestion_pipeline.client import create_client

# Initialize ingestion client
client = create_client()

# Ingest documents
client.ingest_directory("./documents")
# OR
client.upload_file("document.pdf")

# Verify ingestion
info = client.get_collection_info()
print(f"Total items: {info['count']}")
```

**What happens:**
1. Parse documents (PDF, DOCX, images, audio)
2. Chunk text content
3. Generate embeddings (text/image)
4. Store in ChromaDB with metadata

### Phase 2: Retrieval & Generation (retrieval_generation)

```python
from retrieval_generation.rag_client import create_rag_client

# Initialize RAG client (includes both ingestion and retrieval)
rag = create_rag_client()

# Generate answer (complete RAG pipeline)
result = rag.generate_answer(
    question="What is in the knowledge base?",
    top_k=5
)

print(result['answer'])
```

**What happens:**
1. Query embedding generation (using same models as ingestion)
2. Semantic search in ChromaDB (cosine similarity)
3. Context formatting with metadata
4. Prompt construction with context
5. Answer generation via Ollama LLM
6. Citation attachment

## Features

### 1. Multimodal Support

The system handles multiple content types:

```python
# Text documents (PDF, DOCX)
rag.generate_answer("What do the documents say?", filter_type='text')

# Images (JPG, PNG, etc.)
rag.generate_answer("What images are available?", filter_type='image')

# Audio transcripts (MP3, WAV, etc.)
rag.generate_answer("What audio content exists?", filter_type='audio')
```

### 2. Cross-Modal Search

Query with one modality, retrieve another:

```python
# Text query → Find relevant images
context = rag.retrieve_context("machine learning diagram", top_k=5)
# Returns both text chunks AND relevant images

# Image query → Find related text
context = rag.retrieve_context("./image.jpg", query_type='image', top_k=5)
# Returns text that's semantically similar to the image
```

### 3. Flexible Ingestion

```python
# Single file
rag.upload_file("report.pdf")

# Entire directory
rag.ingest_directory("./documents", batch_size=100)

# Check what's in the database
stats = rag.get_stats()
print(f"Total items: {stats['total_items']}")
print(f"Types: {stats['type_distribution']}")
```

### 4. Advanced Retrieval

```python
# Basic retrieval
context = rag.retrieve_context("AI ethics", top_k=10)

# Filtered retrieval
context = rag.retrieve_context("AI ethics", filter_type='text', top_k=10)

# Custom processing
context = rag.retrieve_context("AI", top_k=20)
filtered = [c for c in context if c['score'] < 0.3]  # More relevant
result = rag.generate_answer_with_custom_context("What is AI?", filtered)
```

### 5. Enhanced Prompts

The generator now uses comprehensive prompts that:
- Clearly instruct the LLM on how to use context
- Support multimodal sources (text, images, audio)
- Require citation with `[Citation N]` format
- Handle metadata (pages, timestamps, relevance scores)
- Structure output clearly

## Configuration

### Environment Variables

Set these before running the system:

```bash
# Database
export CHROMA_DB_PATH="../ingestion_pipeline/chroma_local_db"

# Models
export TEXT_MODEL="BAAI/bge-base-en"
export IMAGE_MODEL="google/siglip-base-patch16-224"
export OFFLINE_MODE="1"

# Ollama (for generation)
export OLLAMA_URL="http://localhost:11434"
export OLLAMA_MODEL="phi3:mini"
export OLLAMA_TIMEOUT="60"

# Retrieval
export DEFAULT_TOP_K="10"
```

### Using config.py

```python
from retrieval_generation.config import RAGConfig

# View configuration
RAGConfig.print_config()

# Modify settings
RAGConfig.OLLAMA_MODEL = "llama2"
RAGConfig.DEFAULT_TOP_K = 15
```

## Usage Examples

### Simple Usage

```python
from retrieval_generation.rag_client import create_rag_client

rag = create_rag_client()
result = rag.generate_answer("What is this about?")
print(result['answer'])
```

### Complete Pipeline

```python
from retrieval_generation.rag_client import create_rag_client

# 1. Initialize
rag = create_rag_client()

# 2. Ingest (if needed)
rag.ingest_directory("./my_documents")

# 3. Query
result = rag.generate_answer(
    question="Summarize the key points",
    top_k=7
)

# 4. Display
print(f"Answer: {result['answer']}")
print(f"Sources: {len(result['sources'])}")
for i, source in enumerate(result['sources'], 1):
    print(f"  [{i}] {source['source']} ({source['type']})")
```

### Running the Apps

**Simple App:**
```bash
cd retrieval_generation
python app.py
```

**Integrated App (with demos and interactive mode):**
```bash
cd retrieval_generation
python app_integrated.py
```

**Example Scripts:**
```bash
cd retrieval_generation
python example_usage.py
```

## File Structure

```
RAG/
├── ingestion_pipeline/
│   ├── ingest.py              # Core ingestion pipeline
│   ├── client.py              # Python client for ingestion
│   ├── parsers.py             # PDF, DOCX, image, audio parsers
│   ├── db_setup.py            # ChromaDB initialization
│   ├── app.py                 # FastAPI application
│   └── chroma_local_db/       # ChromaDB storage
│
├── retrieval_generation/
│   ├── rag_client.py          # 🔥 MAIN: Unified RAG client
│   ├── retriever.py           # Context retrieval
│   ├── generator.py           # Answer generation
│   ├── app_integrated.py      # 🔥 MAIN: Complete app with demos
│   ├── app.py                 # Simple app
│   ├── example_usage.py       # Usage examples
│   ├── config.py              # Configuration management
│   ├── requirements.txt       # Dependencies
│   └── README.md              # Module documentation
│
└── INTEGRATION_GUIDE.md       # This file
```

## How It Works Together

### 1. Ingestion Phase

```python
# Using ingestion_pipeline/client.py
from ingestion_pipeline.client import create_client

client = create_client()
client.ingest_directory("./docs")
```

**Process:**
1. `parsers.py` extracts content from files
2. `ingest.py` generates embeddings
3. `db_setup.py` manages ChromaDB connection
4. Embeddings + metadata stored in ChromaDB

### 2. Retrieval Phase

```python
# Using retrieval_generation/rag_client.py
from retrieval_generation.rag_client import create_rag_client

rag = create_rag_client()
result = rag.generate_answer("Question?")
```

**Process:**
1. `rag_client.py` initializes both ingestion client and retrieval system
2. `retriever.py` generates query embedding (using same models)
3. ChromaDB performs semantic search (cosine similarity)
4. `generator.py` builds prompt with retrieved context
5. Ollama generates answer with citations

## API Quick Reference

### RAGClient Methods

```python
from retrieval_generation.rag_client import create_rag_client

rag = create_rag_client()

# Ingestion
rag.upload_file("doc.pdf")
rag.ingest_directory("./docs")

# Retrieval
context = rag.retrieve_context("query", top_k=10)

# Generation
result = rag.generate_answer("question", top_k=5)

# Info
stats = rag.get_stats()
info = rag.get_collection_info()
health = rag.health_check()
```

## Troubleshooting

### Common Issues

1. **Database not found**
   ```
   Solution: Run ingestion pipeline first to create database
   ```

2. **No results from retrieval**
   ```
   Solution: Check if database has data with rag.get_collection_count()
   ```

3. **Ollama connection error**
   ```
   Solution: Start Ollama with 'ollama serve' and pull model 'ollama pull phi3:mini'
   ```

4. **Model not found**
   ```
   Solution: Run ingestion_pipeline/setup_offline.py to download models
   ```

## Performance Considerations

1. **Embedding Generation**: Done once during ingestion, cached in ChromaDB
2. **Retrieval Speed**: O(log n) with HNSW index in ChromaDB
3. **Batch Processing**: Use batch_size=100-200 for large ingestions
4. **Offline Mode**: Enables fully offline operation (no internet required)

## Next Steps

1. **Customize Prompts**: Edit `generator.py` `build_prompt()` function
2. **Add More Models**: Extend `parsers.py` for new file types
3. **Tune Retrieval**: Adjust `top_k` and add re-ranking
4. **Scale Up**: Use ChromaDB client-server for production
5. **Add UI**: Build web interface with FastAPI or Streamlit

## Summary

The integration provides:

✅ **Complete RAG Pipeline** - Ingestion → Retrieval → Generation  
✅ **Multimodal Support** - Text, images, audio  
✅ **Cross-Modal Search** - Query with text, find images (and vice versa)  
✅ **Unified Interface** - One client for everything  
✅ **Offline Capable** - Works without internet  
✅ **Extensible** - Easy to add new features  
✅ **Well-Documented** - Examples and guides included  

The system is production-ready and can be customized for specific use cases!

