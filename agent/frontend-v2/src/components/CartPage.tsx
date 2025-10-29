import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { Input } from "./ui/input";
import { Button } from "./ui/button";
import { Dialog, DialogContent } from "./ui/dialog";
import { ArrowRight, Sparkles, Search, Plus, Minus, Trash2, Edit, ShoppingBag, CreditCard, Wand2 } from "lucide-react";
import { ImageWithFallback } from "./figma/ImageWithFallback";
import outfitVisualization from "figma:asset/860be0bea9b4ab9996111557bb287a54687a54e2.png";

interface Message {
  id: number;
  sender: "user" | "agent";
  text: string;
  image?: string;
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

interface CartItem {
  id: string;
  name: string;
  description: string;
  category: string;
  price: number;
  originalPrice?: number;
  discount?: number;
  quantity: number;
  image: string;
}

export default function CartPage() {
  const navigate = useNavigate();
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputValue, setInputValue] = useState("");
  const [showVisualization, setShowVisualization] = useState(false);
  const [fullscreenImage, setFullscreenImage] = useState(false);
  const [cartItems, setCartItems] = useState<CartItem[]>([]);
  // const [cartItems, setCartItems] = useState<CartItem[]>([
  //   {
  //     id: "helmet-1",
  //     name: "Smith Vantage MIPS",
  //     description: "Dual ventilation zones, advanced safety.",
  //     category: "Helmet",
  //     price: 289,
  //     originalPrice: 340,
  //     discount: 15,
  //     quantity: 1,
  //     image: "https://images.unsplash.com/photo-1612964627570-769abf00d41f?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w3Nzg4Nzd8MHwxfHNlYXJjaHwxfHxzbWl0aCUyMHNraSUyMGhlbG1ldHxlbnwxfHx8fDE3NjEwNjE3MDN8MA&ixlib=rb-4.1.0&q=80&w=1080&utm_source=figma&utm_medium=referral",
  //   },
  //   {
  //     id: "goggle-2",
  //     name: "Smith I/O Mag",
  //     description: "Quick lens swap system.",
  //     category: "Goggles",
  //     price: 249,
  //     originalPrice: 299,
  //     discount: 17,
  //     quantity: 1,
  //     image: "https://images.unsplash.com/photo-1614270270735-e93b1234fc7c?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w3Nzg4Nzd8MHwxfHNlYXJjaHwxfHxzbWl0aCUyMGdvZ2dsZXMlMjBzbm93fGVufDF8fHx8MTc2MTA2MTcwNXww&ixlib=rb-4.1.0&q=80&w=1080&utm_source=figma&utm_medium=referral",
  //   },
  //   {
  //     id: "boot-2",
  //     name: "Salomon S/Pro 100",
  //     description: "Custom fit shell for all-day comfort.",
  //     category: "Boots",
  //     price: 449,
  //     originalPrice: 549,
  //     discount: 18,
  //     quantity: 1,
  //     image: "https://images.unsplash.com/photo-1645999140947-db7546fecb30?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w3Nzg4Nzd8MHwxfHNlYXJjaHwxfHxzYWxvbW9uJTIwc2tpJTIwYm9vdHN8ZW58MXx8fHwxNzYxMDYxNzA2fDA&ixlib=rb-4.1.0&q=80&w=1080&utm_source=figma&utm_medium=referral",
  //   },
  // ]);

  const handleVisualize = () => {
    setShowVisualization(true);
  };

  const handleSend = () => {
    if (!inputValue.trim()) return;
    setInputValue("");
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === "Enter") {
      handleSend();
    }
  };

  const updateQuantity = (id: string, delta: number) => {
    setCartItems(items =>
      items.map(item =>
        item.id === id
          ? { ...item, quantity: Math.max(1, item.quantity + delta) }
          : item
      )
    );
  };

  const removeItem = (id: string) => {
    // TODO: call the agent to remove item from cart
    setCartItems(items => items.filter(item => item.id !== id));
  };

  const subtotal = cartItems.reduce((sum, item) => sum + item.price * item.quantity, 0);
  const totalSavings = cartItems.reduce((sum, item) => {
    if (item.originalPrice) {
      return sum + (item.originalPrice - item.price) * item.quantity;
    }
    return sum;
  }, 0);

  return (
    <div className="flex h-screen bg-white overflow-hidden">
      {/* Left Sidebar - Chat (30%) */}
      <div className="w-[30%] flex items-center justify-center p-6">
        <div className="w-full h-full bg-gray-50 rounded-3xl shadow-[0_8px_30px_rgba(0,0,0,0.08)] flex flex-col relative">
          {/* Chat Messages */}
          <div className="flex-1 overflow-y-auto px-4 pt-8 pb-32 space-y-3">
            {messages.map((message) => (
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

            {/* TODO: bring back */}
            {/* Visualization Result */}
            {/* {showVisualization && (
              <div className="flex justify-start items-start gap-2 mx-4 mt-4">
                <div className="flex-shrink-0 mt-1">
                  <div className="w-6 h-6 rounded-full bg-white flex items-center justify-center">
                    <div className="bg-gradient-to-r from-[#B7B1F2] to-[#FDB7EA] bg-clip-text">
                      <Sparkles className="w-3 h-3 text-transparent" style={{
                        stroke: 'url(#sparkle-gradient-2)',
                      }} />
                    </div>
                    <svg width="0" height="0">
                      <defs>
                        <linearGradient id="sparkle-gradient-2" x1="0%" y1="0%" x2="100%" y2="0%">
                          <stop offset="0%" stopColor="#B7B1F2" />
                          <stop offset="100%" stopColor="#FDB7EA" />
                        </linearGradient>
                      </defs>
                    </svg>
                  </div>
                </div>
                <div className="max-w-[85%] bg-white rounded-[14px] rounded-bl-[4px] overflow-hidden">
                  <ImageWithFallback
                    src={outfitVisualization}
                    alt="Outfit visualization"
                    className="w-full h-auto cursor-pointer hover:opacity-95 transition-opacity"
                    onClick={() => setFullscreenImage(true)}
                  />
                  <p className="text-black leading-relaxed font-[500] text-[13px] px-3 py-2">
                    Here's how your complete outfit looks together! What do you think?
                  </p>
                </div>
              </div>
            )} */}
          </div>

          {/* Input Widget */}
          <div className="absolute bottom-4 left-4 right-4">
            <div className="relative bg-white rounded-2xl shadow-[0_4px_16px_rgba(0,0,0,0.05)] transition-all duration-300 focus-within:shadow-[0_0_0_2px_rgba(183,177,242,0.4),0_0_0_4px_rgba(253,183,234,0.4)]">
              <Input
                type="text"
                placeholder="Type..."
                value={inputValue}
                onChange={(e) => setInputValue(e.target.value)}
                onKeyUp={handleKeyPress}
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

      {/* Right Panel - Cart (70%) */}
      <div className="w-[70%] overflow-y-auto">
        <div className="max-w-5xl mx-auto px-12 py-6">
          <div className="mb-5 flex items-start justify-between">
            <div>
              <h1 className="text-black mb-1">Your Cart</h1>
              <p className="text-gray-600 text-[14px]">
                {cartItems.length} {cartItems.length === 1 ? 'item' : 'items'} ready for checkout
              </p>
            </div>
            
            {/* TODO: bring back */}
            {/* AI Visualization Button */}
            {/* <Button 
              onClick={handleVisualize}
              disabled={showVisualization}
              className="bg-black text-white hover:bg-gray-800 hover:shadow-lg hover:scale-[1.02] transition-all duration-300 rounded-xl h-10 px-4 flex items-center justify-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <Wand2 className="w-4 h-4" />
              <span>Visualize My Fit</span>
            </Button> */}
          </div>

          {/* Cart Items */}
          <div className="space-y-3 mb-5">
            {cartItems.map((item) => (
              <div
                key={item.id}
                className="bg-white rounded-xl shadow-[0_2px_12px_rgba(0,0,0,0.04)] hover:shadow-[0_4px_20px_rgba(0,0,0,0.08)] transition-all duration-300 p-3"
              >
                <div className="flex gap-3">
                  <ImageWithFallback
                    src={item.image}
                    alt={item.name}
                    className="w-16 h-16 object-cover rounded-lg flex-shrink-0"
                  />
                  
                  <div className="flex-grow">
                    <div className="flex items-start justify-between mb-1">
                      <div>
                        <p className="text-gray-500 text-[11px]">{item.category}</p>
                        <h3 className="text-black text-[14px] leading-tight">{item.name}</h3>
                        <p className="text-gray-600 text-[12px] leading-tight">{item.description}</p>
                      </div>
                      
                      <div className="flex gap-1">
                        {/* TODO: bring back */}
                        {/* <Button
                          size="icon"
                          variant="ghost"
                          className="h-7 w-7 rounded-lg hover:bg-gray-100 transition-colors"
                        >
                          <Edit className="w-3 h-3 text-gray-600" />
                        </Button> */}
                        <Button
                          size="icon"
                          variant="ghost"
                          onClick={() => removeItem(item.id)}
                          className="h-7 w-7 rounded-lg hover:bg-red-50 hover:text-red-600 transition-colors"
                        >
                          <Trash2 className="w-3 h-3" />
                        </Button>
                      </div>
                    </div>

                    <div className="flex items-end justify-between mt-2">
                      {/* Quantity Controls */}
                      <div className="flex items-center gap-1.5">
                        {/* TODO: bring back */}
                        {/* <Button
                          size="icon"
                          onClick={() => updateQuantity(item.id, -1)}
                          className="h-7 w-7 rounded-lg bg-gray-100 hover:bg-gray-200 text-black transition-colors"
                        >
                          <Minus className="w-3 h-3" />
                        </Button> */}
                        <span className="text-black min-w-[20px] text-center text-[13px]">In cart: {item.quantity}</span>
                        {/* TODO: bring back */}
                        {/* <Button
                          size="icon"
                          onClick={() => updateQuantity(item.id, 1)}
                          className="h-7 w-7 rounded-lg bg-gray-100 hover:bg-gray-200 text-black transition-colors"
                        >
                          <Plus className="w-3 h-3" />
                        </Button> */}
                      </div>

                      {/* Price */}
                      <div className="text-right">
                        <div className="flex items-center gap-1.5">
                          {/* TODO: bring back */}
                          {/* {item.originalPrice && (
                            <span className="text-gray-400 text-[12px] line-through">
                              ${item.originalPrice}
                            </span>
                          )} */}
                          <span className="text-black text-[15px]">
                            ${item.price}
                          </span>
                        </div>
                        {/* TODO: bring back */}
                        {/* {item.discount && (
                          <span className="inline-block px-1.5 py-0.5 bg-[#FBF3B9] text-black text-[9px] rounded mt-0.5">
                            {item.discount}% off
                          </span>
                        )} */}
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>

          {/* Cart Summary */}
          <div className="bg-gray-50 rounded-xl p-3 mb-5">
            <div className="space-y-2 mb-3">
              <div className="flex items-center justify-between text-[14px]">
                <span className="text-gray-600">Subtotal</span>
                <span className="text-black">${subtotal}</span>
              </div>
              {/* TODO: bring back */}
              {/* {totalSavings > 0 && (
                <div className="flex items-center justify-between text-[14px]">
                  <span className="text-gray-600">Savings</span>
                  <span className="text-green-600">-${totalSavings}</span>
                </div>
              )} */}
              <div className="flex items-center justify-between text-[13px]">
                <span className="text-gray-600">Shipping</span>
                <span className="text-gray-600">At checkout</span>
              </div>
            </div>
            
            <div className="h-px bg-gray-200 my-3" />
            
            <div className="flex items-center justify-between">
              <span className="text-black">Total</span>
              <span className="text-black">${subtotal}</span>
            </div>
          </div>

          {/* Action Buttons */}
          <div className="flex gap-3">
            <Button
              onClick={() => navigate("/catalog")}
              className="flex-1 bg-white text-black border border-gray-200 hover:bg-gray-50 hover:shadow-md hover:scale-[1.02] transition-all duration-200 rounded-xl h-12 flex items-center justify-center gap-2"
            >
              <ShoppingBag className="w-4 h-4" />
              Continue Shopping
            </Button>
            <Button
              className="flex-1 bg-black text-white hover:bg-gray-800 hover:shadow-lg hover:scale-[1.02] transition-all duration-200 rounded-xl h-12 flex items-center justify-center gap-2"
            >
              <CreditCard className="w-4 h-4" />
              Proceed to Checkout
              {/* TODO: link to the checkout URL */}
            </Button>
          </div>
        </div>
      </div>

      {/* TODO: bring back */}
      {/* Fullscreen Image Dialog */}
      {/* <Dialog open={fullscreenImage} onOpenChange={setFullscreenImage}>
        <DialogContent className="max-w-[95vw] max-h-[95vh] p-0 bg-black/95 border-0">
          <div className="flex items-center justify-center w-full h-full">
            <ImageWithFallback
              src={outfitVisualization}
              alt="Outfit visualization fullscreen"
              className="max-w-full max-h-[95vh] object-contain"
            />
          </div>
        </DialogContent>
      </Dialog> */}
    </div>
  );
}
