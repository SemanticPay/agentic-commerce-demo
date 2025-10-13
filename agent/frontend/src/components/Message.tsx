import React from 'react'
import { ChatMessage } from '../types'
import WidgetRenderer from './WidgetRenderer'

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

      {message.widgets && message.widgets.length > 0 && (
        <div className="message-widgets">
          {message.widgets.map((widget, index) => (
            <WidgetRenderer key={index} widget={widget} />
          ))}
        </div>
      )}
    </div>
  )
}

export default Message
