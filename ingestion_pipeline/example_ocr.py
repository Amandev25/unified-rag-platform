"""
Example script demonstrating OCR text extraction from images.

This script shows how to:
1. Initialize the ingestion pipeline with OCR enabled
2. Process images with text using OCR
3. Query the extracted text
"""
import os
from pathlib import Path
from ingest import IngestionPipeline

def main():
    # Initialize pipeline with OCR enabled
    print("Initializing ingestion pipeline with OCR...")
    pipeline = IngestionPipeline(
        db_path="chroma_local_db",
        text_model="BAAI/bge-base-en",
        image_model="google/siglip-base-patch16-224",
        offline_mode=False,  # Set to True if models are already cached
        use_ocr=True,  # Enable OCR for text extraction from images
        ocr_languages=['en']  # Languages for OCR (can add more: ['en', 'es', 'fr'])
    )
    
    print("\n" + "="*60)
    print("OCR-enabled ingestion pipeline ready!")
    print("="*60)
    
    # Example: Process a single image file
    image_path = "C:\\Users\\omvis\\Desktop\\test.png"  # Replace with actual image path
    
    if Path(image_path).exists():
        print(f"\nProcessing image: {image_path}")
        ids, embeddings, documents, metadatas = pipeline.process_file(image_path)
        
        if ids:
            print(f"\n✓ Successfully extracted text from image!")
            print(f"  - Chunks extracted: {len(ids)}")
            print(f"\nExtracted text preview:")
            for i, (doc, meta) in enumerate(zip(documents, metadatas)):
                print(f"\n  Chunk {i+1}:")
                print(f"    Type: {meta['type']}")
                print(f"    Text: {doc[:100]}...")  # First 100 chars
            
            # Insert into database
            pipeline.batch_insert(ids, embeddings, documents, metadatas)
            print(f"\n✓ Data inserted into ChromaDB")
            print(f"  Total items in collection: {pipeline.collection.count()}")
        else:
            print("✗ No text extracted from image")
    else:
        print(f"\n⚠ Image file not found: {image_path}")
        print("\nTo use this example:")
        print("1. Replace 'path/to/your/image.png' with an actual image path")
        print("2. Make sure the image contains readable text")
        print("3. Run: python ingestion_pipeline/example_ocr.py")
    
    # Example: Query extracted text
    if pipeline.collection.count() > 0:
        print("\n" + "="*60)
        print("Example: Searching for OCR-extracted text")
        print("="*60)
        
        query = "what is the abstract about?"  # Replace with actual query
        query_embedding = pipeline.text_embedding_model.encode(query).tolist()
        
        results = pipeline.collection.query(
            query_embeddings=[query_embedding],
            n_results=5,
            where={"type": "image_ocr"}  # Filter for OCR-processed images only
        )
        
        print(f"\nSearch query: '{query}'")
        print(f"Results found: {len(results['ids'][0])}")
        
        for i, (doc_id, doc, distance) in enumerate(zip(
            results['ids'][0], 
            results['documents'][0], 
            results['distances'][0]
        )):
            print(f"\n{i+1}. ID: {doc_id}")
            print(f"   Distance: {distance:.4f}")
            print(f"   Text: {doc[:100]}...")


if __name__ == "__main__":
    main()

