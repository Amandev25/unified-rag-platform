import { useState, useEffect } from 'react'
import Sidebar from './components/Sidebar'
import ChatView from './components/ChatView'
import './App.css'

function App() {
  const [conversations, setConversations] = useState([])
  const [currentConversationId, setCurrentConversationId] = useState(null)
  const [sidebarOpen, setSidebarOpen] = useState(true)
  const [apiStatus, setApiStatus] = useState('checking')
  const [documentCount, setDocumentCount] = useState(0)

  // Check API health on mount
  useEffect(() => {
    checkApiHealth()
    fetchDocumentCount()
  }, [])

  const checkApiHealth = async () => {
    try {
      const response = await fetch('http://localhost:8000/health')
      if (response.ok) {
        setApiStatus('online')
      } else {
        setApiStatus('offline')
      }
    } catch (error) {
      setApiStatus('offline')
    }
  }

  const fetchDocumentCount = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/ingestion/collection/count')
      if (response.ok) {
        const data = await response.json()
        setDocumentCount(data.count || 0)
      }
    } catch (error) {
      console.error('Failed to fetch document count:', error)
    }
  }

  const createNewConversation = () => {
    const newConv = {
      id: Date.now().toString(),
      title: 'New Chat',
      messages: [],
      createdAt: new Date().toISOString()
    }
    setConversations([newConv, ...conversations])
    setCurrentConversationId(newConv.id)
  }

  const deleteConversation = (id) => {
    setConversations(conversations.filter(conv => conv.id !== id))
    if (currentConversationId === id) {
      setCurrentConversationId(null)
    }
  }

  const updateConversation = (id, updates) => {
    setConversations(conversations.map(conv => 
      conv.id === id ? { ...conv, ...updates } : conv
    ))
  }

  const getCurrentConversation = () => {
    return conversations.find(conv => conv.id === currentConversationId)
  }

  // Create first conversation if none exist
  useEffect(() => {
    if (conversations.length === 0) {
      createNewConversation()
    }
  }, [])

  return (
    <div className="app">
      <Sidebar
        isOpen={sidebarOpen}
        onToggle={() => setSidebarOpen(!sidebarOpen)}
        conversations={conversations}
        currentConversationId={currentConversationId}
        onSelectConversation={setCurrentConversationId}
        onNewConversation={createNewConversation}
        onDeleteConversation={deleteConversation}
        apiStatus={apiStatus}
        documentCount={documentCount}
        onRefreshDocumentCount={fetchDocumentCount}
      />
      <ChatView
        conversation={getCurrentConversation()}
        onUpdateConversation={updateConversation}
        sidebarOpen={sidebarOpen}
        apiStatus={apiStatus}
      />
    </div>
  )
}

export default App

