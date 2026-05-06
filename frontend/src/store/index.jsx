import { createContext, useContext, useState, useCallback, useEffect } from 'react'

const AppContext = createContext()

const STORAGE_KEY = 'rag_app_state'

function loadFromStorage() {
  try {
    const saved = localStorage.getItem(STORAGE_KEY)
    if (saved) {
      return JSON.parse(saved)
    }
  } catch (e) {
    console.error('Failed to load from storage:', e)
  }
  return null
}

function saveToStorage(data) {
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(data))
  } catch (e) {
    console.error('Failed to save to storage:', e)
  }
}

export function AppProvider({ children }) {
  const savedState = loadFromStorage()
  const [currentKB, setCurrentKB] = useState(savedState?.currentKB || null)
  const [currentSession, setCurrentSession] = useState(savedState?.currentSession || null)
  const [sessions, setSessions] = useState(savedState?.sessions || [])
  const [knowledgeBases, setKnowledgeBases] = useState(savedState?.knowledgeBases || [])
  const [chatMessagesMap, setChatMessagesMap] = useState(savedState?.chatMessagesMap || {})

  useEffect(() => {
    saveToStorage({
      currentKB,
      currentSession,
      sessions,
      knowledgeBases,
      chatMessagesMap
    })
  }, [currentKB, currentSession, sessions, knowledgeBases, chatMessagesMap])

  const selectKB = useCallback((kb) => {
    setCurrentKB(kb)
    setCurrentSession(null)
  }, [])

  const selectSession = useCallback((session) => {
    setCurrentSession(session)
  }, [])

  const addSession = useCallback((session) => {
    setSessions(prev => [session, ...prev.filter(s => s.id !== session.id)])
  }, [])

  const updateSessions = useCallback((newSessions) => {
    setSessions(newSessions)
  }, [])

  const addKnowledgeBase = useCallback((kb) => {
    setKnowledgeBases(prev => [kb, ...prev.filter(k => k.id !== kb.id)])
  }, [])

  const updateKnowledgeBases = useCallback((newKBs) => {
    setKnowledgeBases(newKBs)
  }, [])

  const removeKnowledgeBase = useCallback((kbId) => {
    setKnowledgeBases(prev => prev.filter(k => k.id !== kbId))
    if (currentKB?.id === kbId) {
      setCurrentKB(null)
    }
  }, [currentKB])

  const setChatMessages = useCallback((sessionId, messages) => {
    setChatMessagesMap(prev => ({
      ...prev,
      [sessionId]: messages
    }))
  }, [])

  const addChatMessage = useCallback((sessionId, message) => {
    setChatMessagesMap(prev => ({
      ...prev,
      [sessionId]: [...(prev[sessionId] || []), message]
    }))
  }, [])

  const getChatMessages = useCallback((sessionId) => {
    return chatMessagesMap[sessionId] || []
  }, [chatMessagesMap])

  return (
    <AppContext.Provider value={{
      currentKB,
      selectKB,
      currentSession,
      selectSession,
      sessions,
      addSession,
      updateSessions,
      knowledgeBases,
      addKnowledgeBase,
      updateKnowledgeBases,
      removeKnowledgeBase,
      chatMessagesMap,
      setChatMessages,
      addChatMessage,
      getChatMessages
    }}>
      {children}
    </AppContext.Provider>
  )
}

export function useApp() {
  const context = useContext(AppContext)
  if (!context) {
    throw new Error('useApp must be used within AppProvider')
  }
  return context
}
