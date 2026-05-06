import { useState, useEffect, useRef } from 'react'
import { chatAPI } from '../services/api'
import { useApp } from '../store/index.jsx'
import ChatMessage from '../components/ChatMessage'
import ChatInput from '../components/ChatInput'

export default function ChatPage() {
  const { currentKB, currentSession, selectSession, addSession, setChatMessages, getChatMessages, updateSessions } = useApp()
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [showSidebar, setShowSidebar] = useState(false)
  const [sessions, setSessions] = useState([])
  const messagesEndRef = useRef(null)
  const [messages, setMessages] = useState([])
  const [sessionInitialized, setSessionInitialized] = useState(false)
  const sidebarRef = useRef(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  useEffect(() => {
    if (currentSession) {
      const savedMessages = getChatMessages(currentSession.id)
      if (savedMessages.length > 0) {
        setMessages(savedMessages)
        setSessionInitialized(true)
      } else {
        loadHistory()
      }
    } else {
      setMessages([])
      setSessionInitialized(false)
    }
  }, [currentSession?.id])

  useEffect(() => {
    if (messages.length > 0 && currentSession) {
      setChatMessages(currentSession.id, messages)
    }
  }, [messages, currentSession, setChatMessages])

  useEffect(() => {
    if (currentKB) {
      loadSessions()
    }
  }, [currentKB?.id])

  useEffect(() => {
    const handleClickOutside = (e) => {
      if (sidebarRef.current && !sidebarRef.current.contains(e.target) &&
          !e.target.closest('.sidebar-trigger')) {
        setShowSidebar(false)
      }
    }
    document.addEventListener('mousedown', handleClickOutside)
    return () => document.removeEventListener('mousedown', handleClickOutside)
  }, [])

  const loadSessions = async () => {
    if (!currentKB) return
    try {
      const response = await chatAPI.getSessions(currentKB.id)
      if (response.data.sessions) {
        setSessions(response.data.sessions)
      }
    } catch (error) {
      console.error('Failed to load sessions:', error)
    }
  }

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
        setChatMessages(currentSession.id, parsedMessages)
        setSessionInitialized(true)
      }
    } catch (error) {
      console.error('Failed to load history:', error)
    }
  }

  const handleNewChat = async () => {
    if (!currentKB) return
    try {
      const response = await chatAPI.createSession({
        knowledge_base_id: currentKB.id
      })
      if (response.data.session_id) {
        const newSession = {
          id: response.data.session_id,
          title: '新对话',
          created_at: new Date().toISOString()
        }
        selectSession(newSession)
        addSession(newSession)
        setShowSidebar(false)
        loadSessions()
      }
    } catch (error) {
      console.error('Failed to create session:', error)
    }
  }

  const handleSelectSession = (session) => {
    selectSession(session)
    setShowSidebar(false)
  }

  const handleDeleteSession = async (e, sessionId) => {
    e.stopPropagation()
    try {
      await chatAPI.deleteSession(sessionId)
      setSessions(prev => prev.filter(s => s.id !== sessionId))
      if (currentSession?.id === sessionId) {
        selectSession(null)
      }
    } catch (error) {
      console.error('Failed to delete session:', error)
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
        const newSession = {
          id: session_id,
          title: content.slice(0, 50) + (content.length > 50 ? '...' : ''),
          created_at: new Date().toISOString()
        }
        selectSession(newSession)
        addSession(newSession)
        setSessionInitialized(true)
        loadSessions()
      } else if (currentSession && !sessionInitialized) {
        const updatedSession = {
          ...currentSession,
          title: content.slice(0, 50) + (content.length > 50 ? '...' : '')
        }
        updateSessions(sessions => sessions.map(s =>
          s.id === currentSession.id ? updatedSession : s
        ))
        setSessionInitialized(true)
        loadSessions()
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

  const formatDate = (dateStr) => {
    const date = new Date(dateStr)
    const now = new Date()
    const diff = now - date
    const days = Math.floor(diff / (1000 * 60 * 60 * 24))
    if (days === 0) return date.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })
    if (days === 1) return '昨天'
    if (days < 7) return `${days}天前`
    return date.toLocaleDateString('zh-CN', { month: 'short', day: 'numeric' })
  }

  if (!currentKB) {
    return (
      <div className="doubao-container">
        <div className="doubao-empty">
          <div className="doubao-logo">🤖</div>
          <h1>欢迎使用 RAG 智能问答</h1>
          <p>请先在左侧选择一个知识库开始对话</p>
        </div>
      </div>
    )
  }

  return (
    <div className="doubao-container">
      {showSidebar && (
        <div className="doubao-sidebar" ref={sidebarRef}>
          <div className="sidebar-header">
            <span className="sidebar-title">历史记录</span>
            <button className="sidebar-close" onClick={() => setShowSidebar(false)}>
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M18 6L6 18M6 6l12 12" />
              </svg>
            </button>
          </div>
          <div className="sidebar-content">
            {sessions.length === 0 ? (
              <div className="sidebar-empty">
                <span>暂无历史记录</span>
              </div>
            ) : (
              sessions.map(session => (
                <div
                  key={session.id}
                  className={`sidebar-item ${currentSession?.id === session.id ? 'active' : ''}`}
                  onClick={() => handleSelectSession(session)}
                >
                  <div className="sidebar-item-icon">
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                      <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" />
                    </svg>
                  </div>
                  <div className="sidebar-item-content">
                    <div className="sidebar-item-title">
                      {session.title && session.title !== '新对话' ? session.title : '新对话'}
                    </div>
                    <div className="sidebar-item-time">{formatDate(session.created_at)}</div>
                  </div>
                  <button
                    className="sidebar-item-delete"
                    onClick={(e) => handleDeleteSession(e, session.id)}
                  >
                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                      <path d="M3 6h18M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2" />
                    </svg>
                  </button>
                </div>
              ))
            )}
          </div>
        </div>
      )}

      <div className="doubao-main">
        <header className="doubao-header">
          <div className="header-kb">
            <span className="kb-badge">📚</span>
            <span className="kb-name">{currentKB.name}</span>
          </div>
          <div className="header-actions">
            <button className="btn-new-chat" onClick={handleNewChat}>
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M12 5v14M5 12h14" />
              </svg>
              新建问答
            </button>
            <button
              className={`btn-history sidebar-trigger ${showSidebar ? 'active' : ''}`}
              onClick={() => setShowSidebar(!showSidebar)}
            >
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </button>
          </div>
        </header>

        {error && <div className="doubao-error">{error}</div>}

        <div className="doubao-messages">
          {!currentSession ? (
            <div className="doubao-welcome">
              <div className="welcome-icon">💬</div>
              <h2>开始智能问答</h2>
              <p>基于「{currentKB.name}」中的文档进行问答</p>
              {currentKB.completed_count === 0 && (
                <p className="welcome-warning">⚠️ 当前知识库暂无已处理的文档</p>
              )}
              <div className="welcome-suggestions">
                <span>RAG 是什么？</span>
                <span>Embedding 是什么？</span>
                <span>有哪些应用场景？</span>
              </div>
            </div>
          ) : messages.length === 0 ? (
            <div className="doubao-welcome">
              <div className="welcome-icon">🤖</div>
              <h2>{currentSession.title && currentSession.title !== '新对话' ? currentSession.title : '新对话'}</h2>
              <p>开始提问吧</p>
              {currentKB.completed_count === 0 && (
                <p className="welcome-warning">⚠️ 当前知识库暂无已处理的文档</p>
              )}
              <div className="welcome-suggestions">
                <span>RAG 是什么？</span>
                <span>Embedding 是什么？</span>
                <span>有哪些应用场景？</span>
              </div>
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

        <div className="doubao-input">
          <ChatInput onSendMessage={handleSendMessage} disabled={loading} />
        </div>
      </div>
    </div>
  )
}