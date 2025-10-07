import React from 'react'
import { ChatMessage } from '../types'

interface MessageProps {
  message: ChatMessage
}

const Message: React.FC<MessageProps> = ({ message }) => {
  const messageClass = message.role === 'user' ? 'user-message' : 'agent-message'
  
  return (
    <div className={`message ${messageClass}`}>
      {message.content}
    </div>
  )
}

export default Message