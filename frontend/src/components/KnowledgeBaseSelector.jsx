import { useState, useEffect } from 'react'
import { knowledgeBaseAPI, chatAPI } from '../services/api'
import { useApp } from '../store/index.jsx'

export default function KnowledgeBaseSelector() {
  const { currentKB, selectKB, knowledgeBases, addKnowledgeBase, removeKnowledgeBase, updateKnowledgeBases } = useApp()
  const [showModal, setShowModal] = useState(false)
  const [newKBName, setNewKBName] = useState('')
  const [newKBDesc, setNewKBDesc] = useState('')
  const [loading, setLoading] = useState(false)

  const loadKnowledgeBases = async () => {
    try {
      const response = await knowledgeBaseAPI.getAll()
      if (response.data.knowledge_bases) {
        const KBs = response.data.knowledge_bases
        updateKnowledgeBases(KBs)
      }
    } catch (error) {
      console.error('Failed to load knowledge bases:', error)
    }
  }

  useEffect(() => {
    loadKnowledgeBases()
  }, [])

  const handleCreateKB = async (e) => {
    e.preventDefault()
    if (!newKBName.trim()) return

    setLoading(true)
    try {
      const response = await knowledgeBaseAPI.create({
        name: newKBName.trim(),
        description: newKBDesc.trim()
      })
      // 重新加载知识库列表
      await loadKnowledgeBases()
      setShowModal(false)
      setNewKBName('')
      setNewKBDesc('')
    } catch (error) {
      console.error('Create KB failed:', error)
      alert('创建失败：' + (error.response?.data?.error || error.message))
    }
    setLoading(false)
  }

  const handleDeleteKB = async (kbId, e) => {
    e.stopPropagation()
    if (!confirm('确定要删除这个知识库吗？')) return

    try {
      await knowledgeBaseAPI.delete(kbId)
      // 重新加载知识库列表
      await loadKnowledgeBases()
    } catch (error) {
      console.error('Delete KB failed:', error)
      alert('删除失败：' + (error.response?.data?.error || error.message))
    }
  }

  return (
    <>
      <div className="sidebar-section">
        <div className="sidebar-section-title">
          知识库
          <button
            onClick={() => setShowModal(true)}
            style={{
              float: 'right',
              background: 'none',
              border: 'none',
              color: 'var(--accent)',
              cursor: 'pointer',
              fontSize: 16,
              padding: 0
            }}
          >
            +
          </button>
        </div>
        <ul className="kb-list">
          {knowledgeBases.map((kb) => (
            <li
              key={kb.id}
              className={`kb-item ${currentKB?.id === kb.id ? 'active' : ''}`}
              onClick={() => selectKB(kb)}
            >
              <div className="kb-icon">📚</div>
              <div className="kb-info">
                <div className="kb-name">{kb.name}</div>
                <div className="kb-stats">
                  {kb.document_count || 0} 文档 · {kb.completed_count || 0} 已处理
                </div>
              </div>
              <button
                onClick={(e) => handleDeleteKB(kb.id, e)}
                style={{
                  background: 'none',
                  border: 'none',
                  color: 'var(--text-muted)',
                  cursor: 'pointer',
                  padding: 4,
                  opacity: 0.6
                }}
                onMouseEnter={(e) => e.target.style.opacity = 1}
                onMouseLeave={(e) => e.target.style.opacity = 0.6}
              >
                ✕
              </button>
            </li>
          ))}
          {knowledgeBases.length === 0 && (
            <li style={{ padding: '16px 12px', color: 'var(--text-muted)', fontSize: 13 }}>
              暂无知识库，点击 + 创建
            </li>
          )}
        </ul>
      </div>

      {showModal && (
        <div className="modal-overlay" onClick={() => setShowModal(false)}>
          <div className="modal" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h3 className="modal-title">创建知识库</h3>
              <button className="modal-close" onClick={() => setShowModal(false)}>✕</button>
            </div>

            <form onSubmit={handleCreateKB}>
              <div className="form-group">
                <label className="form-label">知识库名称 *</label>
                <input
                  type="text"
                  className="form-input"
                  value={newKBName}
                  onChange={(e) => setNewKBName(e.target.value)}
                  placeholder="例如：技术文档、产品手册"
                  required
                />
              </div>

              <div className="form-group">
                <label className="form-label">描述（可选）</label>
                <textarea
                  className="form-input form-textarea"
                  value={newKBDesc}
                  onChange={(e) => setNewKBDesc(e.target.value)}
                  placeholder="简要描述这个知识库的用途..."
                />
              </div>

              <div style={{ display: 'flex', gap: 12, marginTop: 24 }}>
                <button
                  type="button"
                  className="btn btn-secondary"
                  onClick={() => setShowModal(false)}
                  style={{ flex: 1 }}
                >
                  取消
                </button>
                <button
                  type="submit"
                  className="btn btn-primary"
                  disabled={loading || !newKBName.trim()}
                  style={{ flex: 1 }}
                >
                  {loading ? (
                    <>
                      <span className="loading-spinner" style={{ width: 14, height: 14 }}></span>
                      创建中...
                    </>
                  ) : (
                    '创建'
                  )}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </>
  )
}
