"""
Unified RAG API - Main Application

Production-ready FastAPI application integrating:
- Ingestion: Upload and process documents, images, and audio files
- Query Orchestrator: Search and generate answers in one endpoint

This is the main API endpoint for UI integration.
"""

import os
import sys
import tempfile
import shutil
import time
from pathlib import Path
from typing import List, Optional, Dict, Any, Union
from dotenv import load_dotenv

import uvicorn
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

# Add paths for imports
current_dir = Path(__file__).parent
ingestion_dir = current_dir / "ingestion_pipeline"
retrieval_dir = current_dir / "retrieval_generation"
sys.path.insert(0, str(ingestion_dir))
sys.path.insert(0, str(retrieval_dir))

# Import ingestion components
try:
    from client import IngestionClient, create_client
    from logger_config import setup_logger
except ImportError:
    # Try absolute import if running from project root
    from ingestion_pipeline.client import IngestionClient, create_client
    from ingestion_pipeline.logger_config import setup_logger

# Import generation component only
try:
    from generator import get_grounded_answer
except ImportError:
    # Try absolute import if running from project root
    from retrieval_generation.generator import get_grounded_answer

# Load environment variables
load_dotenv()

# Setup logging
logger = setup_logger(__name__, log_file="api_main.log")

# Initialize FastAPI app
app = FastAPI(
    title="Unified RAG API",
    description="Complete RAG system API with ingestion, retrieval, and generation",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware for UI integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("CORS_ORIGINS", "*").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global client instances
ingestion_client: Optional[IngestionClient] = None


# ============================================================================
# Pydantic Models
# ============================================================================

class DirectoryIngestRequest(BaseModel):
    directory_path: str = Field(..., description="Path to directory containing files to ingest")
    batch_size: int = Field(default=100, ge=1, le=1000, description="Batch size for insertion")


class QueryRequest(BaseModel):
    query: str = Field(..., description="User question/query")
    top_k: int = Field(default=10, ge=1, le=100, description="Number of top results to retrieve")
    where: Optional[dict] = Field(default=None, description="Optional metadata filter for search")


class IngestResponse(BaseModel):
    message: str
    chunks_processed: int
    total_items_in_collection: int
    files_processed: List[str]


class QueryResponse(BaseModel):
    answer: str
    sources: List[Dict]
    source_count: int


# ============================================================================
# Startup/Shutdown Events
# ============================================================================

@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    global ingestion_client
    
    try:
        logger.info("Initializing Unified RAG API...")
        
        # Initialize ingestion client
        db_path = os.getenv("CHROMA_DB_PATH", "chroma_local_db")
        text_model = os.getenv("TEXT_MODEL", "BAAI/bge-base-en")
        image_model = os.getenv("IMAGE_MODEL", "google/siglip-base-patch16-224")
        offline_mode = os.getenv("OFFLINE_MODE", "1").lower() in ("1", "true", "yes")
        use_ocr = os.getenv("USE_OCR", "1").lower() in ("1", "true", "yes")
        ocr_languages = os.getenv("OCR_LANGUAGES", "en").split(",")
        
        logger.info(f"DB Path: {db_path}")
        logger.info(f"Text Model: {text_model}")
        logger.info(f"Image Model: {image_model}")
        logger.info(f"Offline Mode: {offline_mode}")
        logger.info(f"Use OCR: {use_ocr}")
        
        ingestion_client = create_client(
            db_path=db_path,
            text_model=text_model,
            image_model=image_model,
            offline_mode=offline_mode,
            use_ocr=use_ocr,
            ocr_languages=ocr_languages
        )
        
        logger.info("✓ Unified RAG API initialized successfully")
        
    except Exception as e:
        logger.error(f"Failed to initialize API: {e}", exc_info=True)
        raise


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("Shutting down Unified RAG API...")


# ============================================================================
# Health & Info Endpoints
# ============================================================================

@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "Unified RAG API",
        "version": "1.0.0",
        "status": "operational",
        "endpoints": {
            "ingestion": {
                "upload": "POST /api/ingestion/upload",
                "ingest_directory": "POST /api/ingestion/directory",
                "collection_info": "GET /api/ingestion/collection/info",
                "collection_count": "GET /api/ingestion/collection/count"
            },
            "query": {
                "query": "POST /api/query - Ask a question and get an answer"
            }
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        if ingestion_client is None:
            return JSONResponse(
                status_code=503,
                content={"status": "unhealthy", "message": "Ingestion client not initialized"}
            )
        
        health = ingestion_client.health_check()
        return {
            "status": health.get("status", "unknown"),
            "ingestion": health,
            "api": "operational"
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}", exc_info=True)
        return JSONResponse(
            status_code=503,
            content={"status": "unhealthy", "message": str(e)}
        )


# ============================================================================
# Ingestion Endpoints
# ============================================================================

@app.post("/api/ingestion/upload", response_model=IngestResponse)
async def upload_file(
    file: UploadFile = File(..., description="File to upload and ingest")
):
    """
    Upload and ingest a single file (PDF, DOCX, image, or audio).
    
    Supported formats:
    - Documents: PDF, DOCX
    - Images: JPG, PNG, GIF, BMP, WEBP
    - Audio: MP3, WAV, M4A, FLAC
    """
    if ingestion_client is None:
        raise HTTPException(status_code=503, detail="Ingestion client not initialized")
    
    # Check file extension
    file_ext = Path(file.filename).suffix.lower()
    if file_ext not in ingestion_client.pipeline.supported_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type. Supported: {list(ingestion_client.pipeline.supported_extensions.keys())}"
        )
    
    tmp_file_path = None
    try:
        # Save uploaded file to temporary location
        with tempfile.NamedTemporaryFile(delete=False, suffix=file_ext) as tmp_file:
            shutil.copyfileobj(file.file, tmp_file)
            tmp_file_path = tmp_file.name
        
        # Process the file
        result = ingestion_client.upload_file(tmp_file_path)
        
        return IngestResponse(
            message=result["message"],
            chunks_processed=result["chunks_processed"],
            total_items_in_collection=result["total_items_in_collection"],
            files_processed=result["files_processed"]
        )
    
    except HTTPException:
        raise
    except RuntimeError as e:
        # Check if it's an ffmpeg-related error
        error_msg = str(e).lower()
        if 'ffmpeg' in error_msg:
            logger.error(f"ffmpeg error: {e}", exc_info=True)
            raise HTTPException(
                status_code=400,
                detail=f"Audio processing failed: {str(e)}"
            )
        logger.error(f"Runtime error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")
    except Exception as e:
        logger.error(f"Error processing file: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")
    
    finally:
        # Clean up temporary file
        if tmp_file_path and os.path.exists(tmp_file_path):
            try:
                time.sleep(0.1)  # Small delay for Windows file handle release
                os.unlink(tmp_file_path)
            except (PermissionError, OSError) as e:
                logger.warning(f"Could not delete temporary file {tmp_file_path}: {e}")


@app.post("/api/ingestion/directory", response_model=IngestResponse)
async def ingest_directory(request: DirectoryIngestRequest):
    """Ingest all supported files from a directory"""
    if ingestion_client is None:
        raise HTTPException(status_code=503, detail="Ingestion client not initialized")
    
    try:
        result = ingestion_client.ingest_directory(
            directory_path=request.directory_path,
            batch_size=request.batch_size
        )
        
        return IngestResponse(
            message=result["message"],
            chunks_processed=result["chunks_processed"],
            total_items_in_collection=result["total_items_in_collection"],
            files_processed=result["files_processed"]
        )
    
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error ingesting directory: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error ingesting directory: {str(e)}")


@app.get("/api/ingestion/collection/info")
async def get_collection_info():
    """Get information about the ChromaDB collection"""
    if ingestion_client is None:
        raise HTTPException(status_code=503, detail="Ingestion client not initialized")
    
    try:
        info = ingestion_client.get_collection_info()
        return info
    except Exception as e:
        logger.error(f"Error getting collection info: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error getting collection info: {str(e)}")


@app.get("/api/ingestion/collection/count")
async def get_collection_count():
    """Get the total number of items in the collection"""
    if ingestion_client is None:
        raise HTTPException(status_code=503, detail="Ingestion client not initialized")
    
    try:
        count = ingestion_client.get_collection_count()
        return {"count": count}
    except Exception as e:
        logger.error(f"Error getting collection count: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error getting collection count: {str(e)}")


# ============================================================================
# Query Orchestrator Endpoint
# ============================================================================

def format_search_results_to_context_chunks(search_results: Dict[str, Any]) -> List[Dict]:
    """
    Convert ingestion client search results to generator's expected format.
    
    Ingestion search returns:
    {
        "ids": [[id1, id2, ...]],
        "distances": [[0.1, 0.2, ...]],
        "documents": [["content1", "content2", ...]],
        "metadatas": [[{metadata1}, {metadata2}, ...]]
    }
    
    Generator expects:
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
    """
    context_chunks = []
    
    # Extract the first query's results (since we only query with one vector)
    ids_list = search_results.get("ids", [[]])[0] if search_results.get("ids") else []
    distances_list = search_results.get("distances", [[]])[0] if search_results.get("distances") else []
    documents_list = search_results.get("documents", [[]])[0] if search_results.get("documents") else []
    metadatas_list = search_results.get("metadatas", [[{}]])[0] if search_results.get("metadatas") else []
    
    # Build formatted context chunks
    num_results = len(ids_list)
    for i in range(num_results):
        chunk_id = ids_list[i] if i < len(ids_list) else None
        distance = distances_list[i] if i < len(distances_list) else None
        document = documents_list[i] if i < len(documents_list) else "N/A"
        metadata = metadatas_list[i] if i < len(metadatas_list) else {}
        
        # Extract source and type from metadata
        source = metadata.get("source_file", "unknown") if isinstance(metadata, dict) else "unknown"
        content_type = metadata.get("type", "text") if isinstance(metadata, dict) else "text"
        
        # Convert distance to score (lower distance = higher score, so we use 1 - distance)
        # If distance is None, set score to None
        score = (1.0 - distance) if distance is not None else None
        
        context_chunk = {
            "id": chunk_id,
            "score": score,
            "source": source,
            "type": content_type,
            "content": document,
            "metadata": metadata if isinstance(metadata, dict) else {}
        }
        
        context_chunks.append(context_chunk)
    
    return context_chunks


@app.post("/api/query", response_model=QueryResponse)
async def query_orchestrator(request: QueryRequest):
    """
    Query orchestrator: Search the knowledge base and generate an answer.
    
    This endpoint:
    1. Searches the knowledge base using ingestion client's search method
    2. Formats the search results for the generator
    3. Generates a grounded answer using the LLM
    4. Returns the answer with sources
    
    This is the main endpoint for UI queries.
    """
    if ingestion_client is None:
        raise HTTPException(status_code=503, detail="Ingestion client not initialized")
    
    try:
        # Step 1: Search the knowledge base using ingestion client
        logger.info(f"Searching for query: {request.query[:50]}...")
        search_results = ingestion_client.search(
            query_text=request.query,
            n_results=request.top_k,
            where=request.where
        )
        
        # Step 2: Format search results to context chunks format
        context_chunks = format_search_results_to_context_chunks(search_results)
        
        if not context_chunks:
            # No results found
            return QueryResponse(
                answer="I could not find any relevant information in the knowledge base to answer your question.",
                sources=[],
                source_count=0
            )
        
        logger.info(f"Found {len(context_chunks)} context chunks, generating answer...")
        
        # Step 3: Generate answer using generator
        result = get_grounded_answer(
            question=request.query,
            context_chunks=context_chunks
        )
        
        logger.info("Answer generated successfully")
        
        # Step 4: Return the result
        return QueryResponse(
            answer=result["answer"],
            sources=result["sources"],
            source_count=len(result["sources"])
        )
    
    except Exception as e:
        logger.error(f"Error in query orchestrator: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error processing query: {str(e)}")


# ============================================================================
# Main Entry Point
# ============================================================================

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    host = os.getenv("HOST", "0.0.0.0")
    
    logger.info(f"Starting Unified RAG API on {host}:{port}")
    uvicorn.run(app, host=host, port=port, log_level="info")

