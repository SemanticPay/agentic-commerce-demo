import type React from "react";
import { useState, useEffect, ReactNode } from "react";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Loader2, Copy, CopyCheck } from "lucide-react";
import { InputForm } from "@/components/InputForm";
import { Button } from "@/components/ui/button";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { cn } from "@/utils";
import { Badge } from "@/components/ui/badge";
import CheckoutModal from "./CheckoutModal"
type MdComponentProps = {
  className?: string;
  children?: ReactNode;
  [key: string]: any;
};

interface ProcessedEvent {
  title: string;
  data: any;
}

// ✅ Markdown render components (including clickable image cards)
const mdComponents = {
  h1: ({ className, children, ...props }: MdComponentProps) => (
    <h1 className={cn("text-2xl font-bold mt-4 mb-2", className)} {...props}>{children}</h1>
  ),
  h2: ({ className, children, ...props }: MdComponentProps) => (
    <h2 className={cn("text-xl font-bold mt-3 mb-2", className)} {...props}>{children}</h2>
  ),
  h3: ({ className, children, ...props }: MdComponentProps) => (
    <h3 className={cn("text-lg font-bold mt-3 mb-1", className)} {...props}>{children}</h3>
  ),
  p: ({ className, children, ...props }: MdComponentProps) => (
    <p className={cn("mb-3 leading-7", className)} {...props}>{children}</p>
  ),
  a: ({ className, children, href, ...props }: MdComponentProps) => (
    <Badge className="text-xs mx-0.5">
      <a
        className={cn("text-blue-400 hover:text-blue-300 text-xs", className)}
        href={href}
        target="_blank"
        rel="noopener noreferrer"
        {...props}
      >{children}</a>
    </Badge>
  ),
  ul: ({ className, children, ...props }: MdComponentProps) => (
    <ul className={cn("list-disc pl-6 mb-3", className)} {...props}>{children}</ul>
  ),
  ol: ({ className, children, ...props }: MdComponentProps) => (
    <ol className={cn("list-decimal pl-6 mb-3", className)} {...props}>{children}</ol>
  ),
  li: ({ className, children, ...props }: MdComponentProps) => (
    <li className={cn("mb-1", className)} {...props}>{children}</li>
  ),
  blockquote: ({ className, children, ...props }: MdComponentProps) => (
    <blockquote className={cn("border-l-4 border-neutral-600 pl-4 italic my-3 text-sm", className)} {...props}>{children}</blockquote>
  ),
  code: ({ className, children, ...props }: MdComponentProps) => (
    <code className={cn("bg-neutral-900 rounded px-1 py-0.5 font-mono text-xs", className)} {...props}>{children}</code>
  ),
  pre: ({ className, children, ...props }: MdComponentProps) => (
    <pre className={cn("bg-neutral-900 p-3 rounded-lg overflow-x-auto font-mono text-xs my-3", className)} {...props}>{children}</pre>
  ),
  hr: ({ className, ...props }: MdComponentProps) => (
    <hr className={cn("border-neutral-600 my-4", className)} {...props} />
  ),
  table: ({ className, children, ...props }: MdComponentProps) => (
    <div className="my-3 overflow-x-auto">
      <table className={cn("border-collapse w-full", className)} {...props}>{children}</table>
    </div>
  ),
  th: ({ className, children, ...props }: MdComponentProps) => (
    <th className={cn("border border-neutral-600 px-3 py-2 text-left font-bold", className)} {...props}>{children}</th>
  ),
  td: ({ className, children, ...props }: MdComponentProps) => (
    <td className={cn("border border-neutral-600 px-3 py-2", className)} {...props}>{children}</td>
  ),

  img: ({ src, alt }) => (
    <div
      onClick={() => {
        const event = new CustomEvent("chat-message", {
          detail: { text: `Add item ${alt} to cart` }
        });
        window.dispatchEvent(event);
      }}
      className="p-2 inline-block bg-neutral-800 border border-neutral-600 rounded-xl 
                 m-2 text-center w-[180px] cursor-pointer hover:border-blue-400 transition-all"
    >
      <img
        src={src}
        alt={alt}
        className="object-cover h-[180px] w-full rounded-md mb-2"
      />
      <div className="text-xs text-neutral-300">{alt}</div>
    </div>
  ),
};

interface ChatMessagesViewProps {
  messages: {
    type: "human" | "ai";
    content: string;
    id: string;
    agent?: string;
    finalReportWithCitations?: boolean;
  }[];
  isLoading: boolean;
  scrollAreaRef: React.RefObject<HTMLDivElement | null>;
  onSubmit: (query: string) => void;
  onCancel: () => void;
  displayData: string | null;
  messageEvents: Map<string, ProcessedEvent[]>;
  websiteCount: number;
}

export function ChatMessagesView({
  messages,
  isLoading,
  scrollAreaRef,
  onSubmit,
  onCancel,
}: ChatMessagesViewProps) {
  const [copiedMessageId, setCopiedMessageId] = useState<string | null>(null);

  // 🧠 Listen for synthetic "chat-message" events (like clicking product images)
  useEffect(() => {
    const handleSyntheticMessage = (e: any) => {
      const text = e.detail?.text;
      if (text) onSubmit(text);
    };
    window.addEventListener("chat-message", handleSyntheticMessage);
    return () => window.removeEventListener("chat-message", handleSyntheticMessage);
  }, [onSubmit]);

  const handleCopy = async (text: string, messageId: string) => {
    try {
      await navigator.clipboard.writeText(text);
      setCopiedMessageId(messageId);
      setTimeout(() => setCopiedMessageId(null), 2000);
    } catch (err) {
      console.error("Failed to copy text:", err);
    }
  };

  const handleNewChat = () => window.location.reload();

  return (
    <div className="flex flex-col h-full w-full">
      {/* 🧭 Header */}
      <div className="border-b border-neutral-700 p-4 bg-neutral-800">
        <div className="max-w-4xl mx-auto flex justify-between items-center">
          <h1 className="text-lg font-semibold text-neutral-100">Shop</h1>
          <Button
            onClick={handleNewChat}
            variant="outline"
            className="bg-neutral-700 hover:bg-neutral-600 text-neutral-100 
                       border-neutral-600 hover:border-neutral-500"
          >
            New Chat
          </Button>
        </div>
      </div>

      {/* 💬 Chat area */}
      <div className="flex-1 flex flex-col w-full overflow-hidden">
        <ScrollArea
          ref={scrollAreaRef}
          className="flex-1 w-full overflow-y-auto max-h-[calc(100vh-160px)]"
        >
          <div className="p-4 md:p-6 space-y-2 max-w-4xl mx-auto">
            {messages.map((message) => (
              <div
                key={message.id}
                className={`flex ${message.type === "human" ? "justify-end" : "justify-start"}`}
              >
                {message.type === "human" ? (
                  <div className="text-white bg-neutral-700 px-4 pt-3 rounded-3xl 
                                  break-words max-w-[100%] sm:max-w-[90%] rounded-br-lg">
                    <ReactMarkdown components={mdComponents} remarkPlugins={[remarkGfm]}>
                      {message.content}
                    </ReactMarkdown>
                  </div>
                ) : (
                  <div className="relative break-words flex flex-col w-full">
                    <div className="flex items-start gap-3">
                      <div className="flex-1">
                        <ReactMarkdown components={mdComponents} remarkPlugins={[remarkGfm]}>
                          {message.content}
                        </ReactMarkdown>
                      </div>
                      <button
                        onClick={() => handleCopy(message.content, message.id)}
                        className="p-1 hover:bg-neutral-700 rounded"
                      >
                        {copiedMessageId === message.id ? (
                          <CopyCheck className="h-4 w-4 text-green-500" />
                        ) : (
                          <Copy className="h-4 w-4 text-neutral-400" />
                        )}
                      </button>
                    </div>
                  </div>
                )}
              </div>
            ))}

            {/* 🔄 Loading Indicator */}
            {isLoading && (
              <div className="flex justify-start pl-10 pt-2">
                <div className="flex items-center gap-2 text-neutral-400">
                  <Loader2 className="h-4 w-4 animate-spin" />
                  <span>Thinking...</span>
                </div>
              </div>
            )}
          </div>
        </ScrollArea>
      </div>

      {/* 🧾 Input section */}
      <div className="border-t border-neutral-700 p-4 w-full">
        <div className="max-w-3xl mx-auto">
          <InputForm onSubmit={onSubmit} isLoading={isLoading} context="chat" />
          {isLoading && (
            <div className="mt-4 flex justify-center">
              <Button
                variant="outline"
                onClick={onCancel}
                className="text-red-400 hover:text-red-300"
              >
                Cancel
              </Button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}