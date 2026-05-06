import { useState, useRef, useEffect } from 'react'

export default function ChatMessage({ message, isLoading = false }) {
  const [showSources, setShowSources] = useState(false)

  const formatTime = (dateStr) => {
    const date = new Date(dateStr)
    return date.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })
  }

  const sources = message.sources || (typeof message.sources_json === 'string' ? JSON.parse(message.sources_json || '[]') : [])

  const getFileName = (path) => {
    if (!path) return '未知来源'
    const parts = path.split(/[/\\]/)
    const fileName = parts[parts.length - 1]
    const decoded = decodeURIComponent(fileName)
    return decoded
  }

  const isUser = message.role === 'user'

  return (
    <div className={`message ${isUser ? 'message-user' : 'message-assistant'}`}>
      <div className={`message-avatar ${message.role}`}>
        {isUser ? '👤' : '🤖'}
      </div>
      <div className="message-content">
        <div className="message-role">
          {isUser ? '你' : 'RAG 助手'}
          <span style={{ marginLeft: 8, fontSize: 12, color: 'var(--text-muted)' }}>
            {formatTime(message.created_at)}
          </span>
        </div>
        <div className="message-text">
          {isLoading ? (
            <span style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
              <span className="loading-spinner"></span>
              正在思考中...
            </span>
          ) : (
            message.content.split('\n').map((line, i) => (
              <p key={i} style={{ marginBottom: line ? 12 : 0 }}>{line}</p>
            ))
          )}
        </div>

        {!isUser && sources.length > 0 && (
          <div style={{ marginTop: 16 }}>
            <button
              onClick={() => setShowSources(!showSources)}
              style={{
                background: 'var(--bg-tertiary)',
                border: '1px solid var(--border)',
                borderRadius: 8,
                padding: '8px 16px',
                color: 'var(--text-secondary)',
                fontSize: 13,
                cursor: 'pointer',
                display: 'flex',
                alignItems: 'center',
                gap: 8
              }}
            >
              📚 查看参考来源 ({sources.length})
              <span style={{ transform: showSources ? 'rotate(90deg)' : 'rotate(0)', transition: 'transform 0.2s' }}>▶</span>
            </button>

            {showSources && (
              <div className="message-sources" style={{ marginTop: 12 }}>
                <div className="sources-title">检索到的相关片段</div>
                {sources.map((source, idx) => (
                  <div key={idx} className="source-item">
                    <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 8 }}>
                      <span style={{ fontWeight: 500 }}>{getFileName(source.source)}</span>
                      <span className="source-score">{(source.score * 100).toFixed(1)}%</span>
                    </div>
                    <p style={{ color: 'var(--text-secondary)', fontSize: 13 }}>{source.content}...</p>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  )
}
