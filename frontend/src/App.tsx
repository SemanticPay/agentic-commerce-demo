import { useState, useRef, useCallback, useEffect } from "react";
import { v4 as uuidv4 } from 'uuid';
import { WelcomeScreen } from "@/components/WelcomeScreen";
import { ChatMessagesView } from "@/components/ChatMessagesView";

type DisplayData = string | null;
interface MessageWithAgent {
  type: "human" | "ai";
  content: string;
  id: string;
  agent?: string;
}

interface ProcessedEvent {
  title: string;
  data: any;
}

export default function App() {
  const [userId, setUserId] = useState<string | null>(null);
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [appName, setAppName] = useState<string | null>(null);
  const [messages, setMessages] = useState<MessageWithAgent[]>([]);
  const [displayData, setDisplayData] = useState<DisplayData | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [messageEvents, setMessageEvents] = useState<Map<string, ProcessedEvent[]>>(new Map());
  const [isBackendReady, setIsBackendReady] = useState(false);
  const [isCheckingBackend, setIsCheckingBackend] = useState(true);
  const currentAgentRef = useRef('');
  const accumulatedTextRef = useRef("");
  const scrollAreaRef = useRef<HTMLDivElement>(null);

  const retryWithBackoff = async (fn: () => Promise<any>, maxRetries = 10, maxDuration = 120000) => {
    const startTime = Date.now();
    let lastError: Error;
    for (let attempt = 0; attempt < maxRetries; attempt++) {
      if (Date.now() - startTime > maxDuration) throw new Error(`Retry timeout after ${maxDuration}ms`);
      try {
        return await fn();
      } catch (error) {
        lastError = error as Error;
        const delay = Math.min(1000 * Math.pow(2, attempt), 5000);
        console.log(`Attempt ${attempt + 1} failed, retrying in ${delay}ms...`, error);
        await new Promise(resolve => setTimeout(resolve, delay));
      }
    }
    throw lastError!;
  };

  const createSession = async () => {
    const sessionId = uuidv4();
    const response = await fetch(`/api/apps/app/users/u_999/sessions/${sessionId}`, {
      method: "POST",
      headers: { "Content-Type": "application/json" }
    });
    if (!response.ok) throw new Error(`Failed to create session: ${response.statusText}`);
    const data = await response.json();
    return { userId: data.userId, sessionId: data.id, appName: data.appName };
  };

  const checkBackendHealth = async () => {
    try {
      const response = await fetch("/api/docs");
      return response.ok;
    } catch (error) {
      console.log("Backend not ready yet:", error);
      return false;
    }
  };

  const extractDataFromSSE = (data: string) => {
    try {
      const parsed = JSON.parse(data);
      const textParts = parsed.content?.parts?.filter((p: any) => p.text).map((p: any) => p.text) || [];
      const agent = parsed.author || '';
      return { textParts, agent };
    } catch (error) {
      console.error('Error parsing SSE data:', error);
      return { textParts: [], agent: '' };
    }
  };

  const getEventTitle = (agentName: string): string => {
    switch (agentName) {
      case "product_agent": return "Searching for Products";
      case "cart_agent": return "Managing Shopping Cart";
      case "shopper_agent": return "Shopping Assistant";
      default: return `Processing (${agentName || 'Unknown Agent'})`;
    }
  };

  const processSseEventData = (jsonData: string, aiMessageId: string) => {
    const { textParts, agent } = extractDataFromSSE(jsonData);

    if (agent && agent !== currentAgentRef.current) currentAgentRef.current = agent;

    if (textParts.length > 0) {
      const eventTitle = getEventTitle(agent);
      setMessageEvents(prev => new Map(prev).set(aiMessageId, [...(prev.get(aiMessageId) || []), {
        title: eventTitle,
        data: { type: 'text', content: textParts.join(" ") }
      }]));

      for (const text of textParts) {
        accumulatedTextRef.current += text + " ";
        setMessages(prev => prev.map(msg =>
          msg.id === aiMessageId ? { ...msg, content: accumulatedTextRef.current.trim(), agent: currentAgentRef.current || msg.agent } : msg
        ));
        setDisplayData(accumulatedTextRef.current.trim());
      }
    }
  };

  const handleSubmit = useCallback(async (query: string) => {
    if (!query.trim()) return;
    setIsLoading(true);

    let currentUserId = userId;
    let currentSessionId = sessionId;
    let currentAppName = appName;

    if (!currentSessionId || !currentUserId || !currentAppName) {
      const sessionData = await retryWithBackoff(createSession);
      currentUserId = sessionData.userId;
      currentSessionId = sessionData.sessionId;
      currentAppName = sessionData.appName;
      setUserId(currentUserId);
      setSessionId(currentSessionId);
      setAppName(currentAppName);
    }

    const userMessageId = Date.now().toString();
    setMessages(prev => [...prev, { type: "human", content: query, id: userMessageId }]);

    const aiMessageId = `${Date.now()}_ai`;
    currentAgentRef.current = '';
    accumulatedTextRef.current = '';
    setMessages(prev => [...prev, { type: "ai", content: "", id: aiMessageId, agent: '' }]);

    try {
      const response = await fetch("/api/run_sse", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          appName: currentAppName,
          userId: currentUserId,
          sessionId: currentSessionId,
          newMessage: { parts: [{ text: query }], role: "user" },
          streaming: false
        })
      });

      if (!response.ok) throw new Error(`Failed: ${response.statusText}`);

      const reader = response.body?.getReader();
      const decoder = new TextDecoder();
      let buffer = "";

      if (reader) {
        while (true) {
          const { done, value } = await reader.read();
          if (value) buffer += decoder.decode(value, { stream: true });

          let line;
          while ((line = buffer.indexOf('\n')) >= 0) {
            const currentLine = buffer.slice(0, line).trim();
            buffer = buffer.slice(line + 1);
            if (currentLine.startsWith('data:')) {
              const data = currentLine.substring(5).trim();
              processSseEventData(data, aiMessageId);
            }
          }
          if (done) break;
        }
      }
    } catch (error: any) {
      setMessages(prev => [...prev, { type: "ai", content: `Error: ${error.message}`, id: `${Date.now()}_ai_error` }]);
    }
    setIsLoading(false);
  }, [appName, sessionId, userId]);

  useEffect(() => {
    const checkBackend = async () => {
      setIsCheckingBackend(true);
      for (let i = 0; i < 60; i++) {
        if (await checkBackendHealth()) {
          setIsBackendReady(true);
          setIsCheckingBackend(false);
          return;
        }
        await new Promise(r => setTimeout(r, 2000));
      }
      setIsCheckingBackend(false);
      console.error("Backend failed to start in time");
    };
    checkBackend();
  }, []);

  const handleCancel = useCallback(() => {
    setMessages([]);
    setDisplayData(null);
    setMessageEvents(new Map());
    window.location.reload();
  }, []);

  const BackendLoadingScreen = () => (
    <div className="flex-1 flex flex-col items-center justify-center p-4">
      <div className="text-center space-y-6">
        <h1 className="text-3xl font-bold">🛍️ SemantikShopper</h1>
        <p>Connecting to backend...</p>
      </div>
    </div>
  );

  return (
    <div className="flex h-screen bg-neutral-800 text-neutral-100 font-sans">
      <main className="flex flex-col h-screen w-full">
        <div className="flex flex-col flex-1 overflow-hidden">
          {isCheckingBackend ? (
            <BackendLoadingScreen />
          ) : !isBackendReady ? (
            <div className="flex flex-col items-center justify-center flex-1">
              <h2 className="text-2xl font-bold text-red-400">Backend Unavailable</h2>
              <button onClick={() => window.location.reload()} className="mt-4 px-4 py-2 bg-blue-600 rounded-lg">
                Retry
              </button>
            </div>
          ) : messages.length === 0 ? (
            <WelcomeScreen handleSubmit={handleSubmit} isLoading={isLoading} onCancel={handleCancel} />
          ) : (
            <ChatMessagesView
              messages={messages}
              isLoading={isLoading}
              scrollAreaRef={scrollAreaRef}
              onSubmit={handleSubmit}
              onCancel={handleCancel}
              displayData={displayData}
              messageEvents={messageEvents}
            />
          )}
        </div>
      </main>
    </div>
  );
}