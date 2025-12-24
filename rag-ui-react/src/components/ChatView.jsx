import { useState, useRef, useEffect } from 'react'
import { Send, Loader, AlertCircle } from 'lucide-react'
import Message from './Message'
import './ChatView.css'

function ChatView({ conversation, onUpdateConversation, sidebarOpen, apiStatus }) {
  const [inputValue, setInputValue] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const messagesEndRef = useRef(null)
  const textareaRef = useRef(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [conversation?.messages])

  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto'
      textareaRef.current.style.height = textareaRef.current.scrollHeight + 'px'
    }
  }, [inputValue])

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!inputValue.trim() || isLoading || !conversation) return
    if (apiStatus !== 'online') {
      alert('Backend API is not available. Please start the backend server.')
      return
    }

    const userMessage = {
      id: Date.now().toString(),
      role: 'user',
      content: inputValue.trim(),
      timestamp: new Date().toISOString()
    }

    // Update conversation with user message
    const updatedMessages = [...conversation.messages, userMessage]
    onUpdateConversation(conversation.id, {
      messages: updatedMessages,
      title: conversation.messages.length === 0 ? inputValue.slice(0, 50) : conversation.title
    })

    setInputValue('')
    setIsLoading(true)

    try {
      const response = await fetch('http://localhost:8000/api/query', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          query: userMessage.content,
          top_k: 10
        })
      })

      if (!response.ok) {
        throw new Error('Failed to get response from API')
      }

      const data = await response.json()

      const assistantMessage = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: data.answer,
        sources: data.sources,
        timestamp: new Date().toISOString()
      }

      onUpdateConversation(conversation.id, {
        messages: [...updatedMessages, assistantMessage]
      })
    } catch (error) {
      console.error('Error:', error)
      const errorMessage = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: `Sorry, I encountered an error: ${error.message}. Please make sure the backend API is running on http://localhost:8000`,
        timestamp: new Date().toISOString(),
        isError: true
      }
      onUpdateConversation(conversation.id, {
        messages: [...updatedMessages, errorMessage]
      })
    } finally {
      setIsLoading(false)
    }
  }

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSubmit(e)
    }
  }

  if (!conversation) {
    return (
      <div className="chat-view empty">
        <div className="empty-state">
          <h2>Welcome to RAG Chat</h2>
          <p>Start a new conversation to begin</p>
        </div>
      </div>
    )
  }

  return (
    <div className={`chat-view ${sidebarOpen ? 'sidebar-open' : 'sidebar-closed'}`}>
      <div className="chat-header">
        <h2>{conversation.title}</h2>
        {apiStatus !== 'online' && (
          <div className="api-warning">
            <AlertCircle size={16} />
            <span>Backend API offline</span>
          </div>
        )}
      </div>

      <div className="messages-container">
        {conversation.messages.length === 0 ? (
          <div className="welcome-message">
            <h1>How can I help you today?</h1>
            <p>Ask me anything about your documents</p>
          </div>
        ) : (
          conversation.messages.map(message => (
            <Message key={message.id} message={message} />
          ))
        )}
        {isLoading && (
          <div className="loading-message">
            <Loader className="spinner" size={20} />
            <span>Thinking...</span>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      <div className="input-container">
        <form onSubmit={handleSubmit} className="input-form">
          <textarea
            ref={textareaRef}
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Message RAG Chat..."
            className="message-input"
            rows="1"
            disabled={isLoading}
          />
          <button
            type="submit"
            className="send-button"
            disabled={isLoading || !inputValue.trim() || apiStatus !== 'online'}
          >
            <Send size={18} />
          </button>
        </form>
        <p className="input-hint">Press Enter to send, Shift+Enter for new line</p>
      </div>
    </div>
  )
}

export default ChatView

