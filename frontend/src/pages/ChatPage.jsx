import { useState, useEffect, useRef } from 'react'
import { chatAPI } from '../services/api'
import { useApp } from '../store/index.jsx'
import ChatMessage from '../components/ChatMessage'
import ChatInput from '../components/ChatInput'

export default function ChatPage() {
  const { currentKB, currentSession, selectSession } = useApp()
  const [messages, setMessages] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const messagesEndRef = useRef(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  useEffect(() => {
    if (currentSession) {
      loadHistory()
    } else {
      setMessages([])
    }
  }, [currentSession])

  const loadHistory = async () => {
    if (!currentSession) return

    try {
      const response = await chatAPI.getHistory(currentSession.id)
      if (response.data.messages) {
        const parsedMessages = response.data.messages.map(msg => ({
          ...msg,
          sources: typeof msg.sources === 'string' ? JSON.parse(msg.sources || '[]') : (msg.sources || [])
        }))
        setMessages(parsedMessages)
      }
    } catch (error) {
      console.error('Failed to load history:', error)
    }
  }

  const handleSendMessage = async (content) => {
    if (!content.trim()) return

    setLoading(true)
    setError(null)

    const tempUserMessage = {
      id: Date.now(),
      session_id: currentSession?.id || 0,
      role: 'user',
      content,
      sources: [],
      created_at: new Date().toISOString()
    }

    setMessages(prev => [...prev, tempUserMessage])

    try {
      const response = await chatAPI.sendMessage({
        message: content,
        session_id: currentSession?.id,
        knowledge_base_id: currentKB?.id
      })

      const { answer, sources, session_id } = response.data

      if (!currentSession && session_id) {
        selectSession({ id: session_id })
      }

      const assistantMessage = {
        id: Date.now() + 1,
        session_id: session_id || currentSession?.id,
        role: 'assistant',
        content: answer,
        sources,
        created_at: new Date().toISOString()
      }

      setMessages(prev => [...prev, assistantMessage])
    } catch (error) {
      setError('发送消息失败，请重试')
      setMessages(prev => prev.filter(m => m.id !== tempUserMessage.id))
    }

    setLoading(false)
  }

  if (!currentKB) {
    return (
      <div className="chat-container">
        <div className="empty-state">
          <div className="empty-state-icon">💬</div>
          <h2>欢迎使用 RAG 智能问答</h2>
          <p>请先在左侧选择一个知识库开始对话，或创建一个新的知识库并上传文档。</p>
        </div>
      </div>
    )
  }

  return (
    <div className="chat-container">
      <div className="chat-header">
        <h1>{currentKB.name}</h1>
        <p>{currentKB.description || '开始智能问答'}</p>
      </div>

      {error && (
        <div style={{
          padding: 12,
          background: 'rgba(239, 68, 68, 0.1)',
          border: '1px solid rgba(239, 68, 68, 0.3)',
          borderRadius: 8,
          marginBottom: 16,
          color: 'var(--error)',
          fontSize: 14
        }}>
          {error}
        </div>
      )}

      <div className="chat-messages">
        {messages.length === 0 ? (
          <div className="empty-state">
            <div className="empty-state-icon">🤖</div>
            <h2>开始提问吧</h2>
            <p>
              基于「{currentKB.name}」中的文档，我可以回答您的问题。
              {currentKB.completed_count === 0 && ' 当前知识库暂无已处理的文档。'}
            </p>
          </div>
        ) : (
          <>
            {messages.map((msg) => (
              <ChatMessage
                key={msg.id}
                message={msg}
                isLoading={loading && msg.id === messages[messages.length - 1]?.id && msg.role === 'assistant' && msg.content === ''}
              />
            ))}
          </>
        )}
        <div ref={messagesEndRef} />
      </div>

      <ChatInput onSendMessage={handleSendMessage} disabled={loading} />
    </div>
  )
}
