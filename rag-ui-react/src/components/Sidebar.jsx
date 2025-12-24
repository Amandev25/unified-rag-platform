import { useState } from 'react'
import { Menu, X, Plus, Trash2, Upload, Database, CheckCircle, XCircle, Loader } from 'lucide-react'
import UploadModal from './UploadModal'
import './Sidebar.css'

function Sidebar({ 
  isOpen, 
  onToggle, 
  conversations, 
  currentConversationId, 
  onSelectConversation, 
  onNewConversation, 
  onDeleteConversation,
  apiStatus,
  documentCount,
  onRefreshDocumentCount
}) {
  const [showUploadModal, setShowUploadModal] = useState(false)

  const getStatusIcon = () => {
    switch (apiStatus) {
      case 'online':
        return <CheckCircle size={16} className="status-icon status-online" />
      case 'offline':
        return <XCircle size={16} className="status-icon status-offline" />
      default:
        return <Loader size={16} className="status-icon status-checking" />
    }
  }

  const formatDate = (dateString) => {
    const date = new Date(dateString)
    const now = new Date()
    const diffInHours = (now - date) / (1000 * 60 * 60)
    
    if (diffInHours < 24) {
      return 'Today'
    } else if (diffInHours < 48) {
      return 'Yesterday'
    } else if (diffInHours < 168) {
      return `${Math.floor(diffInHours / 24)} days ago`
    } else {
      return date.toLocaleDateString()
    }
  }

  return (
    <>
      <div className={`sidebar ${isOpen ? 'open' : 'closed'}`}>
        <div className="sidebar-header">
          <button className="sidebar-toggle" onClick={onToggle}>
            {isOpen ? <X size={20} /> : <Menu size={20} />}
          </button>
          {isOpen && <h1 className="sidebar-title">RAG Chat</h1>}
        </div>

        {isOpen && (
          <>
            <button className="new-chat-btn" onClick={onNewConversation}>
              <Plus size={18} />
              <span>New Chat</span>
            </button>

            <div className="conversations-list">
              {conversations.map(conv => (
                <div
                  key={conv.id}
                  className={`conversation-item ${conv.id === currentConversationId ? 'active' : ''}`}
                  onClick={() => onSelectConversation(conv.id)}
                >
                  <div className="conversation-info">
                    <span className="conversation-title">{conv.title}</span>
                    <span className="conversation-date">{formatDate(conv.createdAt)}</span>
                  </div>
                  <button
                    className="delete-btn"
                    onClick={(e) => {
                      e.stopPropagation()
                      onDeleteConversation(conv.id)
                    }}
                  >
                    <Trash2 size={14} />
                  </button>
                </div>
              ))}
            </div>

            <div className="sidebar-footer">
              <button className="upload-btn" onClick={() => setShowUploadModal(true)}>
                <Upload size={18} />
                <span>Upload Documents</span>
              </button>

              <div className="status-section">
                <div className="status-item">
                  {getStatusIcon()}
                  <span>API: {apiStatus}</span>
                </div>
                <div className="status-item">
                  <Database size={16} />
                  <span>{documentCount} documents</span>
                </div>
              </div>
            </div>
          </>
        )}
      </div>

      {showUploadModal && (
        <UploadModal
          onClose={() => setShowUploadModal(false)}
          onUploadComplete={() => {
            setShowUploadModal(false)
            onRefreshDocumentCount()
          }}
        />
      )}
    </>
  )
}

export default Sidebar

