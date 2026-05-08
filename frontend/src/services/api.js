import axios from 'axios'

// 生产环境 API 配置 - 2026-05-08 最终修复版本
// 直接硬编码正确的 API URL 以避免 CDN 缓存问题
const API_BASE_URL = 'https://rag-api-t46i.onrender.com/api'

console.log('API Base URL:', API_BASE_URL)

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 60000,
  headers: {
    'Content-Type': 'application/json'
  }
})

apiClient.interceptors.response.use(
  response => response,
  error => {
    console.error('API Error:', error.response?.data || error.message)
    return Promise.reject(error)
  }
)

export const chatAPI = {
  sendMessage: (data) => apiClient.post('/chat', data),
  getSessions: (kbId) => apiClient.get('/chat/sessions', { params: { knowledge_base_id: kbId } }),
  getSession: (sessionId) => apiClient.get(`/chat/sessions/${sessionId}`),
  createSession: (data) => apiClient.post('/chat/sessions', data),
  deleteSession: (sessionId) => apiClient.delete(`/chat/sessions/${sessionId}`),
  getHistory: (sessionId) => apiClient.get(`/chat/history/${sessionId}`)
}

export const documentAPI = {
  upload: (formData) => apiClient.post('/documents/upload', formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  }),
  process: (docId) => apiClient.post(`/documents/${docId}/process`),
  getStatus: (docId) => apiClient.get(`/documents/${docId}/status`),
  getAll: (kbId) => apiClient.get('/documents', { params: { knowledge_base_id: kbId } }),
  getOne: (docId) => apiClient.get(`/documents/${docId}`),
  delete: (docId) => apiClient.delete(`/documents/${docId}`)
}

export const knowledgeBaseAPI = {
  create: (data) => apiClient.post('/knowledge-bases', data),
  getAll: () => apiClient.get('/knowledge-bases'),
  getOne: (kbId) => apiClient.get(`/knowledge-bases/${kbId}`),
  delete: (kbId) => apiClient.delete(`/knowledge-bases/${kbId}`)
}

export default apiClient
