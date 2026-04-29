import { useState, useRef } from 'react'
import { documentAPI } from '../services/api'

export default function FileUpload({ kbId, onUploadComplete, onError }) {
  const [uploading, setUploading] = useState(false)
  const [dragover, setDragover] = useState(false)
  const fileInputRef = useRef(null)

  const handleFileChange = async (e) => {
    const files = e.target.files
    if (!files || files.length === 0) return

    await uploadFiles(Array.from(files))
  }

  const handleDrop = async (e) => {
    e.preventDefault()
    setDragover(false)

    const files = e.dataTransfer.files
    if (files.length === 0) return

    await uploadFiles(Array.from(files))
  }

  const uploadFiles = async (files) => {
    setUploading(true)

    for (const file of files) {
      const ext = file.name.split('.').pop().toLowerCase()
      if (!['pdf', 'txt', 'md', 'doc', 'docx'].includes(ext)) {
        onError?.(`不支持的文件格式: ${file.name}`)
        continue
      }

      try {
        const formData = new FormData()
        formData.append('file', file)
        formData.append('knowledge_base_id', kbId)

        const response = await documentAPI.upload(formData)

        if (response.data.error) {
          onError?.(response.data.error)
        } else {
          onUploadComplete?.(response.data)
        }
      } catch (error) {
        onError?.(`上传失败: ${file.name}`)
      }
    }

    setUploading(false)
    if (fileInputRef.current) {
      fileInputRef.current.value = ''
    }
  }

  const handleDragOver = (e) => {
    e.preventDefault()
    setDragover(true)
  }

  const handleDragLeave = (e) => {
    e.preventDefault()
    setDragover(false)
  }

  const formatFileSize = (bytes) => {
    if (bytes < 1024) return bytes + ' B'
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB'
    return (bytes / (1024 * 1024)).toFixed(1) + ' MB'
  }

  return (
    <div>
      <div
        className={`upload-area ${dragover ? 'dragover' : ''}`}
        onDrop={handleDrop}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onClick={() => fileInputRef.current?.click()}
      >
        <input
          ref={fileInputRef}
          type="file"
          multiple
          accept=".pdf,.txt,.md,.doc,.docx"
          onChange={handleFileChange}
          style={{ display: 'none' }}
        />

        {uploading ? (
          <>
            <div style={{ fontSize: 32, marginBottom: 16 }}>
              <span className="loading-spinner" style={{ width: 40, height: 40, borderWidth: 3 }}></span>
            </div>
            <p style={{ fontSize: 16, fontWeight: 500 }}>正在上传处理...</p>
          </>
        ) : (
          <>
            <div style={{ fontSize: 48, marginBottom: 16 }}>📄</div>
            <p style={{ fontSize: 16, fontWeight: 500, marginBottom: 8 }}>
              点击或拖拽文件到此区域上传
            </p>
            <p style={{ fontSize: 13, color: 'var(--text-secondary)' }}>
              支持 PDF、TXT、Markdown、DOC、DOCX 格式
            </p>
          </>
        )}
      </div>

      <div style={{ marginTop: 16, padding: 16, background: 'var(--bg-tertiary)', borderRadius: 12 }}>
        <p style={{ fontSize: 13, color: 'var(--text-secondary)', lineHeight: 1.6 }}>
          <strong style={{ color: 'var(--text-primary)' }}>上传说明：</strong><br/>
          1. 文件上传后需要点击「处理」按钮进行向量化<br/>
          2. 处理时间取决于文件大小，一般 10-30 秒<br/>
          3. 支持批量上传多个文件
        </p>
      </div>
    </div>
  )
}
