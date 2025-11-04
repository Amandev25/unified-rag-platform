"""
Configuration file for the RAG System
Centralizes all configuration settings
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class RAGConfig:
    """Configuration for the RAG system"""
    
    # Database settings
    CHROMA_DB_PATH = os.getenv("CHROMA_DB_PATH", "../ingestion_pipeline/chroma_local_db")
    COLLECTION_NAME = os.getenv("COLLECTION_NAME", "multimodal_collection")
    
    # Model settings
    TEXT_MODEL = os.getenv("TEXT_MODEL", "BAAI/bge-base-en")
    IMAGE_MODEL = os.getenv("IMAGE_MODEL", "google/siglip-base-patch16-224")
    OFFLINE_MODE = os.getenv("OFFLINE_MODE", "1").lower() in ("1", "true", "yes")
    
    # Ollama settings (for generation)
    OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")
    OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "gemma:2b")
    OLLAMA_TIMEOUT = int(os.getenv("OLLAMA_TIMEOUT", "60"))
    
    # Retrieval settings
    DEFAULT_TOP_K = int(os.getenv("DEFAULT_TOP_K", "3"))
    
    # Audio processing settings (from ingestion pipeline)
    WHISPER_MODEL = os.getenv("WHISPER_MODEL", "base.en")
    AUDIO_CHUNK_DURATION = int(os.getenv("AUDIO_CHUNK_DURATION", "10"))
    
    # Text chunking settings (from ingestion pipeline)
    TEXT_CHUNK_SIZE = int(os.getenv("TEXT_CHUNK_SIZE", "1000"))
    TEXT_CHUNK_OVERLAP = int(os.getenv("TEXT_CHUNK_OVERLAP", "50"))
    
    @classmethod
    def print_config(cls):
        """Print current configuration"""
        print("=" * 60)
        print("RAG System Configuration")
        print("=" * 60)
        print("\n[Database]")
        print(f"  ChromaDB Path: {cls.CHROMA_DB_PATH}")
        print(f"  Collection: {cls.COLLECTION_NAME}")
        print("\n[Embedding Models]")
        print(f"  Text Model: {cls.TEXT_MODEL}")
        print(f"  Image Model: {cls.IMAGE_MODEL}")
        print(f"  Offline Mode: {cls.OFFLINE_MODE}")
        print("\n[LLM (Ollama)]")
        print(f"  URL: {cls.OLLAMA_URL}")
        print(f"  Model: {cls.OLLAMA_MODEL}")
        print(f"  Timeout: {cls.OLLAMA_TIMEOUT}s")
        print("\n[Retrieval]")
        print(f"  Default Top-K: {cls.DEFAULT_TOP_K}")
        print("\n[Audio Processing]")
        print(f"  Whisper Model: {cls.WHISPER_MODEL}")
        print(f"  Chunk Duration: {cls.AUDIO_CHUNK_DURATION}s")
        print("\n[Text Processing]")
        print(f"  Chunk Size: {cls.TEXT_CHUNK_SIZE}")
        print(f"  Chunk Overlap: {cls.TEXT_CHUNK_OVERLAP}")
        print("=" * 60)
    
    @classmethod
    def to_dict(cls):
        """Convert config to dictionary"""
        return {
            "database": {
                "chroma_db_path": cls.CHROMA_DB_PATH,
                "collection_name": cls.COLLECTION_NAME
            },
            "models": {
                "text_model": cls.TEXT_MODEL,
                "image_model": cls.IMAGE_MODEL,
                "offline_mode": cls.OFFLINE_MODE
            },
            "ollama": {
                "url": cls.OLLAMA_URL,
                "model": cls.OLLAMA_MODEL,
                "timeout": cls.OLLAMA_TIMEOUT
            },
            "retrieval": {
                "default_top_k": cls.DEFAULT_TOP_K
            },
            "audio": {
                "whisper_model": cls.WHISPER_MODEL,
                "chunk_duration": cls.AUDIO_CHUNK_DURATION
            },
            "text": {
                "chunk_size": cls.TEXT_CHUNK_SIZE,
                "chunk_overlap": cls.TEXT_CHUNK_OVERLAP
            }
        }




if __name__ == "__main__":
    # Print configuration when run directly
    RAGConfig.print_config()

