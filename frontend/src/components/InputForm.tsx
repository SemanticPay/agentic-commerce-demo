import { useState, useRef, useEffect } from "react"
import { Button } from "@/components/ui/button"
import { Textarea } from "@/components/ui/textarea"
import {
  Loader2,
  Send,
  ShoppingCart,
  CreditCard,
  Trash2,
} from "lucide-react"
import CheckoutModal from "@/components/CheckoutModal"

interface InputFormProps {
  onSubmit: (query: string) => void
  isLoading: boolean
  context?: "homepage" | "chat"
}

export function InputForm({
  onSubmit,
  isLoading,
  context = "homepage",
}: InputFormProps) {
  const [inputValue, setInputValue] = useState("")
  const [checkoutOpen, setCheckoutOpen] = useState(false)
  const textareaRef = useRef<HTMLTextAreaElement>(null)

  useEffect(() => {
    if (textareaRef.current) textareaRef.current.focus()
  }, [])

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (inputValue.trim() && !isLoading) {
      onSubmit(inputValue.trim())
      setInputValue("")
    }
  }

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault()
      handleSubmit(e)
    }
  }

  const placeholderText =
    context === "chat"
      ? "Respond to the agent, update your cart, or ask a follow-up..."
      : "What are you shopping for today? Try something like 'Find me running shoes under $100'"

  return (
    <>
      <form onSubmit={handleSubmit} className="flex flex-col gap-4 w-full">
        {/* Input Row */}
        <div className="flex items-end space-x-2">
          <Textarea
            ref={textareaRef}
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder={placeholderText}
            rows={1}
            className="flex-1 resize-none pr-10 min-h-[40px]"
          />

          <Button type="submit" size="icon" disabled={isLoading || !inputValue.trim()}>
            {isLoading ? (
              <Loader2 className="h-4 w-4 animate-spin" />
            ) : (
              <Send className="h-4 w-4" />
            )}
          </Button>
        </div>

        {/* Cart Action Buttons - Only in Chat Mode */}
        {!isLoading && context === "chat" && (
          <div className="mt-2 w-full flex justify-center gap-3">
            <Button
              variant="secondary"
              className="text-blue-600 border-blue-600 hover:bg-blue-50"
              onClick={() => console.log("Show Cart clicked")}
              type="button"
            >
              <ShoppingCart className="w-4 h-4 mr-2" />
              Show Cart
            </Button>

            <Button
              variant="default"
              className="bg-green-600 hover:bg-green-500 text-white"
              onClick={() => setCheckoutOpen(true)}
              type="button"
            >
              <CreditCard className="w-4 h-4 mr-2" />
              Checkout
            </Button>

            <Button
              variant="destructive"
              className="bg-red-600 hover:bg-red-500 text-white"
              onClick={() => console.log("Empty Cart clicked")}
              type="button"
            >
              <Trash2 className="w-4 h-4 mr-2" />
              Empty Cart
            </Button>
          </div>
        )}
      </form>

      {/* ✅ Checkout Modal */}
      <CheckoutModal open={checkoutOpen} onClose={() => setCheckoutOpen(false)} />
    </>
  )
}