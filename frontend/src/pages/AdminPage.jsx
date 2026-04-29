import { useState, useEffect } from 'react'
import { useApp } from '../store/index.jsx'
import { documentAPI } from '../services/api'
import FileUpload from '../components/FileUpload'
import DocumentList from '../components/DocumentList'

export default function AdminPage() {
  const { currentKB, selectKB } = useApp()
  const [activeTab, setActiveTab] = useState('documents')
  const [documents, setDocuments] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [toast, setToast] = useState(null)

  useEffect(() => {
    if (currentKB) {
      loadDocuments()
    }
  }, [currentKB])

  const loadDocuments = async () => {
    if (!currentKB) return

    setLoading(true)
    try {
      const response = await documentAPI.getAll(currentKB.id)
      setDocuments(response.data.documents || [])
    } catch (error) {
      setError('加载文档失败')
    }
    setLoading(false)
  }

  const showToast = (message, type = 'success') => {
    setToast({ message, type })
    setTimeout(() => setToast(null), 3000)
  }

  const handleUploadComplete = (data) => {
    showToast(`文档 "${data.filename}" 上传成功`)
    loadDocuments()
  }

  const handleUploadError = (errorMsg) => {
    showToast(errorMsg, 'error')
  }

  if (!currentKB) {
    return (
      <div className="chat-container">
        <div className="empty-state">
          <div className="empty-state-icon">⚙️</div>
          <h2>知识库管理</h2>
          <p>请先在左侧选择一个知识库进行管理。</p>
        </div>
      </div>
    )
  }

  return (
    <div className="chat-container">
      <div className="chat-header">
        <h1>管理：{currentKB.name}</h1>
        <p>{currentKB.description || '知识库管理面板'}</p>
      </div>

      <div className="admin-tabs">
        <button
          className={`tab-button ${activeTab === 'documents' ? 'active' : ''}`}
          onClick={() => setActiveTab('documents')}
        >
          📄 文档管理
        </button>
        <button
          className={`tab-button ${activeTab === 'upload' ? 'active' : ''}`}
          onClick={() => setActiveTab('upload')}
        >
          ⬆️ 上传文档
        </button>
        <button
          className={`tab-button ${activeTab === 'settings' ? 'active' : ''}`}
          onClick={() => setActiveTab('settings')}
        >
          ⚙️ 设置
        </button>
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

      {activeTab === 'documents' && (
        <div>
          <div className="card">
            <div className="card-header">
              <h3 className="card-title">文档列表</h3>
              <button className="btn btn-primary btn-sm" onClick={loadDocuments}>
                🔄 刷新
              </button>
            </div>
          </div>

          {loading ? (
            <div style={{ textAlign: 'center', padding: 48 }}>
              <span className="loading-spinner" style={{ width: 32, height: 32 }}></span>
              <p style={{ marginTop: 16, color: 'var(--text-secondary)' }}>加载中...</p>
            </div>
          ) : (
            <DocumentList
              documents={documents}
              onDocumentChange={loadDocuments}
            />
          )}
        </div>
      )}

      {activeTab === 'upload' && (
        <div>
          <div className="card">
            <div className="card-header">
              <h3 className="card-title">上传新文档</h3>
            </div>
            <FileUpload
              kbId={currentKB.id}
              onUploadComplete={handleUploadComplete}
              onError={handleUploadError}
            />
          </div>
        </div>
      )}

      {activeTab === 'settings' && (
        <div>
          <div className="card">
            <div className="card-header">
              <h3 className="card-title">知识库设置</h3>
            </div>

            <div style={{ marginBottom: 24 }}>
              <label className="form-label">知识库名称</label>
              <input
                type="text"
                className="form-input"
                value={currentKB.name}
                disabled
              />
            </div>

            <div style={{ marginBottom: 24 }}>
              <label className="form-label">描述</label>
              <textarea
                className="form-input form-textarea"
                value={currentKB.description || ''}
                disabled
              />
            </div>

            <div style={{
              padding: 16,
              background: 'var(--bg-tertiary)',
              borderRadius: 8,
              fontSize: 13,
              color: 'var(--text-secondary)'
            }}>
              <p><strong>统计信息：</strong></p>
              <ul style={{ marginTop: 8, paddingLeft: 20 }}>
                <li>文档总数：{currentKB.document_count || 0}</li>
                <li>已处理：{currentKB.completed_count || 0}</li>
                <li>创建时间：{new Date(currentKB.created_at).toLocaleString('zh-CN')}</li>
              </ul>
            </div>
          </div>

          <div className="card" style={{ borderColor: 'rgba(239, 68, 68, 0.3)' }}>
            <div className="card-header">
              <h3 className="card-title" style={{ color: 'var(--error)' }}>危险区域</h3>
            </div>
            <p style={{ fontSize: 14, color: 'var(--text-secondary)', marginBottom: 16 }}>
              删除知识库将同时删除所有关联的文档和对话记录，此操作不可恢复。
            </p>
            <button
              className="btn btn-danger"
              onClick={() => {
                if (confirm('确定要删除这个知识库吗？所有数据将被永久删除！')) {
                  // Handle delete
                }
              }}
            >
              删除知识库
            </button>
          </div>
        </div>
      )}

      {toast && (
        <div className={`toast ${toast.type}`}>
          {toast.message}
        </div>
      )}
    </div>
  )
}
