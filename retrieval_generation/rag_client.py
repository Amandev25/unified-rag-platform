"""
Unified RAG Client
Integrates ingestion pipeline client with retrieval and generation systems
"""
import os
import sys
from pathlib import Path
from typing import List, Dict, Union, Optional, Any
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Add ingestion_pipeline to path
current_dir = Path(__file__).parent
parent_dir = current_dir.parent
ingestion_dir = parent_dir / "ingestion_pipeline"
sys.path.insert(0, str(ingestion_dir))

try:
    from PIL import Image
except ImportError:
    raise ImportError("Pillow package not found. Please install it using: pip install pillow")

# Import from ingestion pipeline (using sys.path that was added above)
try:
    from client import IngestionClient
except ImportError:
    # Try absolute import if running from project root
    from ingestion_pipeline.client import IngestionClient

# Import from retrieval_generation
try:
    from retriever import RetrievalSystem
    from generator import get_grounded_answer
    from config import RAGConfig
except ImportError:
    # Try absolute import if running from project root
    from retrieval_generation.retriever import RetrievalSystem
    from retrieval_generation.generator import get_grounded_answer
    from retrieval_generation.config import RAGConfig


class RAGClient:
    """
    Unified RAG Client that integrates:
    - Document ingestion (from ingestion_pipeline)
    - Context retrieval (from retrieval_generation)
    - Answer generation (from retrieval_generation)
    """
    
    def __init__(
        self,
        db_path: str = "chroma_local_db",
        text_model: str = "BAAI/bge-base-en",
        image_model: str = "google/siglip-base-patch16-224",
        offline_mode: bool = True
    ):
        """
        Initialize the unified RAG client.
        
        Args:
            db_path: Path to ChromaDB storage directory
            text_model: SentenceTransformer model for text embeddings
            image_model: HuggingFace model for image embeddings
            offline_mode: If True, only use cached models (no downloads)
        """
        print("=" * 60)
        print("Initializing Unified RAG Client")
        print("=" * 60)
        
        # Determine absolute path to db_path relative to ingestion_pipeline
        if not Path(db_path).is_absolute():
            db_path = str(ingestion_dir / db_path)
        
        # Initialize ingestion client (for database operations and ingestion)
        print("\n[1/2] Initializing Ingestion Client...")
        self.ingestion_client = IngestionClient(
            db_path=db_path,
            text_model=text_model,
            image_model=image_model,
            offline_mode=offline_mode
        )
        print("✓ Ingestion Client ready")
        
        # For retrieval, we'll use a lightweight wrapper around the ingestion client
        # instead of creating a separate RetrievalSystem (which would duplicate model loading)
        print("\n[2/2] Setting up Retrieval System...")
        print("  (Reusing loaded models for efficiency)")
        
        # Create a minimal retrieval system that reuses the ingestion client's resources
        self._setup_retrieval_system(db_path, text_model, image_model, offline_mode)
        
        print("✓ Retrieval System ready")
        
        print("\n" + "=" * 60)
        print("RAG Client initialized successfully!")
        print(f"Database: {db_path}")
        print(f"Collection items: {self.get_collection_count()}")
        print("=" * 60 + "\n")
    
    def _setup_retrieval_system(self, db_path, text_model, image_model, offline_mode):
        """
        Set up retrieval system by reusing loaded models from ingestion client.
        This avoids loading the same large models twice.
        """
        # Store references to avoid reloading
        self.text_embedding_model = self.ingestion_client.pipeline.text_embedding_model
        self.image_model = self.ingestion_client.pipeline.image_model
        self.image_processor = self.ingestion_client.pipeline.image_processor
        self.collection = self.ingestion_client.pipeline.collection
        self.db_path = db_path
    
    # ========== INGESTION METHODS (from IngestionClient) ==========
    
    def upload_file(self, file_path: str) -> Dict[str, Any]:
        """
        Upload and ingest a single file (PDF, DOCX, image, or audio).
        
        Args:
            file_path: Path to file to upload and ingest
            
        Returns:
            Dictionary with ingestion results
        """
        return self.ingestion_client.upload_file(file_path)
    
    def ingest_directory(self, directory_path: str, batch_size: int = 100) -> Dict[str, Any]:
        """
        Ingest all supported files from a directory.
        
        Args:
            directory_path: Path to directory containing files to ingest
            batch_size: Number of items to batch before inserting into ChromaDB
            
        Returns:
            Dictionary with ingestion results
        """
        return self.ingestion_client.ingest_directory(directory_path, batch_size)
    
    def get_collection_info(self) -> Dict[str, Any]:
        """Get information about the ChromaDB collection."""
        return self.ingestion_client.get_collection_info()
    
    def get_collection_count(self) -> int:
        """Get the total number of items in the collection."""
        return self.ingestion_client.get_collection_count()
    
    def get_item(self, item_id: str) -> Dict[str, Any]:
        """Get a specific item from the collection by ID."""
        return self.ingestion_client.get_item(item_id)
    
    def delete_item(self, item_id: str) -> Dict[str, str]:
        """Delete a specific item from the collection by ID."""
        return self.ingestion_client.delete_item(item_id)
    
    # ========== RETRIEVAL METHODS (from RetrievalSystem) ==========
    
    def retrieve_context(
        self,
        query: Union[str, Image.Image],
        query_type: str = 'text',
        top_k: Optional[int] = None,
        filter_type: Optional[str] = None
    ) -> List[Dict]:
        """
        Retrieve relevant context chunks for a query.
        
        Uses the loaded embedding models to perform semantic search in ChromaDB.
        
        Args:
            query: Text string or image (path or PIL Image)
            query_type: Type of query - 'text' or 'image' (default: 'text')
            top_k: Number of top results to return (default: uses RAGConfig.DEFAULT_TOP_K)
            filter_type: Optional filter by type ('text', 'image', 'audio')
            
        Returns:
            List of formatted context chunks with structure:
            [
                {
                    "id": "report.pdf_chunk_1",
                    "score": 0.85,
                    "source": "report.pdf",
                    "type": "text",
                    "content": "...",
                    "metadata": {"page": 3}
                },
                ...
            ]
        """
        # Use DEFAULT_TOP_K from config if top_k not specified
        if top_k is None:
            top_k = RAGConfig.DEFAULT_TOP_K
        # Generate query embedding
        query_vector = self._embed_query(query, query_type)
        
        # Search in ChromaDB
        raw_results = self.collection.query(
            query_embeddings=[query_vector.tolist()],
            n_results=top_k,
            include=["documents", "metadatas", "distances"]
        )
        
        # Format results
        results = self._format_results(raw_results)
        
        # Apply filter if specified
        if filter_type:
            results = [r for r in results if r.get('type') == filter_type]
        
        return results
    
    def _embed_query(self, query: Union[str, Image.Image], query_type: str) -> Any:
        """Generate embedding for a query"""
        import torch
        import numpy as np
        
        if query_type == 'text':
            if isinstance(query, str):
                embedding = self.text_embedding_model.encode(
                    query,
                    normalize_embeddings=False,
                    show_progress_bar=False,
                    convert_to_numpy=True
                )
            else:
                raise ValueError("Text query must be a string")
        
        elif query_type == 'image':
            if isinstance(query, str):
                # Load image from path
                try:
                    image = Image.open(query).convert("RGB")
                except Exception as e:
                    raise ValueError(f"Failed to open image file '{query}': {str(e)}")
            elif isinstance(query, Image.Image):
                image = query.convert("RGB") if query.mode != "RGB" else query
            else:
                raise ValueError("Image query must be a file path (string) or PIL Image object")
            
            # Use SigLIP to encode
            inputs = self.image_processor(images=image, return_tensors="pt")
            with torch.no_grad():
                image_embeds = self.image_model.get_image_features(**inputs)
            image_embeds = image_embeds / image_embeds.norm(p=2, dim=-1, keepdim=True)
            embedding = image_embeds.squeeze().cpu().numpy()
        
        else:
            raise ValueError(f"Invalid query_type: {query_type}. Must be 'text' or 'image'")
        
        return embedding
    
    def _format_results(self, raw_results: Dict) -> List[Dict]:
        """Format raw ChromaDB results into clean list of dicts"""
        formatted_results = []
        
        if not raw_results:
            return formatted_results
        
        ids = raw_results.get('ids', [[]])[0]
        distances = raw_results.get('distances', [[]])[0]
        documents = raw_results.get('documents', [[]])[0]
        metadatas = raw_results.get('metadatas', [[]])[0]
        
        for i in range(len(ids)):
            metadata = metadatas[i] if i < len(metadatas) else {}
            formatted_result = {
                "id": ids[i] if i < len(ids) else None,
                "score": distances[i] if i < len(distances) else None,
                "source": metadata.get('source_file', 'unknown') if isinstance(metadata, dict) else 'unknown',
                "type": metadata.get('type', 'unknown') if isinstance(metadata, dict) else 'unknown',
                "content": documents[i] if i < len(documents) else 'N/A',
                "metadata": metadata if isinstance(metadata, dict) else {}
            }
            formatted_results.append(formatted_result)
        
        return formatted_results
    
    def search_by_text(
        self,
        query_text: str,
        n_results: int = 10,
        where: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Search the collection using the ingestion client's search method.
        This is an alternative search that uses the client's direct search.
        
        Args:
            query_text: Text query to search for
            n_results: Number of results to return (default: 10)
            where: Optional metadata filter (e.g., {"type": "text"})
            
        Returns:
            Dictionary with raw search results from ChromaDB
        """
        return self.ingestion_client.search(query_text, n_results, where)
    
    # ========== GENERATION METHODS ==========
    
    def generate_answer(
        self,
        question: str,
        query_type: str = 'text',
        top_k: Optional[int] = None,
        filter_type: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Complete RAG pipeline: retrieve context and generate answer.
        
        This is the main method that combines retrieval and generation.
        
        Args:
            question: User's question (text string)
            query_type: Type of query for retrieval - 'text' or 'image' (default: 'text')
            top_k: Number of context chunks to retrieve (default: uses RAGConfig.DEFAULT_TOP_K)
            filter_type: Optional filter by type ('text', 'image', 'audio')
            
        Returns:
            Dictionary with:
                - answer: Generated answer with citations
                - sources: List of source chunks used
                - query: Original question
                - context_count: Number of context chunks used
        """
        # Use DEFAULT_TOP_K from config if top_k not specified
        if top_k is None:
            top_k = RAGConfig.DEFAULT_TOP_K
        # Step 1: Retrieve context
        print(f"\n[RAG] Retrieving context for query: '{question[:100]}...'")
        context_chunks = self.retrieve_context(
            query=question,
            query_type=query_type,
            top_k=top_k,
            filter_type=filter_type
        )
        
        print(f"[RAG] Retrieved {len(context_chunks)} context chunks")
        
        if not context_chunks:
            return {
                "answer": "I couldn't find any relevant information to answer your question.",
                "sources": [],
                "query": question,
                "context_count": 0
            }
        
        # Step 2: Generate answer
        print(f"[RAG] Generating answer...")
        result = get_grounded_answer(question, context_chunks)
        
        # Enhance result with additional metadata
        result['query'] = question
        result['context_count'] = len(context_chunks)
        
        print(f"[RAG] Answer generated successfully!\n")
        return result
    
    def generate_answer_with_custom_context(
        self,
        question: str,
        context_chunks: List[Dict]
    ) -> Dict[str, Any]:
        """
        Generate answer using custom/pre-retrieved context chunks.
        
        Args:
            question: User's question
            context_chunks: Pre-retrieved context chunks
            
        Returns:
            Dictionary with answer and sources
        """
        result = get_grounded_answer(question, context_chunks)
        result['query'] = question
        result['context_count'] = len(context_chunks)
        return result
    
    # ========== UTILITY METHODS ==========
    
    def health_check(self) -> Dict[str, Any]:
        """Check the health status of the RAG system."""
        return self.ingestion_client.health_check()
    
    def get_stats(self) -> Dict[str, Any]:
        """Get statistics about the RAG system."""
        info = self.get_collection_info()
        
        # Get type distribution by sampling
        try:
            sample_results = self.ingestion_client.search("", n_results=min(100, info['count']))
            type_counts = {}
            for metadata in sample_results['metadatas'][0]:
                doc_type = metadata.get('type', 'unknown')
                type_counts[doc_type] = type_counts.get(doc_type, 0) + 1
        except:
            type_counts = {}
        
        return {
            "collection_name": info['name'],
            "total_items": info['count'],
            "type_distribution": type_counts,
            "database_path": self.db_path  # Use the db_path we stored during init
        }


# Convenience function for quick usage
def create_rag_client(
    db_path: str = None,
    text_model: str = None,
    image_model: str = None,
    offline_mode: bool = True
) -> RAGClient:
    """
    Create a RAGClient with default or custom settings.
    
    Args:
        db_path: Path to ChromaDB (default: "chroma_local_db" or CHROMA_DB_PATH env var)
        text_model: Text embedding model (default: "BAAI/bge-base-en" or TEXT_MODEL env var)
        image_model: Image embedding model (default: "google/siglip-base-patch16-224" or IMAGE_MODEL env var)
        offline_mode: Offline mode flag (default: True or OFFLINE_MODE env var)
        
    Returns:
        Initialized RAGClient instance
    """
    # Use environment variables if not provided
    if db_path is None:
        db_path = os.getenv("CHROMA_DB_PATH", "chroma_local_db")
    if text_model is None:
        text_model = os.getenv("TEXT_MODEL", "BAAI/bge-base-en")
    if image_model is None:
        image_model = os.getenv("IMAGE_MODEL", "google/siglip-base-patch16-224")
    if offline_mode:
        offline_mode = os.getenv("OFFLINE_MODE", "1").lower() in ("1", "true", "yes")
    
    return RAGClient(
        db_path=db_path,
        text_model=text_model,
        image_model=image_model,
        offline_mode=offline_mode
    )


if __name__ == "__main__":
    """Example usage of the RAGClient"""
    
    # Initialize client
    print("Creating RAG Client...")
    rag = create_rag_client()
    
    # Get stats
    print("\nRAG System Stats:")
    stats = rag.get_stats()
    for key, value in stats.items():
        print(f"  {key}: {value}")
    
    # Example: Ask a question
    print("\n" + "=" * 60)
    print("Example Query")
    print("=" * 60)
    
    question = "What information do you have about development?"
    print(f"\nQuestion: {question}")
    
    try:
        result = rag.generate_answer(question, top_k=5)
        print(f"\nAnswer:\n{result['answer']}")
        print(f"\nUsed {result['context_count']} context chunks")
    except Exception as e:
        print(f"Error: {e}")

