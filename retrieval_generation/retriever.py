"""
Person 2: Retrieval (Augmentation) Specialist
Multimodal RAG System - Retrieval Module

High-level Goal: Given a query (text or image), find the most relevant data chunks from ChromaDB.

Updated to match Person 1's setup:
- Text embeddings: BAAI/bge-base-en (via SentenceTransformer)
- Image embeddings: google/siglip-base-patch16-224 (via transformers)
- Database path: chroma_local_db (matches Person 1)
- Collection name: multimodal_collection (matches Person 1)
"""

import os
from typing import List, Dict, Union

try:
    import chromadb  # type: ignore
except ImportError:
    raise ImportError(
        "chromadb package not found. Please install it using: pip install chromadb"
    )

try:
    from sentence_transformers import SentenceTransformer  # type: ignore
except ImportError:
    raise ImportError(
        "sentence-transformers package not found. Please install it using: pip install sentence-transformers"
    )

try:
    from transformers import AutoProcessor, AutoModel  # type: ignore
except ImportError:
    raise ImportError(
        "transformers package not found. Please install it using: pip install transformers"
    )

try:
    from PIL import Image  # type: ignore
except ImportError:
    raise ImportError(
        "Pillow package not found. Please install it using: pip install pillow"
    )

try:
    import numpy as np  # type: ignore
except ImportError:
    raise ImportError(
        "NumPy package not found. Please install it using: pip install numpy"
    )

try:
    import torch  # type: ignore
except ImportError:
    raise ImportError(
        "torch package not found. Please install it using: pip install torch"
    )


class RetrievalSystem:
    """Retrieval system for multimodal RAG.
    
    Matches Person 1's embedding models and database configuration:
    - Text: BAAI/bge-base-en
    - Image: google/siglip-base-patch16-224
    - DB: chroma_local_db
    - Collection: multimodal_collection
    """
    
    def __init__(
        self, 
        db_path: str = "chroma_local_db", 
        collection_name: str = "multimodal_collection",
        text_model: str = "BAAI/bge-base-en",
        image_model: str = "google/siglip-base-patch16-224",
        offline_mode: bool = True
    ):
        """
        Initialize the retrieval system.
        
        Args:
            db_path: Path to the ChromaDB database directory (default: chroma_local_db)
            collection_name: Name of the collection in ChromaDB (default: multimodal_collection)
            text_model: SentenceTransformer model for text embeddings (default: BAAI/bge-base-en)
            image_model: HuggingFace model for image embeddings (default: google/siglip-base-patch16-224)
            offline_mode: If True, only use cached models (no downloads)
        """
        # Store db_path - connection will be lazy (created when first needed)
        self._db_path = db_path
        self._client = None
        self._collection = None
        self.collection_name = collection_name
        self.offline_mode = offline_mode
        
        # Load text embedding model (BAAI/bge-base-en) - matches Person 1
        print(f"Loading text embedding model: {text_model}...")
        if offline_mode:
            print("  (Offline mode: using local cache only)")
            original_hf_offline = os.environ.get('HF_HUB_OFFLINE', None)
            os.environ['HF_HUB_OFFLINE'] = '1'
        else:
            print("  (Online mode: will download if not in cache)")
        
        try:
            self.text_embedding_model = SentenceTransformer(text_model)
            print("✓ Text embedding model loaded successfully!")
        except Exception as e:
            error_msg = str(e).lower()
            if offline_mode and ('not found' in error_msg or 'does not exist' in error_msg or 'offline' in error_msg):
                raise RuntimeError(
                    f"Text model '{text_model}' not found in local cache.\n"
                    f"Please download it first (while online) using:\n"
                    f"  python ingestion_pipeline/setup_offline.py\n"
                    f"Or manually:\n"
                    f"  python -c \"from sentence_transformers import SentenceTransformer; SentenceTransformer('{text_model}')\""
                ) from e
            else:
                raise
        finally:
            if offline_mode:
                if original_hf_offline is None:
                    os.environ.pop('HF_HUB_OFFLINE', None)
                else:
                    os.environ['HF_HUB_OFFLINE'] = original_hf_offline
        
        # Load image embedding model (SigLIP) - matches Person 1
        print(f"Loading image embedding model: {image_model}...")
        if offline_mode:
            original_hf_offline = os.environ.get('HF_HUB_OFFLINE', None)
            os.environ['HF_HUB_OFFLINE'] = '1'
        else:
            print("  (Online mode: will download if not in cache)")
        
        try:
            self.image_model = AutoModel.from_pretrained(image_model)
            self.image_processor = AutoProcessor.from_pretrained(image_model)
            self.image_model.eval()  # Set to evaluation mode
            print("✓ Image embedding model (SigLIP) loaded successfully!")
        except Exception as e:
            error_msg = str(e).lower()
            if offline_mode and ('not found' in error_msg or 'does not exist' in error_msg or 'offline' in error_msg):
                raise RuntimeError(
                    f"Image model '{image_model}' not found in local cache.\n"
                    f"Please download it first (while online) using:\n"
                    f"  python ingestion_pipeline/setup_offline.py\n"
                    f"Or manually:\n"
                    f"  python -c \"from transformers import AutoModel, AutoProcessor; AutoModel.from_pretrained('{image_model}'); AutoProcessor.from_pretrained('{image_model}')\""
                ) from e
            else:
                raise
        finally:
            if offline_mode:
                if original_hf_offline is None:
                    os.environ.pop('HF_HUB_OFFLINE', None)
                else:
                    os.environ['HF_HUB_OFFLINE'] = original_hf_offline
    
    @property
    def client(self):
        """Lazy initialization of ChromaDB client."""
        if self._client is None:
            # Initialize ChromaDB PersistentClient for local storage
            try:
                self._client = chromadb.PersistentClient(path=self._db_path)
            except Exception as e:
                raise RuntimeError(
                    f"Failed to connect to ChromaDB database at '{self._db_path}'. "
                    "Make sure the directory exists or check your connection settings."
                ) from e
        return self._client
    
    @property
    def collection(self):
        """Lazy initialization of ChromaDB collection."""
        if self._collection is None:
            try:
                # Get or create the collection (matches Person 1's collection name)
                self._collection = self.client.get_or_create_collection(
                    name=self.collection_name,
                    metadata={"hnsw:space": "cosine"}  # Use cosine similarity
                )
            except Exception as e:
                raise RuntimeError(
                    f"Failed to get or create collection '{self.collection_name}': {str(e)}"
                ) from e
        return self._collection
    
    def embed_query(self, query: Union[str, Image.Image], query_type: str = 'text') -> np.ndarray:
        """
        Encode a query (text or image) into an embedding vector.
        
        Uses the same models as Person 1:
        - Text: BAAI/bge-base-en (SentenceTransformer)
        - Image: google/siglip-base-patch16-224 (SigLIP)
        
        Args:
            query: Text string (for text queries) or image file path (string) or PIL Image object (for image queries)
            query_type: Type of query - 'text' or 'image'
        
        Returns:
            numpy array containing the embedding vector
        """
        if query_type == 'text':
            # For text queries, use BGE model (matches Person 1)
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
            # For image queries, use SigLIP model (matches Person 1)
            if isinstance(query, str):
                # If it's a file path, load it
                try:
                    image = Image.open(query).convert("RGB")
                except Exception as e:
                    raise ValueError(f"Failed to open image file '{query}': {str(e)}")
            elif isinstance(query, Image.Image):
                # If it's already a PIL Image, ensure RGB
                image = query.convert("RGB") if query.mode != "RGB" else query
            else:
                raise ValueError("Image query must be a file path (string) or PIL Image object")
            
            try:
                # Use SigLIP processor and model (matches Person 1's process exactly)
                inputs = self.image_processor(images=image, return_tensors="pt")
                with torch.no_grad():
                    image_embeds = self.image_model.get_image_features(**inputs)
                # Normalize the embedding (matches Person 1)
                image_embeds = image_embeds / image_embeds.norm(p=2, dim=-1, keepdim=True)
                embedding = image_embeds.squeeze().cpu().numpy()
            except Exception as e:
                raise RuntimeError(f"Failed to encode image: {str(e)}") from e
        
        else:
            raise ValueError(f"Invalid query_type: {query_type}. Must be 'text' or 'image'")
        
        return embedding
    
    def search(self, query_vector: np.ndarray, top_k: int = 10) -> Dict:
        """
        Search for the most relevant chunks in ChromaDB.
        
        Args:
            query_vector: Embedding vector of the query
            top_k: Number of top results to return
        
        Returns:
            Dictionary containing search results from ChromaDB
        """
        # Convert numpy array to list for ChromaDB
        query_vector_list = query_vector.tolist()
        
        # Perform search in ChromaDB
        # Cross-modal search works because:
        # - Text and images are both embedded into vectors
        # - ChromaDB uses cosine similarity to find matches
        # - A text query vector can find image vectors and vice-versa
        try:
            results = self.collection.query(
                query_embeddings=[query_vector_list],
                n_results=top_k,
                include=["documents", "metadatas", "distances"]
            )
            return results
        except Exception as e:
            raise RuntimeError(f"ChromaDB search failed: {str(e)}") from e
    
    def format_results(self, raw_results: Dict) -> List[Dict]:
        """
        Parse and format raw ChromaDB results into a clean list of dictionaries.
        
        Args:
            raw_results: Raw results from ChromaDB search
        
        Returns:
            Formatted list of dictionaries with clean structure
        
        Note: ChromaDB returns results in format:
        {
            'ids': [[id1, id2, ...]],
            'distances': [[0.1, 0.2, ...]],
            'documents': [['content1', 'content2', ...]],
            'metadatas': [[{'source_file': 'file1.pdf', 'type': 'text', ...}, ...]]
        }
        """
        formatted_results = []
        
        if not raw_results:
            return formatted_results
        
        # ChromaDB returns a dict with lists of lists (one inner list per query)
        # Since we query with one vector, we take the first element of each list
        ids = raw_results.get('ids', [[]])
        distances = raw_results.get('distances', [[]])
        documents = raw_results.get('documents', [[]])
        metadatas = raw_results.get('metadatas', [[]])
        
        # Extract the first query's results (since we only query with one vector)
        ids_list = ids[0] if ids and len(ids) > 0 else []
        distances_list = distances[0] if distances and len(distances) > 0 else []
        documents_list = documents[0] if documents and len(documents) > 0 else []
        metadatas_list = metadatas[0] if metadatas and len(metadatas) > 0 else []
        
        # Build formatted results
        num_results = len(ids_list)
        for i in range(num_results):
            # Extract metadata fields
            metadata = metadatas_list[i] if i < len(metadatas_list) else {}
            source = metadata.get('source_file', 'unknown') if isinstance(metadata, dict) else 'unknown'
            entity_type = metadata.get('type', 'unknown') if isinstance(metadata, dict) else 'unknown'
            
            # Get content from documents or metadata
            content = documents_list[i] if i < len(documents_list) else 'N/A'
            if content == 'N/A' and isinstance(metadata, dict):
                content = metadata.get('content', 'N/A')
            
            # Get full metadata (may contain additional fields)
            full_metadata = metadata if isinstance(metadata, dict) else {}
            
            formatted_result = {
                "id": ids_list[i] if i < len(ids_list) else None,
                "score": distances_list[i] if i < len(distances_list) else None,
                "source": source,
                "type": entity_type,
                "content": content,
                "metadata": full_metadata
            }
            formatted_results.append(formatted_result)
        
        return formatted_results
    
    def get_context(
        self, 
        query: Union[str, Image.Image], 
        query_type: str = 'text', 
        top_k: int = 10
    ) -> List[Dict]:
        """
        Main function to retrieve relevant context chunks for a query.
        
        This is the primary function that should be used by Person 3.
        
        Args:
            query: Text string or image (path or PIL Image)
            query_type: Type of query - 'text' or 'image' (default: 'text')
            top_k: Number of top results to return (default: 10)
        
        Returns:
            List of formatted context chunks with the structure:
            [
                {
                    "id": "report.pdf_chunk_1",
                    "score": 0.85,
                    "source": "report.pdf",
                    "type": "text",
                    "content": "...",
                    "metadata": {"page": 3}
                },
                {
                    "id": "screenshot.png_image",
                    "score": 0.82,
                    "source": "screenshot.png",
                    "type": "image",
                    "content": "N/A",
                    "metadata": {}
                }
            ]
        """
        # Step 1: Encode the query into embedding vector
        query_vector = self.embed_query(query, query_type=query_type)
        
        # Step 2: Search in ChromaDB
        raw_results = self.search(query_vector, top_k=top_k)
        
        # Step 3: Format the results
        formatted_results = self.format_results(raw_results)
        
        return formatted_results


# Convenience function for easy usage
def get_context(
    query: Union[str, Image.Image], 
    query_type: str = 'text', 
    top_k: int = 10,
    db_path: str = "chroma_local_db",
    collection_name: str = "multimodal_collection",
    offline_mode: bool = True
) -> List[Dict]:
    """
    Convenience function to retrieve context chunks.
    
    Creates a RetrievalSystem instance and retrieves relevant chunks.
    
    Args:
        query: Text string or image (path or PIL Image)
        query_type: Type of query - 'text' or 'image' (default: 'text')
        top_k: Number of top results to return (default: 10)
        db_path: Path to ChromaDB database directory (default: chroma_local_db)
        collection_name: Name of the collection in ChromaDB (default: multimodal_collection)
        offline_mode: If True, only use cached models (default: True)
    
    Returns:
        List of formatted context chunks
    """
    retriever = RetrievalSystem(
        db_path=db_path, 
        collection_name=collection_name,
        offline_mode=offline_mode
    )
    return retriever.get_context(query, query_type=query_type, top_k=top_k)


# Example usage (for testing)
if __name__ == "__main__":
    print("=" * 60)
    print("Person 2: Retrieval Module - Example Usage")
    print("=" * 60)
    print("Updated to match Person 1's setup:")
    print("  - Text model: BAAI/bge-base-en")
    print("  - Image model: google/siglip-base-patch16-224")
    print("  - DB path: chroma_local_db")
    print("  - Collection: multimodal_collection")
    print("=" * 60)
    
    try:
        # Initialize retriever
        print("\nInitializing RetrievalSystem...")
        retriever = RetrievalSystem()
        
        # Note: The database directory 'chroma_local_db' must exist (created by Person 1)
        # before you can perform actual searches.
        print("\n[OK] RetrievalSystem initialized successfully!")
        print("\nNote: To use this module, ensure:")
        print("  1. chroma_local_db directory exists (created by Person 1)")
        print("  2. Collection 'multimodal_collection' exists in the database")
        print("  3. Database contains indexed data")
        
        # Example 1: Text query (will only work if database exists)
        print("\n" + "=" * 60)
        print("Example 1: Text Query")
        print("=" * 60)
        text_query = "Show me the report that has a description about international development in 2024"
        print(f"\nQuery: {text_query}")
        
        try:
            results = retriever.get_context(text_query, query_type='text', top_k=5)
            print(f"[OK] Found {len(results)} results:")
            for i, result in enumerate(results, 1):
                score = result.get('score', 'N/A')
                score_str = f"{score:.4f}" if isinstance(score, (int, float)) else str(score)
                content_preview = result.get('content', 'N/A')
                if isinstance(content_preview, str) and len(content_preview) > 100:
                    content_preview = content_preview[:100] + "..."
                print(f"\n{i}. Score: {score_str}")
                print(f"   ID: {result.get('id', 'unknown')}")
                print(f"   Source: {result.get('source', 'unknown')}")
                print(f"   Type: {result.get('type', 'unknown')}")
                print(f"   Content preview: {content_preview}")
        except Exception as e:
            print(f"[WARNING] Error performing search: {e}")
            print("This is expected if the database directory doesn't exist yet or is empty.")
            print("Person 1 needs to create the database first.")
        
        # Example 2: Image query
        print("\n" + "=" * 60)
        print("Example 2: Image Query")
        print("=" * 60)
        print("To test image queries, uncomment and provide an image path:")
        print("# image_path = 'path/to/your/image.png'")
        print("# results = retriever.get_context(image_path, query_type='image', top_k=5)")
        
    except ImportError as e:
        print(f"[ERROR] Import Error: {e}")
        print("\nTo fix this:")
        print("  1. Make sure you're in a virtual environment")
        print("  2. Install: pip install -r requirements.txt")
    except Exception as e:
        print(f"[ERROR] Error: {e}")
        print("\nThis module requires the ChromaDB database to be set up by Person 1 first.")
        print("Make sure you've run the ingestion pipeline to populate the database.")
