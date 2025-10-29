import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { Input } from "./ui/input";
import { Button } from "./ui/button";
import { ArrowRight, Sparkles, ShoppingCart, Search } from "lucide-react";
import { ImageWithFallback } from "./figma/ImageWithFallback";

interface Message {
  id: number;
  sender: "user" | "agent";
  text: string;
}

// const chatMessages: Message[] = [
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


interface Product {
  id: string;
  title: string;
  description: string;
  image: string;
}

interface Category {
  title: string;
  subtitle: string;
  description: string;
  products: Product[];
}

// const catalog: Category[] = [
//   {
//     title: "Skis (Size 165–170 cm)",
//     subtitle: "All-Mountain / Mid-Range Quality",
//     description: "Perfect for your first trip to Val Thorens. These all-mountain skis are sized for your height (178 cm) and designed to handle mixed snow conditions. They're forgiving for beginners while being quality enough to grow with you.",
//     products: [
//       {
//         id: "ski-1",
//         title: "Nordica Enforcer 88",
//         description: "Stable on groomed and mixed snow.",
//         image: "https://images.unsplash.com/photo-1544036674-eca5143b8cd0?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w3Nzg4Nzd8MHwxfHNlYXJjaHwxfHxub3JkaWNhJTIwc2tpcyUyMHdpbnRlcnxlbnwxfHx8fDE3NjEwNjE3MDJ8MA&ixlib=rb-4.1.0&q=80&w=1080&utm_source=figma&utm_medium=referral",
//       },
//       {
//         id: "ski-2",
//         title: "Salomon QST 92",
//         description: "Versatile and forgiving for intermediate skiers.",
//         image: "https://images.unsplash.com/photo-1617807061622-c9f19f8d9277?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w3Nzg4Nzd8MHwxfHNlYXJjaHwxfHxzYWxvbW9uJTIwc2tpcyUyMG1vdW50YWlufGVufDF8fHx8MTc2MTA2MTcwM3ww&ixlib=rb-4.1.0&q=80&w=1080&utm_source=figma&utm_medium=referral",
//       },
//       {
//         id: "ski-3",
//         title: "Rossignol Experience 82 Ti",
//         description: "Smooth turns, great edge control.",
//         image: "https://images.unsplash.com/photo-1758672143199-38bc522fbea4?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w3Nzg4Nzd8MHwxfHNlYXJjaHwxfHxyb3NzaWdub2wlMjBza2lzJTIwc25vd3xlbnwxfHx8fDE3NjEwNjE3MDN8MA&ixlib=rb-4.1.0&q=80&w=1080&utm_source=figma&utm_medium=referral",
//       },
//     ],
//   },
//   {
//     title: "Helmets",
//     subtitle: "Lightweight & Ventilated",
//     description: "Safety first for your Alpine adventure. These helmets feature MIPS technology for advanced protection and ventilation systems to keep you comfortable during January's cold temperatures at high altitude.",
//     products: [
//       {
//         id: "helmet-1",
//         title: "Smith Vantage MIPS",
//         description: "Dual ventilation zones, advanced safety.",
//         image: "https://images.unsplash.com/photo-1612964627570-769abf00d41f?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w3Nzg4Nzd8MHwxfHNlYXJjaHwxfHxzbWl0aCUyMHNraSUyMGhlbG1ldHxlbnwxfHx8fDE3NjEwNjE3MDN8MA&ixlib=rb-4.1.0&q=80&w=1080&utm_source=figma&utm_medium=referral",
//       },
//       {
//         id: "helmet-2",
//         title: "POC Obex Spin",
//         description: "Sleek fit, integrated communication-ready design.",
//         image: "https://images.unsplash.com/photo-1544620862-d47d57948ecc?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w3Nzg4Nzd8MHwxfHNlYXJjaHwxfHxwb2MlMjBoZWxtZXQlMjBza2lpbmd8ZW58MXx8fHwxNzYxMDYxNzA0fDA&ixlib=rb-4.1.0&q=80&w=1080&utm_source=figma&utm_medium=referral",
//       },
//       {
//         id: "helmet-3",
//         title: "Giro Jackson MIPS",
//         description: "Adjustable venting, comfort liner.",
//         image: "https://images.unsplash.com/photo-1674078118432-cfcb778b191f?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w3Nzg4Nzd8MHwxfHNlYXJjaHwxfHxnaXJvJTIwc2tpJTIwaGVsbWV0fGVufDF8fHx8MTc2MTA2MTcwNHww&ixlib=rb-4.1.0&q=80&w=1080&utm_source=figma&utm_medium=referral",
//       },
//     ],
//   },
//   {
//     title: "Goggles",
//     subtitle: "All-Condition Lenses",
//     description: "Essential for varying weather conditions in the Alps. These goggles handle everything from sunny days to snowy conditions, with anti-fog technology to keep your vision clear throughout the day.",
//     products: [
//       {
//         id: "goggle-1",
//         title: "Oakley Flight Deck XM",
//         description: "Wide vision, anti-fog tech.",
//         image: "https://images.unsplash.com/photo-1513908512605-c58d3f08079f?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w3Nzg4Nzd8MHwxfHNlYXJjaHwxfHxvYWtsZXklMjBza2klMjBnb2dnbGVzfGVufDF8fHx8MTc2MTA2MTcwNXww&ixlib=rb-4.1.0&q=80&w=1080&utm_source=figma&utm_medium=referral",
//       },
//       {
//         id: "goggle-2",
//         title: "Smith I/O Mag",
//         description: "Quick lens swap system.",
//         image: "https://images.unsplash.com/photo-1614270270735-e93b1234fc7c?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w3Nzg4Nzd8MHwxfHNlYXJjaHwxfHxzbWl0aCUyMGdvZ2dsZXMlMjBzbm93fGVufDF8fHx8MTc2MTA2MTcwNXww&ixlib=rb-4.1.0&q=80&w=1080&utm_source=figma&utm_medium=referral",
//       },
//       {
//         id: "goggle-3",
//         title: "Anon M4 Toric",
//         description: "Magnetic face mask integration.",
//         image: "https://images.unsplash.com/photo-1634834506092-04e032e18bea?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w3Nzg4Nzd8MHwxfHNlYXJjaHwxfHxhbm9uJTIwZ29nZ2xlcyUyMHdpbnRlcnxlbnwxfHx8fDE3NjEwNjE3MDV8MA&ixlib=rb-4.1.0&q=80&w=1080&utm_source=figma&utm_medium=referral",
//       },
//     ],
//   },
//   {
//     title: "Boots",
//     subtitle: "Medium Flex (For Comfort + Control)",
//     description: "The right balance for a first-timer. Medium flex boots give you the support you need to learn proper technique while staying comfortable during full days on the mountain. Sized to match your weight and skill level.",
//     products: [
//       {
//         id: "boot-1",
//         title: "Atomic Hawx Prime 100",
//         description: "Ideal balance for mid-range performance.",
//         image: "https://images.unsplash.com/photo-1727582917307-25078b767df9?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w3Nzg4Nzd8MHwxfHNlYXJjaHwxfHxhdG9taWMlMjBza2klMjBib290c3xlbnwxfHx8fDE3NjEwNjE3MDZ8MA&ixlib=rb-4.1.0&q=80&w=1080&utm_source=figma&utm_medium=referral",
//       },
//       {
//         id: "boot-2",
//         title: "Salomon S/Pro 100",
//         description: "Custom fit shell for all-day comfort.",
//         image: "https://images.unsplash.com/photo-1645999140947-db7546fecb30?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w3Nzg4Nzd8MHwxfHNlYXJjaHwxfHxzYWxvbW9uJTIwc2tpJTIwYm9vdHN8ZW58MXx8fHwxNzYxMDYxNzA2fDA&ixlib=rb-4.1.0&q=80&w=1080&utm_source=figma&utm_medium=referral",
//       },
//       {
//         id: "boot-3",
//         title: "Lange RX 100",
//         description: "Classic mid-flex with precision fit.",
//         image: "https://images.unsplash.com/photo-1628736775595-b4e7deebc5c8?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w3Nzg4Nzd8MHwxfHNlYXJjaHwxfHxsYW5nZSUyMHNraSUyMGJvb3RzfGVufDF8fHx8MTc2MTA2MTcwNnww&ixlib=rb-4.1.0&q=80&w=1080&utm_source=figma&utm_medium=referral",
//       },
//     ],
//   },
// ];

export default function CatalogPage() {
  const navigate = useNavigate();
  const [messages] = useState<Message[]>([]);
  const [catalog, setCatalog] = useState<Category[]>([]);
  const [inputValue, setInputValue] = useState("");
  // const [cartCount, setCartCount] = useState(3);

  // TODO: send to backend and handle the response (re-render widgets?)
  // use setCatalog
  const handleSend = () => {
    if (!inputValue.trim()) return;
    setInputValue("");
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === "Enter") {
      handleSend();
    }
  };

  const handleAddToCart = () => {
    // setCartCount(prev => prev + 1);
    // TODO: call the agent to add item to cart
  };

  return (
    <div className="flex h-screen bg-white overflow-hidden">
      {/* Left Sidebar - Chat (30%) */}
      <div className="w-[30%] flex items-center justify-center p-6">
        <div className="w-full h-full bg-gray-50 rounded-3xl shadow-[0_8px_30px_rgba(0,0,0,0.08)] flex flex-col relative">
          {/* Chat Messages */}
          <div className="flex-1 overflow-y-auto px-4 pt-8 pb-32 space-y-3">
          {messages.map((message, index) => (
            <div
              key={message.id}
              className={`flex ${message.sender === "user" ? "justify-end" : "justify-start items-start gap-2"}`}
            >
              {message.sender === "agent" && (
                <div className="flex-shrink-0 mt-1">
                  <div className="w-6 h-6 rounded-full bg-white flex items-center justify-center">
                    <div className="bg-gradient-to-r from-[#B7B1F2] to-[#FDB7EA] bg-clip-text">
                      <Sparkles className="w-3 h-3 text-transparent" style={{
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
                className={`max-w-[85%] px-3 py-2 text-[13px] ${
                  message.sender === "user"
                    ? "bg-[#FFDCCC] rounded-[14px] rounded-br-[4px]"
                    : "bg-white rounded-[14px] rounded-bl-[4px]"
                }`}
              >
                <p className="text-black leading-relaxed font-[500]">
                  {message.text}
                </p>
              </div>
            </div>
          ))}
          
          {/* TODO: bring back */}
          {/* Query Box */}
          {/* <div className="mx-4 mt-4 bg-white rounded-2xl p-3 shadow-[0_2px_12px_rgba(0,0,0,0.06)]">
            <div className="flex items-center justify-between mb-2">
              <div className="flex items-center gap-2">
                <Search className="w-3.5 h-3.5 text-gray-500" />
                <span className="text-black text-[12px]">Query</span>
              </div>
              <span className="text-gray-500 text-[11px]">22 results</span>
            </div>
            <p className="text-gray-600 text-[13px] leading-relaxed italic">
              Find mid-range ski equipment for a beginner skier (178 cm, 72 kg) going to Val Thorens in January — include skis sized around 165–170 cm, helmet, goggles, and boots suitable for cold Alpine snow.
            </p>
          </div> */}
        </div>

          {/* Input Widget */}
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
                onClick={handleSend}
                size="icon"
                className="absolute right-2 top-1/2 -translate-y-1/2 h-8 w-8 rounded-full text-white bg-gradient-to-r from-[#B7B1F2] to-[#FDB7EA] shadow-md hover:shadow-lg hover:scale-105 transition-all duration-200"
              >
                <ArrowRight className="w-3 h-3" />
              </Button>
            </div>
          </div>
        </div>
      </div>

      {/* Right Panel - Product Catalog (70%) */}
      <div className="w-[70%] overflow-y-auto relative">
        <div className="max-w-6xl mx-auto px-12 py-12">
          <div className="space-y-12">
            {catalog.map((category, categoryIndex) => (
              <div key={categoryIndex} className="space-y-6">
                <div>
                  <h2 className="text-black mb-1">{category.title}</h2>
                  <p className="text-gray-500 mb-3">{category.subtitle}</p>
                  <p className="text-gray-600 text-[15px] leading-relaxed max-w-3xl">{category.description}</p>
                </div>

                <div className="grid grid-cols-3 gap-6">
                  {category.products.map((product) => (
                    <div
                      key={product.id}
                      className="bg-white rounded-2xl overflow-hidden shadow-[0_2px_12px_rgba(0,0,0,0.04)] hover:shadow-[0_4px_20px_rgba(0,0,0,0.08)] transition-all duration-300 flex flex-col h-full"
                    >
                      <ImageWithFallback
                        src={product.image}
                        alt={product.title}
                        className="w-full h-48 object-cover flex-shrink-0"
                      />
                      <div className="p-6 flex flex-col flex-grow">
                        <div className="flex-grow mb-4">
                          <h3 className="text-black mb-2">{product.title}</h3>
                          <p className="text-gray-600 text-[14px] leading-relaxed">
                            {product.description}
                          </p>
                        </div>
                        <div className="flex gap-3">
                          <Button
                            onClick={handleAddToCart}
                            className="flex-1 bg-white text-black border border-gray-200 hover:bg-gray-50 hover:shadow-md hover:scale-[1.02] transition-all duration-200 rounded-xl h-11"
                          >
                            <ShoppingCart className="w-4 h-4 mr-2" />
                            Add to Cart
                          </Button>
                          {/* <Button
                            onClick={() => navigate(`/product/${product.id}`)}
                            className="flex-1 bg-white text-black border border-gray-200 hover:bg-gray-50 hover:shadow-md hover:scale-[1.02] transition-all duration-200 rounded-xl h-11"
                          >
                            // TODO: change this, this is static, should render product related info
                            Show More
                          </Button> */}
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </div>
        
        {/* Floating Cart Button */}
        <Button
          onClick={() => navigate("/cart")}
          className="fixed bottom-8 right-8 h-14 w-14 rounded-full bg-black shadow-[0_8px_24px_rgba(0,0,0,0.15)] hover:shadow-[0_12px_32px_rgba(0,0,0,0.2)] hover:scale-110 transition-all duration-300 flex items-center justify-center"
        >
          <ShoppingCart className="w-5 h-5 text-white" />
          {/* TODO: bring back */}
          {/* {cartCount > 0 && (
            <div className="absolute -top-1 -right-1 h-6 w-6 rounded-full bg-[#FFDCCC] flex items-center justify-center shadow-md">
              <span className="text-black text-[11px] font-[600]">{cartCount}</span>
            </div>
          )} */}
        </Button>
      </div>
    </div>
  );
}
