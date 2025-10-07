import React from 'react'
import { ChatMessage } from '../types'
import Message from './Message'
import LoadingIndicator from './LoadingIndicator'

interface ChatMessagesProps {
  messages: ChatMessage[]
  isLoading: boolean
  messagesEndRef: React.RefObject<HTMLDivElement | null>
}

const ChatMessages: React.FC<ChatMessagesProps> = ({ messages, isLoading, messagesEndRef }) => {
  return (
    <div className="chat-messages">
      {messages.map((message, index) => (
        <Message 
          key={index} 
          message={message} 
        />
      ))}
      {isLoading && <LoadingIndicator />}
      <div ref={messagesEndRef} />
    </div>
  )
}

export default ChatMessages