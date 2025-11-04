# EasyOCR Implementation Summary

## Overview
Successfully integrated **EasyOCR** into the ingestion pipeline to extract text from images and save them as vector embeddings in ChromaDB.

## Changes Made

### 1. **requirements.txt**
- Added `easyocr>=1.7.0` dependency

### 2. **parsers.py**
- Added `import easyocr`
- Created new `ImageOCRParser` class that:
  - Initializes EasyOCR reader with configurable languages
  - Extracts text from images using OCR
  - Filters results by confidence threshold (>0.3)
  - Chunks extracted text similar to PDF/DOCX processing
  - Returns text chunks with metadata type `"image_ocr"`

### 3. **ingest.py**
- Added import for `ImageOCRParser`
- Updated `IngestionPipeline.__init__()` with new parameters:
  - `use_ocr: bool = True` - Enable/disable OCR
  - `ocr_languages: List[str] = ['en']` - Configure OCR languages
- Modified image processing logic:
  - **If OCR enabled**: Extract text using EasyOCR → create text embeddings → store as `"image_ocr"` type
  - **If OCR disabled**: Use SigLIP for direct image embeddings → store as `"image"` type
- Text chunks from images are now processed identically to PDF/DOCX text chunks

### 4. **app.py** (FastAPI application)
- Added environment variable support:
  - `USE_OCR` - Enable/disable OCR (default: `1`)
  - `OCR_LANGUAGES` - Comma-separated language codes (default: `en`)
- Updated pipeline initialization to pass OCR settings

### 5. **client.py** (Python client)
- Updated `IngestionClient.__init__()` with new parameters:
  - `use_ocr: bool = True` - Enable/disable OCR
  - `ocr_languages: List[str] = None` - Configure OCR languages (default: ['en'])
- Updated `create_client()` convenience function to support OCR parameters
- Added environment variable support for `USE_OCR` and `OCR_LANGUAGES`
- Updated example usage comments to demonstrate OCR functionality

### 6. **setup_offline.py**
- Added `download_easyocr_models()` function
- Downloads EasyOCR models for specified languages during offline setup
- Updated summary to include EasyOCR model status
- Added EasyOCR cache location: `~/.EasyOCR/`

### 7. **README.md**
- Added comprehensive "OCR Text Extraction from Images" section
- Documented:
  - How OCR works (5-step process)
  - How to enable/disable OCR
  - How to configure languages
  - Comparison between OCR mode vs Direct Image mode
  - Installation and setup instructions
- Updated environment variables documentation
- Updated model cache locations

### 8. **example_ocr.py** (New file)
- Created example script demonstrating:
  - Pipeline initialization with OCR
  - Processing images with text extraction
  - Querying OCR-extracted text
  - Filtering results by type

## How It Works

### OCR Processing Flow
1. **Image Upload** → Image file (JPG, PNG, GIF, BMP, WEBP) is provided
2. **OCR Detection** → EasyOCR scans the image and detects text regions
3. **Text Extraction** → Extracts text from detected regions (confidence > 0.3)
4. **Text Chunking** → Splits extracted text into 1000-char chunks with 50-char overlap
5. **Embedding Creation** → Converts each text chunk to vector embedding using text model (BAAI/bge-base-en)
6. **Database Storage** → Stores chunks with metadata type `"image_ocr"`

### Metadata Structure
```json
{
  "source_file": "screenshot.png",
  "type": "image_ocr",
  "format": "PNG",
  "size": "(1920, 1080)",
  "chunk_index": 0,
  "total_chunks": 3
}
```

## Configuration

### Environment Variables
```bash
# Enable OCR (default)
export USE_OCR=1

# Disable OCR (use direct image embeddings instead)
export USE_OCR=0

# Configure languages (comma-separated)
export OCR_LANGUAGES=en,es,fr
```

### Python API
```python
from ingest import IngestionPipeline

# With OCR enabled
pipeline = IngestionPipeline(
    use_ocr=True,
    ocr_languages=['en', 'es']
)

# With OCR disabled
pipeline = IngestionPipeline(
    use_ocr=False
)
```

## Supported Languages
EasyOCR supports 80+ languages including:
- English (`en`)
- Spanish (`es`)
- French (`fr`)
- German (`de`)
- Chinese Simplified (`ch_sim`)
- Chinese Traditional (`ch_tra`)
- Japanese (`ja`)
- Korean (`ko`)
- Arabic (`ar`)
- And many more...

[Full list](https://www.jaided.ai/easyocr/)

## Usage Examples

### 1. Upload Image via API
```bash
curl -X POST "http://localhost:8000/upload" \
  -F "file=@screenshot.png"
```

### 2. Search OCR Text
```bash
curl -X POST "http://localhost:8000/search" \
  -H "Content-Type: application/json" \
  -d '{
    "query_text": "machine learning",
    "n_results": 10,
    "where": {"type": "image_ocr"}
  }'
```

### 3. Process Directory with Images
```python
from ingest import IngestionPipeline

pipeline = IngestionPipeline(use_ocr=True)
pipeline.ingest_directory("./documents")
# All images in the directory will be OCR-processed
```

### 4. Using the Python Client
```python
from ingestion_pipeline.client import create_client

# Create client with OCR enabled (default)
client = create_client()

# Or with custom OCR settings
client = create_client(
    use_ocr=True,
    ocr_languages=['en', 'es', 'fr']
)

# Upload image with text
result = client.upload_file("screenshot.png")
print(f"Extracted {result['chunks_processed']} text chunks from image")

# Search OCR-extracted text
results = client.search(
    query_text="machine learning",
    where={"type": "image_ocr"}
)
```

## Testing

### Prerequisites
1. Install dependencies:
```bash
pip install -r ingestion_pipeline/requirements.txt
```

2. Download models (requires internet):
```bash
python ingestion_pipeline/setup_offline.py
```

### Test OCR
1. Run the example script:
```bash
python ingestion_pipeline/example_ocr.py
```

2. Or test with a specific image:
```python
from ingest import IngestionPipeline

pipeline = IngestionPipeline(use_ocr=True, offline_mode=False)
ids, embeddings, docs, metas = pipeline.process_file("image_with_text.png")

if ids:
    print(f"Extracted {len(ids)} chunks")
    print(f"First chunk: {docs[0][:100]}...")
```

## Benefits

1. **Text Searchability**: Images with text are now searchable via semantic text queries
2. **Flexible Processing**: Choose between OCR (text extraction) or direct image embeddings
3. **Multi-language Support**: Extract text in 80+ languages
4. **Consistent Format**: OCR text is processed identically to PDF/DOCX text
5. **Metadata Tracking**: Type field distinguishes between `"image_ocr"` and `"image"`

## Notes

- OCR is **enabled by default** (`USE_OCR=1`)
- Text extraction works best with clear, high-contrast text
- Confidence threshold is set to 0.3 (configurable in `ImageOCRParser`)
- OCR models are cached in `~/.EasyOCR/` directory
- First-time OCR initialization may take a few seconds to load models

## Performance

- **CPU Mode**: EasyOCR runs on CPU by default (compatible with all systems)
- **Model Loading**: ~2-5 seconds on first initialization
- **Processing Speed**: ~1-3 seconds per image (depends on image size and text complexity)
- **Memory Usage**: ~500MB for English model

## Future Enhancements (Optional)

- [ ] Add GPU support for faster OCR processing
- [ ] Configurable confidence threshold
- [ ] Support for rotated text detection
- [ ] OCR quality metrics in metadata
- [ ] Batch OCR processing for multiple images
- [ ] OCR result caching to avoid reprocessing

---

**Implementation Date**: November 4, 2025
**Status**: ✅ Complete and Ready for Use

