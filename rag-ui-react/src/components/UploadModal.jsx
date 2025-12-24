import { useState } from 'react'
import { X, Upload, File, CheckCircle, XCircle, Loader } from 'lucide-react'
import './UploadModal.css'

function UploadModal({ onClose, onUploadComplete }) {
  const [dragActive, setDragActive] = useState(false)
  const [files, setFiles] = useState([])
  const [uploading, setUploading] = useState(false)

  const handleDrag = (e) => {
    e.preventDefault()
    e.stopPropagation()
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true)
    } else if (e.type === "dragleave") {
      setDragActive(false)
    }
  }

  const handleDrop = (e) => {
    e.preventDefault()
    e.stopPropagation()
    setDragActive(false)
    
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      handleFiles(Array.from(e.dataTransfer.files))
    }
  }

  const handleFileInput = (e) => {
    if (e.target.files && e.target.files.length > 0) {
      handleFiles(Array.from(e.target.files))
    }
  }

  const handleFiles = (newFiles) => {
    const fileObjects = newFiles.map(file => ({
      file,
      name: file.name,
      size: formatFileSize(file.size),
      status: 'pending'
    }))
    setFiles(prev => [...prev, ...fileObjects])
  }

  const formatFileSize = (bytes) => {
    if (bytes === 0) return '0 Bytes'
    const k = 1024
    const sizes = ['Bytes', 'KB', 'MB', 'GB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i]
  }

  const uploadFiles = async () => {
    setUploading(true)
    
    for (let i = 0; i < files.length; i++) {
      if (files[i].status !== 'pending') continue
      
      setFiles(prev => prev.map((f, idx) => 
        idx === i ? { ...f, status: 'uploading' } : f
      ))

      try {
        const formData = new FormData()
        formData.append('file', files[i].file)

        const response = await fetch('http://localhost:8000/api/ingestion/upload', {
          method: 'POST',
          body: formData
        })

        if (!response.ok) {
          throw new Error('Upload failed')
        }

        const result = await response.json()
        
        setFiles(prev => prev.map((f, idx) => 
          idx === i ? { 
            ...f, 
            status: 'success',
            chunksProcessed: result.chunks_processed 
          } : f
        ))
      } catch (error) {
        setFiles(prev => prev.map((f, idx) => 
          idx === i ? { ...f, status: 'error', error: error.message } : f
        ))
      }
    }

    setUploading(false)
  }

  const removeFile = (index) => {
    setFiles(prev => prev.filter((_, idx) => idx !== index))
  }

  const allUploaded = files.length > 0 && files.every(f => f.status === 'success')

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content" onClick={e => e.stopPropagation()}>
        <div className="modal-header">
          <h2>Upload Documents</h2>
          <button className="close-btn" onClick={onClose}>
            <X size={20} />
          </button>
        </div>

        <div 
          className={`upload-area ${dragActive ? 'drag-active' : ''}`}
          onDragEnter={handleDrag}
          onDragLeave={handleDrag}
          onDragOver={handleDrag}
          onDrop={handleDrop}
        >
          <Upload size={48} className="upload-icon" />
          <p className="upload-text">Drag & drop files here</p>
          <p className="upload-subtext">or</p>
          <label className="file-input-label">
            <input
              type="file"
              multiple
              onChange={handleFileInput}
              accept=".pdf,.docx,.jpg,.jpeg,.png,.gif,.bmp,.webp,.mp3,.wav,.m4a,.flac"
              style={{ display: 'none' }}
            />
            <span>Browse Files</span>
          </label>
          <p className="supported-formats">
            Supported: PDF, DOCX, Images (JPG, PNG, GIF, BMP, WEBP), Audio (MP3, WAV, M4A, FLAC)
          </p>
        </div>

        {files.length > 0 && (
          <div className="files-list">
            {files.map((file, idx) => (
              <div key={idx} className="file-item">
                <File size={20} className="file-icon" />
                <div className="file-info">
                  <div className="file-name">{file.name}</div>
                  <div className="file-meta">
                    {file.size}
                    {file.chunksProcessed && ` • ${file.chunksProcessed} chunks processed`}
                  </div>
                </div>
                <div className="file-status">
                  {file.status === 'pending' && (
                    <button onClick={() => removeFile(idx)} className="remove-btn">
                      <X size={16} />
                    </button>
                  )}
                  {file.status === 'uploading' && <Loader size={16} className="spinner" />}
                  {file.status === 'success' && <CheckCircle size={16} className="success-icon" />}
                  {file.status === 'error' && <XCircle size={16} className="error-icon" />}
                </div>
              </div>
            ))}
          </div>
        )}

        <div className="modal-footer">
          {allUploaded ? (
            <button className="btn btn-primary" onClick={onUploadComplete}>
              Done
            </button>
          ) : (
            <>
              <button className="btn btn-secondary" onClick={onClose}>
                Cancel
              </button>
              <button 
                className="btn btn-primary" 
                onClick={uploadFiles}
                disabled={files.length === 0 || uploading}
              >
                {uploading ? 'Uploading...' : `Upload ${files.length} file${files.length !== 1 ? 's' : ''}`}
              </button>
            </>
          )}
        </div>
      </div>
    </div>
  )
}

export default UploadModal

