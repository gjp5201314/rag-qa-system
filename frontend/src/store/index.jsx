import { createContext, useContext, useState, useCallback } from 'react'

const AppContext = createContext()

export function AppProvider({ children }) {
  const [currentKB, setCurrentKB] = useState(null)
  const [currentSession, setCurrentSession] = useState(null)
  const [sessions, setSessions] = useState([])
  const [knowledgeBases, setKnowledgeBases] = useState([])

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
      removeKnowledgeBase
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
