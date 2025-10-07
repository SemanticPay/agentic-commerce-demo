import React from 'react'
import { ChatMessage } from '../types'
import { UIResourceRenderer, isUIResource } from '@mcp-ui/client'

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
      <div key={index}>
      {isUIResource(uiObject) &&
        <div>
          <UIResourceRenderer 
              resource={uiObject.resource} 
          />   
        </div>
      }
      </div>
    ))}
    </div>
  )
}

export default Message
