import { User, Bot, FileText } from 'lucide-react'
import './Message.css'

function Message({ message }) {
  const isUser = message.role === 'user'

  return (
    <div className={`message ${isUser ? 'user-message' : 'assistant-message'} ${message.isError ? 'error-message' : ''}`}>
      <div className="message-avatar">
        {isUser ? <User size={20} /> : <Bot size={20} />}
      </div>
      <div className="message-content">
        <div className="message-text">
          {message.content}
        </div>
        {message.sources && message.sources.length > 0 && (
          <div className="message-sources">
            <div className="sources-header">
              <FileText size={14} />
              <span>Sources ({message.sources.length})</span>
            </div>
            <div className="sources-list">
              {message.sources.slice(0, 5).map((source, idx) => (
                <div key={idx} className="source-item">
                  <span className="source-number">{idx + 1}</span>
                  <div className="source-info">
                    <span className="source-name">{source.source}</span>
                    {source.type && (
                      <span className="source-type">{source.type}</span>
                    )}
                  </div>
                </div>
              ))}
              {message.sources.length > 5 && (
                <div className="source-item more">
                  <span>+ {message.sources.length - 5} more sources</span>
                </div>
              )}
            </div>
          </div>
        )}
        <div className="message-timestamp">
          {new Date(message.timestamp).toLocaleTimeString([], { 
            hour: '2-digit', 
            minute: '2-digit' 
          })}
        </div>
      </div>
    </div>
  )
}

export default Message

