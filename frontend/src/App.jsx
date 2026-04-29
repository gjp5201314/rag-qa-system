import { useState } from 'react'
import { AppProvider, useApp } from './store/index.jsx'
import HomePage from './pages/HomePage'
import ChatPage from './pages/ChatPage'
import AdminPage from './pages/AdminPage'
import KnowledgeBaseSelector from './components/KnowledgeBaseSelector'

function AppContent() {
  const [currentPage, setCurrentPage] = useState('home')
  const { currentKB } = useApp()

  const renderPage = () => {
    switch (currentPage) {
      case 'chat':
        return <ChatPage />
      case 'admin':
        return <AdminPage />
      default:
        return <HomePage />
    }
  }

  return (
    <div className="app">
      <aside className="sidebar">
        <div className="sidebar-header">
          <div className="logo">
            <div className="logo-icon">R</div>
            RAG 系统
          </div>
        </div>

        <div className="sidebar-content">
          <div className="sidebar-section">
            <div className="sidebar-section-title">导航</div>
            <ul className="kb-list">
              <li
                className={`kb-item ${currentPage === 'home' ? 'active' : ''}`}
                onClick={() => setCurrentPage('home')}
              >
                <div className="kb-icon">🏠</div>
                <div className="kb-info">
                  <div className="kb-name">首页</div>
                </div>
              </li>

              <li
                className={`kb-item ${currentPage === 'chat' ? 'active' : ''}`}
                onClick={() => setCurrentPage('chat')}
              >
                <div className="kb-icon">💬</div>
                <div className="kb-info">
                  <div className="kb-name">智能问答</div>
                </div>
              </li>

              <li
                className={`kb-item ${currentPage === 'admin' ? 'active' : ''}`}
                onClick={() => setCurrentPage('admin')}
              >
                <div className="kb-icon">⚙️</div>
                <div className="kb-info">
                  <div className="kb-name">知识库管理</div>
                </div>
              </li>
            </ul>
          </div>

          <KnowledgeBaseSelector />

          {currentKB && (
            <div style={{
              padding: 16,
              marginTop: 'auto',
              borderTop: '1px solid var(--border)'
            }}>
              <div style={{ fontSize: 12, color: 'var(--text-muted)', marginBottom: 8 }}>
                当前知识库
              </div>
              <div style={{ fontSize: 14, fontWeight: 500 }}>
                {currentKB.name}
              </div>
            </div>
          )}
        </div>
      </aside>

      <main className="main-content">
        {renderPage()}
      </main>
    </div>
  )
}

export default function App() {
  return (
    <AppProvider>
      <AppContent />
    </AppProvider>
  )
}
