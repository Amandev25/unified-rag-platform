# RAG System - Quick Start Guide

Get up and running with the complete RAG (Retrieval-Augmented Generation) system in 5 minutes!

## Prerequisites

1. **Python 3.8+** installed
2. **Ollama** installed and running ([Download here](https://ollama.ai))
3. **Git** (to clone if needed)

## Step 1: Install Dependencies

```bash
# Navigate to the project
cd RAG

# Install ingestion pipeline dependencies
cd ingestion_pipeline
pip install -r requirements.txt

# Install retrieval generation dependencies
cd ../retrieval_generation
pip install -r requirements.txt
```

## Step 2: Download Models (One-time setup)

```bash
# Download embedding models (for offline use)
cd ../ingestion_pipeline
python setup_offline.py
```

This will download:
- Text embedding model: BAAI/bge-base-en
- Image embedding model: google/siglip-base-patch16-224
- Whisper model for audio transcription

## Step 3: Start Ollama

In a separate terminal:

```bash
# Start Ollama server
ollama serve

# In another terminal, pull a model (if not already installed)
ollama pull phi3:mini
```

## Step 4: Ingest Your Documents

Create a folder with your documents and ingest them:

```bash
cd RAG/ingestion_pipeline

# Create a test documents folder
mkdir -p my_documents

# Copy your PDF, DOCX, images, or audio files to my_documents/
# Then ingest:

python -c "
from client import create_client
client = create_client()
result = client.ingest_directory('./my_documents')
print(f'✓ Ingested {result[\"chunks_processed\"]} chunks')
"
```

**Alternative: Use Python script**

Create `ingest_my_docs.py`:

```python
from client import create_client

client = create_client()
result = client.ingest_directory('./my_documents')

print(f"✓ Successfully ingested:")
print(f"  - Files: {len(result['files_processed'])}")
print(f"  - Chunks: {result['chunks_processed']}")
print(f"  - Total in DB: {result['total_items_in_collection']}")
```

Run it:
```bash
python ingest_my_docs.py
```

## Step 5: Ask Questions!

### Option A: Interactive App (Recommended)

```bash
cd ../retrieval_generation
python app_integrated.py
```

This launches an interactive application where you can:
- Run demo queries
- Ask your own questions
- View system statistics

### Option B: Simple Script

```bash
python app.py
```

Edit `app.py` to change the question:
```python
my_question = "What is in the knowledge base?"
```

### Option C: Use in Your Code

Create `my_rag_script.py`:

```python
from rag_client import create_rag_client

# Initialize
rag = create_rag_client()

# Ask a question
result = rag.generate_answer(
    question="What are the main topics in my documents?",
    top_k=5
)

# Display answer
print(f"Answer: {result['answer']}")
print(f"\nSources used: {result['context_count']}")
```

Run it:
```bash
python my_rag_script.py
```

## Configuration (Optional)

Create a `.env` file or export environment variables:

```bash
# In retrieval_generation/.env

CHROMA_DB_PATH=../ingestion_pipeline/chroma_local_db
OLLAMA_URL=http://localhost:11434
OLLAMA_MODEL=phi3:mini
OLLAMA_TIMEOUT=60
DEFAULT_TOP_K=10
OFFLINE_MODE=1
```

## Example Workflow

Here's a complete example:

```python
from rag_client import create_rag_client

# 1. Initialize the RAG system
print("Initializing RAG system...")
rag = create_rag_client()

# 2. Check what's in the database
stats = rag.get_stats()
print(f"\nDatabase has {stats['total_items']} items")

# 3. Optional: Ingest more documents
# rag.upload_file("new_document.pdf")
# rag.ingest_directory("./more_documents")

# 4. Ask questions
questions = [
    "What is this knowledge base about?",
    "What are the main topics?",
    "Summarize the key information"
]

for question in questions:
    print(f"\n{'='*60}")
    print(f"Q: {question}")
    print('='*60)
    
    result = rag.generate_answer(question, top_k=5)
    
    print(f"\nA: {result['answer']}")
    print(f"\nSources: {result['context_count']} chunks used")
```

## Troubleshooting

### "Database is empty" error

**Solution:** You need to ingest documents first:
```bash
cd ingestion_pipeline
python -c "from client import create_client; c = create_client(); c.ingest_directory('./my_documents')"
```

### "Could not connect to Ollama" error

**Solution:** 
1. Start Ollama: `ollama serve`
2. Pull a model: `ollama pull phi3:mini`
3. Check it's running: `curl http://localhost:11434/api/tags`

### "Model not found in local cache" error

**Solution:** Download models first:
```bash
cd ingestion_pipeline
python setup_offline.py
```

### "No relevant context found" error

**Solution:** 
- Check if your query matches the content in the database
- Try increasing `top_k` parameter
- Verify documents were ingested correctly

## Advanced Usage

### Multimodal Queries

```python
# Query for images
result = rag.generate_answer(
    "What images are available?",
    filter_type='image',
    top_k=5
)

# Query with an image
result = rag.generate_answer(
    "./my_image.jpg",
    query_type='image',
    top_k=5
)
```

### Custom Context Processing

```python
# Retrieve context separately
context = rag.retrieve_context("machine learning", top_k=20)

# Filter or process context
high_quality = [c for c in context if c['score'] < 0.3]

# Generate with custom context
result = rag.generate_answer_with_custom_context(
    "Explain machine learning",
    high_quality
)
```

### Batch Processing

```python
questions = ["Q1?", "Q2?", "Q3?"]
results = []

for q in questions:
    result = rag.generate_answer(q, top_k=5)
    results.append(result)
    
# Save results
import json
with open("results.json", "w") as f:
    json.dump(results, f, indent=2)
```

## Directory Structure

```
RAG/
├── ingestion_pipeline/           # Document processing
│   ├── my_documents/            # Your documents go here
│   ├── chroma_local_db/         # Vector database
│   └── client.py                # Ingestion client
│
├── retrieval_generation/         # RAG application
│   ├── rag_client.py            # Main client
│   ├── app_integrated.py        # Interactive app
│   └── example_usage.py         # Examples
│
├── INTEGRATION_GUIDE.md          # Detailed integration docs
└── QUICKSTART.md                 # This file
```

## What's Next?

1. **Explore Examples**: Run `python example_usage.py` for 8 different usage examples
2. **Read the Guide**: Check `INTEGRATION_GUIDE.md` for detailed documentation
3. **Customize Prompts**: Edit `generator.py` to customize answer generation
4. **Add More Content**: Ingest more documents as needed
5. **Build Your App**: Use `rag_client.py` in your own applications

## Resources

- **Full Documentation**: See `retrieval_generation/README.md`
- **Integration Guide**: See `INTEGRATION_GUIDE.md`
- **API Reference**: Check docstrings in `rag_client.py`
- **Examples**: Run `example_usage.py` for code samples

## Support

If you encounter issues:
1. Check the Troubleshooting section above
2. Review `INTEGRATION_GUIDE.md` for detailed explanations
3. Verify all prerequisites are installed
4. Check that Ollama is running and models are downloaded

## Tips for Best Results

1. **Quality Documents**: Ingest well-formatted documents for better results
2. **Right Top-K**: Start with 5-10, adjust based on answer quality
3. **Specific Questions**: More specific questions get better answers
4. **Check Sources**: Review the sources to understand where answers come from
5. **Iterate**: Refine your questions based on initial results

Happy RAG-ing! 🚀

