# RAG System Usage Cheat Sheet

Quick reference for common operations.

## 🚀 Quick Start

```python
from rag_client import create_rag_client

# Initialize
rag = create_rag_client()

# Ask a question
result = rag.generate_answer("Your question here?")
print(result['answer'])
```

## 📥 Ingestion Operations

### Upload Single File
```python
rag.upload_file("document.pdf")
```

### Ingest Directory
```python
rag.ingest_directory("./documents", batch_size=100)
```

### Supported Formats
- **Documents**: PDF, DOCX
- **Images**: JPG, PNG, GIF, BMP, WebP
- **Audio**: MP3, WAV, M4A, FLAC

## 🔍 Retrieval Operations

### Basic Retrieval
```python
context = rag.retrieve_context(
    query="machine learning",
    top_k=10
)
```

### Image Query
```python
context = rag.retrieve_context(
    query="./image.jpg",
    query_type='image',
    top_k=10
)
```

### Filtered Retrieval
```python
# Text only
context = rag.retrieve_context(
    query="AI",
    filter_type='text',
    top_k=10
)

# Images only
context = rag.retrieve_context(
    query="diagram",
    filter_type='image',
    top_k=10
)

# Audio only
context = rag.retrieve_context(
    query="speech",
    filter_type='audio',
    top_k=10
)
```

## 💬 Generation Operations

### Basic Answer
```python
result = rag.generate_answer("What is AI?")
print(result['answer'])
```

### With More Context
```python
result = rag.generate_answer("What is AI?", top_k=10)
```

### With Filtering
```python
result = rag.generate_answer(
    "What text documents exist?",
    filter_type='text',
    top_k=5
)
```

### Custom Context
```python
# Get context
context = rag.retrieve_context("AI", top_k=20)

# Filter/process
filtered = [c for c in context if c['score'] < 0.3]

# Generate
result = rag.generate_answer_with_custom_context(
    "What is AI?",
    filtered
)
```

## 📊 System Information

### Collection Info
```python
info = rag.get_collection_info()
print(f"Name: {info['name']}")
print(f"Count: {info['count']}")
```

### Statistics
```python
stats = rag.get_stats()
print(f"Total items: {stats['total_items']}")
print(f"Types: {stats['type_distribution']}")
```

### Health Check
```python
health = rag.health_check()
print(f"Status: {health['status']}")
```

### Item Count
```python
count = rag.get_collection_count()
print(f"Items: {count}")
```

## 🗄️ Database Operations

### Get Item
```python
item = rag.get_item("document.pdf_chunk_1")
print(item['document'])
```

### Delete Item
```python
rag.delete_item("document.pdf_chunk_1")
```

### Direct Search
```python
results = rag.search_by_text(
    query_text="AI",
    n_results=10,
    where={"type": "text"}
)
```

## 🎨 Result Structure

### Answer Result
```python
result = {
    "answer": "The generated answer with [Citation 1]...",
    "sources": [
        {
            "id": "doc.pdf_chunk_1",
            "score": 0.15,
            "source": "doc.pdf",
            "type": "text",
            "content": "...",
            "metadata": {"page": 3}
        }
    ],
    "query": "Original question",
    "context_count": 5
}
```

### Context Chunk
```python
chunk = {
    "id": "doc.pdf_chunk_1",
    "score": 0.15,
    "source": "doc.pdf",
    "type": "text",
    "content": "The actual text...",
    "metadata": {
        "page": 3,
        "chunk_index": 0,
        "source_file": "doc.pdf",
        "type": "text"
    }
}
```

## 🔧 Configuration

### Environment Variables
```bash
export CHROMA_DB_PATH="../ingestion_pipeline/chroma_local_db"
export OLLAMA_URL="http://localhost:11434"
export OLLAMA_MODEL="phi3:mini"
export DEFAULT_TOP_K="10"
```

### Using Config
```python
from config import RAGConfig

RAGConfig.print_config()
RAGConfig.OLLAMA_MODEL = "llama2"
```

## 🎯 Common Patterns

### Complete Pipeline
```python
# 1. Initialize
rag = create_rag_client()

# 2. Ingest (once)
rag.ingest_directory("./docs")

# 3. Query (many times)
result = rag.generate_answer("Question?")
print(result['answer'])
```

### Batch Questions
```python
questions = ["Q1?", "Q2?", "Q3?"]

for q in questions:
    result = rag.generate_answer(q, top_k=5)
    print(f"Q: {q}")
    print(f"A: {result['answer']}\n")
```

### Quality Check
```python
result = rag.generate_answer("Question?", top_k=10)

# Check sources
if result['context_count'] < 3:
    print("Warning: Few sources used")

# Check scores
for source in result['sources']:
    if source['score'] > 0.5:
        print(f"Warning: Low relevance for {source['source']}")
```

### Multimodal Query
```python
# Find all content types
result = rag.generate_answer(
    "What content is available about AI?",
    top_k=15
)

# Analyze what was retrieved
types = {}
for source in result['sources']:
    t = source['type']
    types[t] = types.get(t, 0) + 1

print(f"Retrieved: {types}")
```

## 🎬 Running Apps

### Simple App
```bash
cd retrieval_generation
python app.py
```

### Interactive App
```bash
python app_integrated.py
# Then select mode:
# 1 = Demos
# 2 = Interactive Q&A
# 3 = Both
```

### Examples
```bash
python example_usage.py
# Then select 1-9
```

## 🐛 Troubleshooting

### Database Empty
```python
# Check count
if rag.get_collection_count() == 0:
    print("Need to ingest documents!")
    rag.ingest_directory("./docs")
```

### Ollama Not Running
```python
try:
    result = rag.generate_answer("Test")
except Exception as e:
    if "Could not connect" in str(e):
        print("Start Ollama: ollama serve")
```

### No Results
```python
context = rag.retrieve_context("query", top_k=10)
if not context:
    print("Try a different query or check database")
```

## 📚 Learn More

- **Quick Start**: `QUICKSTART.md`
- **Full Guide**: `INTEGRATION_GUIDE.md`
- **API Docs**: `README.md`
- **Examples**: `example_usage.py`

## 💡 Tips

1. **Start small**: Use `top_k=5` initially, adjust as needed
2. **Check sources**: Review what chunks were used
3. **Filter by type**: Use `filter_type` for targeted retrieval
4. **Batch process**: Process multiple questions efficiently
5. **Monitor quality**: Check relevance scores

## 🎓 Best Practices

### For Better Answers
- Use specific questions
- Include context in your question
- Adjust `top_k` based on answer quality
- Review sources to verify accuracy

### For Better Performance
- Use batch operations when possible
- Filter by type when appropriate
- Cache frequently used contexts
- Use appropriate `top_k` values (not too high)

### For Better Maintenance
- Check health regularly
- Monitor collection size
- Update documents as needed
- Clear old/irrelevant content

---

**Need help?** Check the full documentation in `INTEGRATION_GUIDE.md`

