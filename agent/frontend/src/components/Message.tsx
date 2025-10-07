import React from 'react'
import { ChatMessage } from '../types'

interface MessageProps {
  message: ChatMessage
}

const Message: React.FC<MessageProps> = ({ message }) => {
  const messageClass = message.role === 'user' ? 'user-message' : 'agent-message'
  
  return (
    <div className={`message ${messageClass}`}>
      <div className="message-content">
        {message.content}
      </div>

    {message.ui_objects && message.ui_objects.map((uiObject, index) => (
      <div key={index} dangerouslySetInnerHTML={{ __html: uiObject }} />
    ))}
    </div>
  )
}

export default Message
