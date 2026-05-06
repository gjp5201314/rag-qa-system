import { useState, useEffect } from 'react'
import { documentAPI } from '../services/api'

export default function DocumentList({ documents, onDocumentChange }) {
  const [processing, setProcessing] = useState(null)
  const [processingProgress, setProcessingProgress] = useState({})

  useEffect(() => {
    const saved = localStorage.getItem('processing_docs')
    if (saved) {
      try {
        const savedProgress = JSON.parse(saved)
        Object.keys(savedProgress).forEach(docId => {
          if (savedProgress[docId].status === 'processing') {
            savedProgress[docId].status = 'pending'
            savedProgress[docId].progress = 0
          }
        })
        setProcessingProgress(savedProgress)
      } catch (e) {
        localStorage.removeItem('processing_docs')
      }
    }
  }, [])

  const saveProgress = (docId, data) => {
    const newProgress = { ...processingProgress, [docId]: data }
    setProcessingProgress(newProgress)
    localStorage.setItem('processing_docs', JSON.stringify(newProgress))
  }

  const clearProgress = (docId) => {
    const newProgress = { ...processingProgress }
    delete newProgress[docId]
    setProcessingProgress(newProgress)
    localStorage.setItem('processing_docs', JSON.stringify(newProgress))
  }

  const handleProcess = async (docId) => {
    setProcessing(docId)
    saveProgress(docId, { status: 'processing', progress: 0 })

    let progress = 0
    const progressInterval = setInterval(() => {
      progress = Math.min(progress + Math.random() * 12, 90)
      saveProgress(docId, { status: 'processing', progress: Math.round(progress) })
    }, 800)

    try {
      await documentAPI.process(docId)
      saveProgress(docId, { status: 'completed', progress: 100 })
      setTimeout(() => {
        clearProgress(docId)
        onDocumentChange?.()
      }, 500)
    } catch (error) {
      console.error('Process failed:', error)
      saveProgress(docId, { status: 'failed', progress: 0 })
      onDocumentChange?.()
    } finally {
      clearInterval(progressInterval)
      setProcessing(null)
    }
  }

  const handleDelete = async (docId) => {
    if (!confirm('确定要删除这个文档吗？')) return

    try {
      await documentAPI.delete(docId)
      clearProgress(docId)
      onDocumentChange?.()
    } catch (error) {
      console.error('Delete failed:', error)
    }
  }

  const formatFileSize = (bytes) => {
    if (!bytes) return '-'
    if (bytes < 1024) return bytes + ' B'
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB'
    return (bytes / (1024 * 1024)).toFixed(1) + ' MB'
  }

  const formatDate = (dateStr) => {
    if (!dateStr) return '-'
    const date = new Date(dateStr)
    return date.toLocaleDateString('zh-CN')
  }

  const getStatusBadge = (status) => {
    const statusMap = {
      pending: { text: '待处理', class: 'status-pending' },
      processing: { text: '处理中', class: 'status-processing' },
      completed: { text: '已完成', class: 'status-completed' },
      failed: { text: '失败', class: 'status-failed' }
    }
    const s = statusMap[status] || statusMap.pending
    return <span className={`status-badge ${s.class}`}>{s.text}</span>
  }

  const getFileIcon = (fileType) => {
    const icons = {
      pdf: '📕',
      txt: '📝',
      md: '📋',
      doc: '📘',
      docx: '📘'
    }
    return icons[fileType] || '📄'
  }

  const ProgressBar = ({ progress, status, docId }) => {
    const isActive = processing === docId
    const savedData = processingProgress[docId]
    const displayProgress = isActive ? progress : (savedData?.progress || 0)

    const getProgressColor = () => {
      if (status === 'failed') return 'var(--error)'
      if (status === 'completed') return 'var(--success)'
      if (isActive) return 'var(--primary)'
      return 'var(--warning)'
    }

    const getStatusText = () => {
      if (status === 'failed') return '失败'
      if (status === 'completed') return '完成'
      if (isActive) return `${displayProgress}%`
      return '等待中'
    }

    return (
      <div className="progress-container">
        <div className="progress-bar">
          <div
            className="progress-fill"
            style={{
              width: `${status === 'completed' ? 100 : displayProgress}%`,
              backgroundColor: getProgressColor()
            }}
          />
          <div className="progress-shimmer" />
        </div>
        <div className="progress-text" style={{ color: getProgressColor() }}>
          {getStatusText()}
        </div>
      </div>
    )
  }

  if (!documents || documents.length === 0) {
    return (
      <div className="card">
        <div style={{ textAlign: 'center', padding: 32, color: 'var(--text-secondary)' }}>
          <p style={{ fontSize: 48, marginBottom: 16 }}>📭</p>
          <p>暂无文档</p>
          <p style={{ fontSize: 13, marginTop: 8 }}>请上传文档开始构建知识库</p>
        </div>
      </div>
    )
  }

  return (
    <div className="card">
      <ul className="document-list">
        {documents.map((doc) => (
          <li key={doc.id} className="document-item">
            <div className="document-icon" style={{ fontSize: 20 }}>
              {getFileIcon(doc.file_type)}
            </div>

            <div className="document-info">
              <div className="document-name">{doc.filename}</div>
              <div className="document-meta">
                {formatFileSize(doc.file_size)} · {formatDate(doc.created_at)}
                {doc.chunk_count > 0 && ` · ${doc.chunk_count} 个片段`}
              </div>
            </div>

            {getStatusBadge(doc.status)}

            <div style={{ display: 'flex', gap: 8, alignItems: 'center' }}>
              {(doc.status === 'pending' || doc.status === 'processing' || doc.status === 'failed') && (
                <ProgressBar
                  progress={processing === doc.id ? 0 : processingProgress[doc.id]?.progress || 0}
                  status={doc.status}
                  docId={doc.id}
                />
              )}

              {doc.status === 'pending' && (
                <button
                  className="btn btn-primary btn-sm"
                  onClick={() => handleProcess(doc.id)}
                  disabled={processing === doc.id}
                >
                  {processing === doc.id ? '处理中...' : '处理'}
                </button>
              )}

              {doc.status === 'completed' && (
                <button
                  className="btn btn-secondary btn-sm"
                  onClick={() => handleProcess(doc.id)}
                  disabled={processing === doc.id}
                >
                  重新处理
                </button>
              )}

              {doc.status === 'failed' && (
                <button
                  className="btn btn-warning btn-sm"
                  onClick={() => handleProcess(doc.id)}
                  disabled={processing === doc.id}
                >
                  {processing === doc.id ? '重试中...' : '🔄 重试'}
                </button>
              )}

              <button
                className="btn btn-danger btn-sm"
                onClick={() => handleDelete(doc.id)}
              >
                删除
              </button>
            </div>
          </li>
        ))}
      </ul>

      <style>{`
        .progress-container {
          width: 120px;
        }

        .progress-bar {
          height: 6px;
          background: var(--bg-tertiary);
          border-radius: 3px;
          overflow: hidden;
          position: relative;
        }

        .progress-fill {
          height: 100%;
          border-radius: 3px;
          transition: width 0.4s ease, background-color 0.3s ease;
          position: relative;
        }

        .progress-shimmer {
          position: absolute;
          top: 0;
          left: 0;
          right: 0;
          bottom: 0;
          background: linear-gradient(
            90deg,
            transparent 0%,
            rgba(255,255,255,0.3) 50%,
            transparent 100%
          );
          animation: shimmer 1.5s infinite;
        }

        @keyframes shimmer {
          0% { transform: translateX(-100%); }
          100% { transform: translateX(100%); }
        }

        .progress-text {
          font-size: 11px;
          margin-top: 4px;
          text-align: center;
          font-weight: 500;
        }
      `}</style>
    </div>
  )
}