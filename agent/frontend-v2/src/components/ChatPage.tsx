import { useEffect, useRef, useState } from "react"
import { motion, AnimatePresence } from "framer-motion"
import { Input } from "./ui/input"
import { Button } from "./ui/button"
import { ArrowRight, Sparkles } from "lucide-react"
import { useChat } from "../context/ChatContext"
import { queryAgent } from "../middleware/query"
import { WidgetRenderer } from "./WidgetRenderer"

export default function ChatPage() {
  const { messages, addMessage } = useChat()
  const [inputValue, setInputValue] = useState("")
  const [loading, setLoading] = useState(false)
  const [widgets, setWidgets] = useState<any[]>([])
  const bottomRef = useRef<HTMLDivElement | null>(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" })
  }, [messages, loading])

  async function handleSend(customMessage?: string) {
    const text = customMessage ?? inputValue.trim()
    if (!text) return
    const userMsg = { id: crypto.randomUUID(), role: "user" as const, text }
    addMessage(userMsg)
    setInputValue("")
    setLoading(true)
    try {
      const res = await queryAgent(text)
      const agentMsg = { id: crypto.randomUUID(), role: "agent" as const, text: res.response }
      addMessage(agentMsg)
      setWidgets(res.widgets || [])
    } catch {
      addMessage({ id: crypto.randomUUID(), role: "agent", text: "Error: could not get response." })
    } finally {
      setLoading(false)
    }
  }

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === "Enter") handleSend()
  }

  const hasWidgets = widgets.length > 0

  return (
    <div className="flex h-screen bg-white overflow-hidden">
      <AnimatePresence initial={false}>
        <motion.div
          key="chat"
          initial={{ width: "100%" }}
          animate={{ width: hasWidgets ? "30%" : "100%" }}
          transition={{ duration: 0.5, ease: "easeInOut" }}
          className="flex items-center justify-center p-6"
        >
          <div className="w-full h-full bg-gray-50 rounded-3xl shadow-[0_8px_30px_rgba(0,0,0,0.08)] flex flex-col relative overflow-hidden">
            <div className="flex-1 overflow-y-auto px-4 pt-8 pb-32 space-y-3">
              {messages.map((m) => (
                <div
                  key={m.id}
                  className={`flex ${m.role === "user" ? "justify-end" : "justify-start items-start gap-2"}`}
                >
                  {m.role === "agent" && (
                    <div className="flex-shrink-0 mt-1">
                      <div className="w-6 h-6 rounded-full bg-white flex items-center justify-center">
                        <div className="bg-gradient-to-r from-[#B7B1F2] to-[#FDB7EA] bg-clip-text">
                          <Sparkles
                            className="w-3 h-3 text-transparent"
                            style={{ stroke: "url(#sparkle-gradient)" }}
                          />
                        </div>
                        <svg width="0" height="0">
                          <defs>
                            <linearGradient id="sparkle-gradient" x1="0%" y1="0%" x2="100%" y2="0%">
                              <stop offset="0%" stopColor="#B7B1F2" />
                              <stop offset="100%" stopColor="#FDB7EA" />
                            </linearGradient>
                          </defs>
                        </svg>
                      </div>
                    </div>
                  )}
                  <div
                    className={`max-w-[85%] px-3 py-2 text-[13px] ${
                      m.role === "user"
                        ? "bg-[#FFDCCC] rounded-[14px] rounded-br-[4px]"
                        : "bg-white rounded-[14px] rounded-bl-[4px]"
                    }`}
                  >
                    <p className="text-black leading-relaxed font-[500]">{m.text}</p>
                  </div>
                </div>
              ))}

              {loading && (
                <div className="flex justify-start items-start gap-3 animate-in fade-in slide-in-from-bottom-4 duration-500">
                  <div className="flex-shrink-0 mt-1">
                    <div className="w-7 h-7 rounded-full bg-white flex items-center justify-center">
                      <div className="bg-gradient-to-r from-[#B7B1F2] to-[#FDB7EA] bg-clip-text">
                        <Sparkles
                          className="w-4 h-4 text-transparent animate-pulse"
                          style={{ stroke: "url(#sparkle-gradient)" }}
                        />
                      </div>
                    </div>
                  </div>
                  <div className="max-w-[70%] px-5 py-3.5 bg-white rounded-[18px] rounded-bl-[4px]">
                    <p className="text-gray-500 text-[16px] leading-relaxed font-[500] flex items-center gap-2">
                      Crunching possibilities
                      <span className="inline-flex gap-0.5">
                        <span className="animate-bounce" style={{ animationDelay: "0ms" }}>.</span>
                        <span className="animate-bounce" style={{ animationDelay: "150ms" }}>.</span>
                        <span className="animate-bounce" style={{ animationDelay: "300ms" }}>.</span>
                      </span>
                    </p>
                  </div>
                </div>
              )}
              <div ref={bottomRef} />
            </div>

            <div className="absolute bottom-4 left-4 right-4">
              <div className="relative bg-white rounded-2xl shadow-[0_4px_16px_rgba(0,0,0,0.05)] transition-all duration-300 focus-within:shadow-[0_0_0_2px_rgba(183,177,242,0.4),0_0_0_4px_rgba(253,183,234,0.4)]">
                <Input
                  type="text"
                  placeholder="Type..."
                  value={inputValue}
                  onChange={(e) => setInputValue(e.target.value)}
                  onKeyPress={handleKeyPress}
                  className="w-full h-14 pl-4 pr-14 rounded-2xl border-0 bg-transparent text-gray-900 placeholder:text-gray-400 focus-visible:ring-0 focus-visible:outline-none text-[14px]"
                />
                <Button
                  onClick={() => handleSend()}
                  size="icon"
                  disabled={loading}
                  className="absolute right-2 top-1/2 -translate-y-1/2 h-8 w-8 rounded-full text-white bg-gradient-to-r from-[#B7B1F2] to-[#FDB7EA]"
                >
                  <ArrowRight className="w-3 h-3" />
                </Button>
              </div>
            </div>
          </div>
        </motion.div>

        {hasWidgets && (
          <motion.div
            key="widgets"
            initial={{ width: 0, opacity: 0 }}
            animate={{ width: "70%", opacity: 1 }}
            exit={{ width: 0, opacity: 0 }}
            transition={{ duration: 0.5, ease: "easeInOut" }}
            className="overflow-y-auto bg-white p-12"
          >
            {widgets.map((widget, idx) => (
              <div key={idx} className="p-6 bg-white">
                <WidgetRenderer html={widget.raw_html_string} onSendMessage={handleSend} />
              </div>
            ))}
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
}