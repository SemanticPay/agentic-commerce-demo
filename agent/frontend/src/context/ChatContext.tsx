import { createContext, useContext, useState, ReactNode } from "react"

export interface ChatMessage {
  id: string
  role: "user" | "agent"
  text: string
}

interface ChatContextType {
  messages: ChatMessage[]
  addMessage: (msg: ChatMessage) => void
  clear: () => void
}

const ChatContext = createContext<ChatContextType | undefined>(undefined)

export function ChatProvider({ children }: { children: ReactNode }) {
  const [messages, setMessages] = useState<ChatMessage[]>([])

  const addMessage = (msg: ChatMessage) =>
    setMessages(prev => [...prev, msg])

  const clear = () => setMessages([])

  return (
    <ChatContext.Provider value={{ messages, addMessage, clear }}>
      {children}
    </ChatContext.Provider>
  )
}

export function useChat() {
  const ctx = useContext(ChatContext)
  if (!ctx) throw new Error("useChat must be used within ChatProvider")
  return ctx
}