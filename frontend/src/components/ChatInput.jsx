import { useState, useRef } from 'react'

export default function ChatInput({ onSendMessage, disabled }) {
  const [message, setMessage] = useState('')
  const textareaRef = useRef(null)

  const handleSubmit = (e) => {
    e.preventDefault()
    if (message.trim() && !disabled) {
      onSendMessage(message.trim())
      setMessage('')
      if (textareaRef.current) {
        textareaRef.current.style.height = 'auto'
      }
    }
  }

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSubmit(e)
    }
  }

  const handleInput = (e) => {
    setMessage(e.target.value)
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto'
      textareaRef.current.style.height = Math.min(textareaRef.current.scrollHeight, 120) + 'px'
    }
  }

  return (
    <form onSubmit={handleSubmit} className="chat-input-container">
      <div className="chat-input-wrapper">
        <textarea
          ref={textareaRef}
          className="chat-input"
          value={message}
          onChange={handleInput}
          onKeyDown={handleKeyDown}
          placeholder="输入您的问题，按 Enter 发送..."
          disabled={disabled}
          rows={1}
        />
        <button
          type="submit"
          className="send-button"
          disabled={disabled || !message.trim()}
        >
          {disabled ? (
            <>
              <span className="loading-spinner"></span>
              发送中
            </>
          ) : (
            <>
              发送
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M22 2L11 13M22 2L15 22L11 13M22 2L2 9L11 13"/>
              </svg>
            </>
          )}
        </button>
      </div>
    </form>
  )
}
