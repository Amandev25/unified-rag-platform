# RAG Knowledge Base UI

A clean, responsive web interface for the RAG Knowledge Base API.

## Features

- **Landing Page**: Choose between uploading documents or asking questions
- **File Upload**: Drag & drop or click to upload documents, images, and audio files
- **Chat Interface**: Ask questions and get intelligent answers from your knowledge base
- **Responsive Design**: Works seamlessly on desktop, tablet, and mobile devices

## Setup

1. Make sure the API server is running on `http://localhost:8000`
2. Open `index.html` in a web browser, or serve it using a local web server

### Using Python's HTTP Server

```bash
cd ui
python -m http.server 3000
```

Then open `http://localhost:3000` in your browser.

### Using Node.js http-server

```bash
cd ui
npx http-server -p 3000
```

## Configuration

To change the API URL, edit the `API_BASE_URL` constant in `app.js`:

```javascript
const API_BASE_URL = 'http://localhost:8000';
```

## Supported File Types

- **Documents**: PDF, DOCX
- **Images**: JPG, PNG, GIF, BMP, WEBP
- **Audio**: MP3, WAV, M4A, FLAC

## Usage

1. **Upload Documents**: Click "Upload File" and select or drag & drop files to build your knowledge base
2. **Ask Questions**: Click "Start Chat" and type your questions to get answers from your knowledge base

## Browser Compatibility

- Chrome/Edge (latest)
- Firefox (latest)
- Safari (latest)

