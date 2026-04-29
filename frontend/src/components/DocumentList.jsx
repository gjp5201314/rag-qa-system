import { useState } from 'react'
import { documentAPI } from '../services/api'

export default function DocumentList({ documents, onDocumentChange }) {
  const [processing, setProcessing] = useState(null)

  const handleProcess = async (docId) => {
    setProcessing(docId)
    try {
      await documentAPI.process(docId)
      onDocumentChange?.()
    } catch (error) {
      console.error('Process failed:', error)
    }
    setProcessing(null)
  }

  const handleDelete = async (docId) => {
    if (!confirm('确定要删除这个文档吗？')) return

    try {
      await documentAPI.delete(docId)
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

            <div style={{ display: 'flex', gap: 8 }}>
              {doc.status === 'pending' && (
                <button
                  className="btn btn-primary btn-sm"
                  onClick={() => handleProcess(doc.id)}
                  disabled={processing === doc.id}
                >
                  {processing === doc.id ? (
                    <>
                      <span className="loading-spinner" style={{ width: 12, height: 12 }}></span>
                      处理中
                    </>
                  ) : (
                    '处理'
                  )}
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
    </div>
  )
}
