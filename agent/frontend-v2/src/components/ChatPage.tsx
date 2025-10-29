import { useState } from "react";
import { Input } from "./ui/input";
import { Button } from "./ui/button";
import { ArrowLeft, ArrowRight, Sparkles } from "lucide-react";
import { Link, useNavigate } from "react-router-dom";

interface Message {
  id: number;
  sender: "user" | "agent";
  text: string;
}

// const initialMessages: Message[] = [
//   { id: 1, sender: "user", text: "Hey, I'm going on my first ski trip and need equipment." },
//   { id: 2, sender: "agent", text: "Nice! Let's get you ready. Do you already have any equipment, or are we starting from scratch?" },
//   { id: 3, sender: "user", text: "Starting from scratch." },
//   { id: 4, sender: "agent", text: "Got it. Where are you skiing—Alps, Rockies, or a smaller resort? Temperature and snow type help me pick the right gear." },
//   { id: 5, sender: "user", text: "Going to Val Thorens in January." },
//   { id: 6, sender: "agent", text: "Great. What's your height and weight so I can size them properly?" },
//   { id: 7, sender: "user", text: "178 cm, 72 kg." },
//   { id: 8, sender: "agent", text: "Perfect. You'll need skis around 165–170 cm. Do you want me to keep it budget-friendly or go for mid-range quality?" },
//   { id: 9, sender: "user", text: "Mid-range sounds good." },
// ];

export default function ChatPage() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputValue, setInputValue] = useState("");
  const navigate = useNavigate();
  
  // Check if the last message is "Mid-range sounds good."
  const lastMessage = messages[messages.length - 1];
  // const showCurating = lastMessage?.sender === "user" && lastMessage?.text.toLowerCase().includes("mid-range sounds good"); // TODO: think further and bring back

  const handleSend = () => {
    if (!inputValue.trim()) return;
    
    const newMessage: Message = {
      id: messages.length + 1,
      sender: "user",
      text: inputValue,
    };
    
    setMessages([...messages, newMessage]);
    setInputValue("");

    // TODO: make call to the backend
    // TODO: add the backend response to the messages list

    
    // Redirect to catalog page after sending any messag
    // TODO: only redirect to catalog if there are any widgets
    setTimeout(() => {
      navigate("/catalog");
    }, 500);
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === "Enter") {
      handleSend();
    }
  };

  return (
    <div className="min-h-screen bg-white">
      {/* Chat Messages */}
      <div className="max-w-4xl mx-auto px-6 pt-12 pb-32 space-y-4">
        {messages.map((message, index) => (
          <div
            key={message.id}
            className={`flex ${message.sender === "user" ? "justify-end" : "justify-start items-start gap-3"} animate-in fade-in slide-in-from-bottom-4 duration-500`}
            style={{ animationDelay: `${index * 50}ms` }}
          >
            {message.sender === "agent" && (
              <div className="flex-shrink-0 mt-1">
                <div className="w-7 h-7 rounded-full bg-white flex items-center justify-center">
                  <div className="bg-gradient-to-r from-[#B7B1F2] to-[#FDB7EA] bg-clip-text">
                    <Sparkles className="w-4 h-4 text-transparent" style={{
                      stroke: 'url(#sparkle-gradient)',
                    }} />
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
              className={`max-w-[70%] px-5 py-3.5 transition-all duration-200 ${
                message.sender === "user"
                  ? "bg-[#FFDCCC] rounded-[18px] rounded-br-[4px]"
                  : "bg-white rounded-[18px] rounded-bl-[4px]"
              }`}
            >
              <p className="text-black text-[16px] leading-relaxed font-[500]">
                {message.text}
              </p>
            </div>
          </div>
        ))}
        
        {/* TODO: bring back */}
        {/* Curating Indicator */}
        {/* showCurating && (
          <div className="space-y-4">
            <div className="flex justify-start items-start gap-3 animate-in fade-in slide-in-from-bottom-4 duration-500">
              <div className="flex-shrink-0 mt-1">
                <div className="w-7 h-7 rounded-full bg-white flex items-center justify-center">
                  <div className="bg-gradient-to-r from-[#B7B1F2] to-[#FDB7EA] bg-clip-text">
                    <Sparkles className="w-4 h-4 text-transparent animate-pulse" style={{
                      stroke: 'url(#sparkle-gradient)',
                    }} />
                  </div>
                </div>
              </div>
              <div className="max-w-[70%] px-5 py-3.5 bg-white rounded-[18px] rounded-bl-[4px]">
                <p className="text-gray-500 text-[16px] leading-relaxed font-[500] flex items-center gap-2">
                  Curating a shopping list for you
                  <span className="inline-flex gap-0.5">
                    <span className="animate-bounce" style={{ animationDelay: '0ms' }}>.</span>
                    <span className="animate-bounce" style={{ animationDelay: '150ms' }}>.</span>
                    <span className="animate-bounce" style={{ animationDelay: '300ms' }}>.</span>
                  </span>
                </p>
              </div>
            </div>
            
            <div className="flex justify-center animate-in fade-in slide-in-from-bottom-4 duration-500" style={{ animationDelay: '800ms' }}>
              <Link to="/catalog">
                <Button className="bg-gradient-to-r from-[#B7B1F2] to-[#FDB7EA] text-white hover:shadow-lg hover:scale-105 transition-all duration-200 rounded-2xl px-8 h-12">
                  View Your Personalized Catalog
                  <ArrowRight className="w-4 h-4 ml-2" />
                </Button>
              </Link>
            </div>
          </div>
        ) */}
      </div>

      {/* Floating Input Widget */}
      <div className="fixed bottom-8 left-1/2 -translate-x-1/2 w-full max-w-2xl px-6">
        <div className="relative bg-white rounded-2xl shadow-[0_4px_16px_rgba(0,0,0,0.05)] transition-all duration-300 hover:scale-[1.02] focus-within:scale-[1.02] focus-within:shadow-[0_0_0_3px_rgba(183,177,242,0.4),0_0_0_6px_rgba(253,183,234,0.4)]">
          <Input
            type="text"
            placeholder="Type your message..."
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            onKeyUp={handleKeyPress}
            className="w-full h-20 pl-6 pr-20 rounded-2xl border-0 bg-transparent text-gray-900 placeholder:text-gray-400 focus-visible:ring-0 focus-visible:outline-none transition-all duration-200"
          />
          <Button
            onClick={handleSend}
            size="icon"
            className="absolute right-4 top-1/2 -translate-y-1/2 h-10 w-10 rounded-full text-white bg-gradient-to-r from-[#B7B1F2] to-[#FDB7EA] shadow-md hover:shadow-lg hover:scale-105 transition-all duration-200"
          >
            <ArrowRight className="w-4 h-4" />
          </Button>
        </div>
      </div>
    </div>
  );
}
