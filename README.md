# Unified RAG Platform

A production-ready, multimodal Retrieval-Augmented Generation (RAG) platform that enables intelligent document search and question-answering across text, images, and audio files. Built with FastAPI, ChromaDB, and state-of-the-art ML models.

![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

## 🚀 Features

### Multimodal Document Processing
- **Documents**: PDF, DOCX with intelligent text extraction and chunking
- **Images**: JPG, PNG, GIF, BMP, WEBP with dual-mode support:
  - OCR-based text extraction (EasyOCR) for text-heavy images
  - Direct image embeddings (SigLIP) for visual content search
- **Audio**: MP3, WAV, M4A, FLAC with Whisper-based speech-to-text conversion
- **Batch Processing**: Efficient directory-level ingestion with configurable batch sizes

### Advanced Retrieval System
- **Semantic Search**: Vector-based similarity search using ChromaDB with HNSW indexing
- **Cross-Modal Retrieval**: Text queries can find relevant images/audio and vice versa
- **Metadata Filtering**: Type-based filtering (text/image/audio) and custom metadata queries
- **Embedding Models**: 
  - Text: `BAAI/bge-base-en` (SentenceTransformers)
  - Images: `google/siglip-base-patch16-224` (HuggingFace)

### Intelligent Answer Generation
- **LLM Integration**: Ollama-based answer generation with configurable models (phi3, llama2, etc.)
- **Context-Aware Responses**: Grounded answers with source citations
- **Citation Support**: Automatic source attribution with `[Citation N]` format
- **Multimodal Context Handling**: Processes text, image, and audio context seamlessly

### Offline-First Architecture
- **Local Model Caching**: All ML models cached locally for offline operation
- **Persistent Vector Database**: ChromaDB with local storage
- **Zero Internet Dependency**: Complete functionality without network connectivity after initial setup

### Multiple User Interfaces
- **RESTful API**: FastAPI-based production API with OpenAPI documentation
- **React Web UI**: Modern, responsive web interface with chat and file upload
- **Desktop Application**: PyQt5-based native desktop client with chat history
- **Vanilla JS UI**: Lightweight web interface for quick deployment

## 📋 Prerequisites

- Python 3.11 or higher
- pip (Python package manager)
- Ollama (for LLM functionality) - [Install Ollama](https://ollama.ai)
- FFmpeg (for audio processing) - [Install FFmpeg](https://ffmpeg.org/download.html)

## 🛠️ Installation

### 1. Clone the Repository

```bash
git clone https://github.com/Amandev25/unified-rag-platform.git
cd unified-rag-platform
```

### 2. Create Virtual Environment

```bash
python -m venv venv

# On Windows
venv\Scripts\activate

# On Linux/Mac
source venv/bin/activate
```

### 3. Install Dependencies

```bash
# Install ingestion pipeline dependencies
pip install -r ingestion_pipeline/requirements.txt

# Install retrieval generation dependencies
pip install -r retrieval_generation/requirements.txt

# Install additional dependencies for API
pip install fastapi uvicorn python-dotenv
```

### 4. Download Models (One-time Setup)

```bash
# Download all required models for offline operation
python ingestion_pipeline/setup_offline.py
```

This will download:
- SentenceTransformer model (`BAAI/bge-base-en`)
- SigLIP image model (`google/siglip-base-patch16-224`)
- Whisper model (`base.en`)
- EasyOCR models (English by default)

### 5. Install and Setup Ollama

```bash
# Install Ollama from https://ollama.ai
# Then pull a model
ollama pull phi3:mini
# or
ollama pull llama2
```

## 🚀 Quick Start

### Option 1: Using the Unified API

```bash
# Start the FastAPI server
python api_main.py

# Or using uvicorn directly
uvicorn api_main:app --reload --port 8000
```

The API will be available at:
- **API**: http://localhost:8000
- **Interactive Docs**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Option 2: Using Python Client

```python
from retrieval_generation.rag_client import create_rag_client

# Initialize RAG client
rag = create_rag_client()

# Ingest documents
rag.upload_file("document.pdf")
rag.ingest_directory("./documents")

# Query the knowledge base
result = rag.generate_answer("What is this about?", top_k=5)
print(result['answer'])
print(f"Sources: {len(result['sources'])}")
```

### Option 3: Using the Desktop Application

```bash
cd rag_desktop_ui
pip install -r requirements.txt
python main.py
```

### Option 4: Using the React Web UI

```bash
cd rag-ui-react
npm install
npm run dev
```

## 📖 Usage Examples

### Upload and Ingest Documents

```python
from ingestion_pipeline.client import create_client

# Create ingestion client
client = create_client()

# Upload a single file
result = client.upload_file("document.pdf")
print(f"Processed {result['chunks_processed']} chunks")

# Ingest entire directory
result = client.ingest_directory("./documents", batch_size=100)
print(f"Processed {len(result['files_processed'])} files")
```

### Semantic Search

```python
from retrieval_generation.retriever import RetrievalSystem

retriever = RetrievalSystem()

# Text query
results = retriever.get_context("machine learning", top_k=10)

# Image query
results = retriever.get_context("./image.jpg", query_type='image', top_k=10)

# Filtered search
results = retriever.get_context("AI", filter_type='text', top_k=5)
```

### Generate Answers

```python
from retrieval_generation.rag_client import create_rag_client

rag = create_rag_client()

# Basic query
result = rag.generate_answer("What are the main topics?", top_k=5)
print(result['answer'])

# With filtering
result = rag.generate_answer(
    "What images are available?",
    filter_type='image',
    top_k=5
)
```

### Using the REST API

```bash
# Upload a file
curl -X POST "http://localhost:8000/api/ingestion/upload" \
  -F "file=@document.pdf"

# Query the knowledge base
curl -X POST "http://localhost:8000/api/query" \
  -H "Content-Type: application/json" \
  -d '{"query": "What is this about?", "top_k": 5}'
```

## 🏗️ Project Structure

```
unified-rag-platform/
├── api_main.py                 # Unified FastAPI application
├── ingestion_pipeline/          # Document processing module
│   ├── client.py               # Ingestion client
│   ├── parsers.py              # File parsers (PDF, DOCX, images, audio)
│   ├── ingest.py               # Ingestion logic
│   ├── setup_offline.py        # Model download script
│   └── README.md               # Detailed ingestion docs
├── retrieval_generation/        # Search and generation module
│   ├── rag_client.py            # Unified RAG client
│   ├── retriever.py             # Semantic search engine
│   ├── generator.py            # LLM answer generation
│   └── README.md                # Detailed retrieval docs
├── rag-ui-react/                # React web interface
│   ├── src/
│   │   ├── components/          # React components
│   │   └── App.jsx              # Main app component
│   └── package.json
├── rag_desktop_ui/              # PyQt5 desktop application
│   ├── main.py                 # Desktop app entry point
│   └── ui/                      # UI components
├── ui/                          # Vanilla JS web interface
│   ├── index.html
│   ├── app.js
│   └── styles.css
└── README.md                    # This file
```

## ⚙️ Configuration

Create a `.env` file in the root directory:

```env
# Database
CHROMA_DB_PATH=chroma_local_db

# Embedding Models
TEXT_MODEL=BAAI/bge-base-en
IMAGE_MODEL=google/siglip-base-patch16-224
OFFLINE_MODE=1

# OCR Settings
USE_OCR=1
OCR_LANGUAGES=en

# Ollama Configuration
OLLAMA_URL=http://localhost:11434
OLLAMA_MODEL=phi3:mini
OLLAMA_TIMEOUT=60

# API Settings
PORT=8000
HOST=0.0.0.0
CORS_ORIGINS=*
```

## 🔧 API Endpoints

### Ingestion Endpoints

- `POST /api/ingestion/upload` - Upload and ingest a single file
- `POST /api/ingestion/directory` - Ingest all files from a directory
- `GET /api/ingestion/collection/info` - Get collection information
- `GET /api/ingestion/collection/count` - Get item count

### Query Endpoints

- `POST /api/query` - Ask a question and get an answer
- `GET /health` - Health check endpoint
- `GET /` - API information

See the interactive API documentation at `/docs` for detailed endpoint information.

## 🧪 Testing

```bash
# Test ingestion pipeline
cd ingestion_pipeline
python test.py

# Test retrieval system
cd retrieval_generation
python test.py

# Test Ollama connection
python test_ollama.py
```

## 📚 Documentation

- [Ingestion Pipeline README](ingestion_pipeline/README.md) - Detailed ingestion documentation
- [Retrieval & Generation README](retrieval_generation/README.md) - Detailed retrieval documentation
- [API Documentation](http://localhost:8000/docs) - Interactive API docs (when server is running)

## 🛠️ Technologies Used

### Backend
- **FastAPI** - Modern, fast web framework
- **ChromaDB** - Vector database for embeddings
- **SentenceTransformers** - Text embeddings
- **HuggingFace Transformers** - Image embeddings
- **OpenAI Whisper** - Audio transcription
- **EasyOCR** - Optical character recognition
- **Ollama** - LLM inference

### Frontend
- **React 18** - Web UI framework
- **PyQt5** - Desktop application framework
- **Vite** - Build tool for React

### Data Processing
- **PyMuPDF** - PDF processing
- **python-docx** - DOCX processing
- **Pillow** - Image processing

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [ChromaDB](https://www.trychroma.com/) for the vector database
- [SentenceTransformers](https://www.sbert.net/) for text embeddings
- [HuggingFace](https://huggingface.co/) for transformer models
- [Ollama](https://ollama.ai/) for LLM inference
- [EasyOCR](https://github.com/JaidedAI/EasyOCR) for OCR capabilities

## 📧 Contact

For questions or support, please open an issue on GitHub.

---

**⭐ If you find this project useful, please consider giving it a star!**

