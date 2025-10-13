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

    {/* {message.widgets && message.widgets.map((widget, index) => (
      // <div key={index} dangerouslySetInnerHTML={{ __html: widget }} />
      <div>Hello!</div>
    ))} */}

      {message.widgets?.map((widget, index) => {
        console.log('Widget:', widget)
        return (
          // <div key={index} dangerouslySetInnerHTML={{ __html: widget }} />
          <div key={index}>Hello</div>
        )
      })}
    </div>
  )
}

export default Message
