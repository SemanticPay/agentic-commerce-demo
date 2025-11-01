import { createRoot } from "react-dom/client"
import App from "./App.tsx"
import "./index.css"
import { ChatProvider } from "./context/ChatContext"

createRoot(document.getElementById("root")!).render(
  <ChatProvider>
    <App />
  </ChatProvider>
)