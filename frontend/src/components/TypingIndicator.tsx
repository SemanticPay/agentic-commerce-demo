import { useEffect, useState } from "react"

export function TypingIndicator() {
  const [dots, setDots] = useState(".")

  useEffect(() => {
    const dotFrames = [".", "..", "..."]
    let frame = 0

    const interval = setInterval(() => {
      frame = (frame + 1) % dotFrames.length
      setDots(dotFrames[frame])
    }, 500)

    return () => clearInterval(interval)
  }, [])

  return (
    <div className="text-gray-500 italic px-4 py-2 animate-pulse">
      Agent is typing{dots}
    </div>
  )
}