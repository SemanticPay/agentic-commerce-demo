import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { Input } from "./ui/input";
import { Button } from "./ui/button";
import { Carousel, CarouselContent, CarouselItem, CarouselNext, CarouselPrevious } from "./ui/carousel";
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "./ui/dialog";
import { Progress } from "./ui/progress";
import { ArrowRight, Sparkles, Search, ShoppingCart, Star, Package, TruckIcon, Shield, ChevronLeft, Check, X, AlertCircle } from "lucide-react";
import { ImageWithFallback } from "./figma/ImageWithFallback";

interface Message {
  id: number;
  sender: "user" | "agent";
  text: string;
}

const chatMessages: Message[] = [
  { id: 1, sender: "user", text: "Hey, I'm going on my first ski trip and need equipment." },
  { id: 2, sender: "agent", text: "Nice! Let's get you ready. Do you already have any equipment, or are we starting from scratch?" },
  { id: 3, sender: "user", text: "Starting from scratch." },
  { id: 4, sender: "agent", text: "Got it. Where are you skiing—Alps, Rockies, or a smaller resort? Temperature and snow type help me pick the right gear." },
  { id: 5, sender: "user", text: "Going to Val Thorens in January." },
  { id: 6, sender: "agent", text: "Great. What's your height and weight so I can size them properly?" },
  { id: 7, sender: "user", text: "178 cm, 72 kg." },
  { id: 8, sender: "agent", text: "Perfect. You'll need skis around 165–170 cm. Do you want me to keep it budget-friendly or go for mid-range quality?" },
  { id: 9, sender: "user", text: "Mid-range sounds good." },
];

const productImages = [
  "https://images.unsplash.com/photo-1612964627570-769abf00d41f?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w3Nzg4Nzd8MHwxfHNlYXJjaHwxfHxzbWl0aCUyMHNraSUyMGhlbG1ldCUyMHdoaXRlfGVufDF8fHx8MTc2MTIwNjU5NHww&ixlib=rb-4.1.0&q=80&w=1080&utm_source=figma&utm_medium=referral",
  "https://images.unsplash.com/photo-1701522907629-f04a5ace7180?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w3Nzg4Nzd8MHwxfHNlYXJjaHwxfHxza2klMjBoZWxtZXQlMjBibGFjayUyMGNsb3NldXB8ZW58MXx8fHwxNzYxMjA2NTk2fDA&ixlib=rb-4.1.0&q=80&w=1080&utm_source=figma&utm_medium=referral",
  "https://images.unsplash.com/photo-1612964627570-769abf00d41f?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w3Nzg4Nzd8MHwxfHNlYXJjaHwxfHxzbWl0aCUyMHNraSUyMGhlbG1ldHxlbnwxfHx8fDE3NjEwNjE3MDN8MA&ixlib=rb-4.1.0&q=80&w=1080&utm_source=figma&utm_medium=referral",
];

const similarItems = [
  {
    id: "helmet-2",
    name: "POC Obex Spin",
    price: 269,
    originalPrice: 319,
    rating: 4.7,
    image: "https://images.unsplash.com/photo-1725826474121-6005426455d5?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w3Nzg4Nzd8MHwxfHNlYXJjaHwxfHxwb2MlMjBza2klMjBoZWxtZXR8ZW58MXx8fHwxNzYxMjA2NTk2fDA&ixlib=rb-4.1.0&q=80&w=1080&utm_source=figma&utm_medium=referral",
    mips: false,
    spin: true,
    vents: 16,
    weight: 470,
    warranty: 2,
    audioReady: true,
    adjustableFit: true,
  },
  {
    id: "helmet-3",
    name: "Giro Range MIPS",
    price: 259,
    originalPrice: 299,
    rating: 4.6,
    image: "https://images.unsplash.com/photo-1674078118432-cfcb778b191f?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w3Nzg4Nzd8MHwxfHNlYXJjaHwxfHxnaXJvJTIwc2tpJTIwaGVsbWV0fGVufDF8fHx8MTc2MTIwNjU5Nnww&ixlib=rb-4.1.0&q=80&w=1080&utm_source=figma&utm_medium=referral",
    mips: true,
    spin: false,
    vents: 14,
    weight: 490,
    warranty: 3,
    audioReady: false,
    adjustableFit: true,
  },
  {
    id: "helmet-4",
    name: "Anon Prime MIPS",
    price: 279,
    originalPrice: 329,
    rating: 4.5,
    image: "https://images.unsplash.com/photo-1612964627570-769abf00d41f?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w3Nzg4Nzd8MHwxfHNlYXJjaHwxfHxzbWl0aCUyMHNraSUyMGhlbG1ldHxlbnwxfHx8fDE3NjEwNjE3MDN8MA&ixlib=rb-4.1.0&q=80&w=1080&utm_source=figma&utm_medium=referral",
    mips: true,
    spin: false,
    vents: 18,
    weight: 460,
    warranty: 2,
    audioReady: true,
    adjustableFit: false,
  },
];

const addOns = [
  {
    id: "addon-1",
    name: "Smith I/O Mag Goggles",
    price: 249,
    image: "https://images.unsplash.com/photo-1760373899648-9bff88285962?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w3Nzg4Nzd8MHwxfHNlYXJjaHwxfHxza2klMjBnb2dnbGVzJTIwZXF1aXBtZW50fGVufDF8fHx8MTc2MTIwNjU5Nnww&ixlib=rb-4.1.0&q=80&w=1080&utm_source=figma&utm_medium=referral",
  },
  {
    id: "addon-2",
    name: "Helmet Liner",
    price: 29,
    image: "https://images.unsplash.com/photo-1634834506092-04e032e18bea?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w3Nzg4Nzd8MHwxfHNlYXJjaHwxfHxoZWxtZXQlMjBsaW5lciUyMHdpbnRlcnxlbnwxfHx8fDE3NjEyMDY1OTZ8MA&ixlib=rb-4.1.0&q=80&w=1080&utm_source=figma&utm_medium=referral",
  },
  {
    id: "addon-3",
    name: "Helmet Storage Bag",
    price: 19,
    image: "https://images.unsplash.com/photo-1725826474121-6005426455d5?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w3Nzg4Nzd8MHwxfHNlYXJjaHwxfHxza2klMjBoZWxtZXQlMjBiYWd8ZW58MXx8fHwxNzYxMjA2NTk3fDA&ixlib=rb-4.1.0&q=80&w=1080&utm_source=figma&utm_medium=referral",
  },
];

// Main product data
const mainProduct = {
  id: "helmet-1",
  name: "Smith Vantage MIPS",
  price: 289,
  originalPrice: 340,
  rating: 4.8,
  mips: true,
  vents: 21,
  weight: 450,
  warranty: 3,
  audioReady: true,
  adjustableFit: true,
};

export default function ProductPage() {
  const navigate = useNavigate();
  const [messages] = useState<Message[]>(chatMessages);
  const [inputValue, setInputValue] = useState("");
  const [cartCount] = useState(3);
  const [isCompareOpen, setIsCompareOpen] = useState(false);
  const [compareItem, setCompareItem] = useState<typeof similarItems[0] | null>(null);

  const handleSend = () => {
    if (!inputValue.trim()) return;
    setInputValue("");
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === "Enter") {
      handleSend();
    }
  };

  const handleCompare = (item: typeof similarItems[0]) => {
    setCompareItem(item);
    setIsCompareOpen(true);
  };

  return (
    <div className="flex h-screen bg-white overflow-hidden">
      {/* Floating Cart Button */}
      <Button
        onClick={() => navigate("/cart")}
        className="fixed bottom-8 right-8 h-14 w-14 rounded-full bg-black shadow-[0_8px_24px_rgba(0,0,0,0.15)] hover:shadow-[0_12px_32px_rgba(0,0,0,0.2)] hover:scale-110 transition-all duration-300 flex items-center justify-center z-50"
      >
        <ShoppingCart className="w-5 h-5 text-white" />
        {cartCount > 0 && (
          <div className="absolute -top-1 -right-1 h-6 w-6 rounded-full bg-[#FFDCCC] flex items-center justify-center shadow-md">
            <span className="text-black text-[11px] font-[600]">{cartCount}</span>
          </div>
        )}
      </Button>

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
            
            {/* Query Box */}
            <div className="mx-4 mt-4 bg-white rounded-2xl p-3 shadow-[0_2px_12px_rgba(0,0,0,0.06)]">
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
            </div>
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

      {/* Right Panel - Product Details (70%) */}
      <div className="w-[70%] overflow-y-auto">
        <div className="max-w-5xl mx-auto px-12 py-6">
          {/* Back Button */}
          <button
            onClick={() => navigate("/catalog")}
            className="flex items-center gap-2 text-gray-600 hover:text-black transition-colors mb-4 group"
          >
            <ChevronLeft className="w-4 h-4 group-hover:-translate-x-0.5 transition-transform" />
            <span className="text-[14px]">Back to Catalog</span>
          </button>

          {/* Hero Section */}
          <div className="grid grid-cols-2 gap-8 mb-8">
            {/* Image Carousel */}
            <div className="relative">
              <Carousel className="w-full">
                <CarouselContent>
                  {productImages.map((image, index) => (
                    <CarouselItem key={index}>
                      <div className="aspect-square rounded-2xl overflow-hidden bg-gray-50">
                        <ImageWithFallback
                          src={image}
                          alt={`Smith Vantage MIPS ${index + 1}`}
                          className="w-full h-full object-cover"
                        />
                      </div>
                    </CarouselItem>
                  ))}
                </CarouselContent>
                <CarouselPrevious className="left-4" />
                <CarouselNext className="right-4" />
              </Carousel>
              
              {/* Floating Add to Cart Button */}
              <Button className="absolute bottom-4 left-4 bg-black text-white hover:bg-gray-800 hover:shadow-lg hover:scale-[1.02] transition-all duration-300 rounded-xl h-11 px-5 flex items-center justify-center gap-2">
                <ShoppingCart className="w-4 h-4" />
                <span>Add to Cart</span>
              </Button>
            </div>

            {/* Product Info */}
            <div>
              <h1 className="text-black mb-2">Smith Vantage MIPS</h1>
              
              {/* Rating & Stock */}
              <div className="flex items-center gap-4 mb-4">
                <div className="flex items-center gap-1">
                  <Star className="w-4 h-4 fill-[#FBF3B9] text-[#FBF3B9]" />
                  <span className="text-[14px] text-black">4.8</span>
                  <span className="text-[14px] text-gray-500">(342 reviews)</span>
                </div>
                <div className="flex items-center gap-1.5">
                  <div className="w-2 h-2 rounded-full bg-green-500" />
                  <span className="text-[14px] text-gray-600">In Stock</span>
                </div>
              </div>

              {/* Price */}
              <div className="mb-6">
                <div className="flex items-center gap-3 mb-1">
                  <span className="text-gray-400 line-through text-[20px]">$340</span>
                  <span className="text-black text-[32px]">$289</span>
                  <span className="px-2 py-1 bg-[#FBF3B9] text-black text-[12px] rounded">15% off</span>
                </div>
                <p className="text-gray-600 text-[14px]">Save $51 on this premium helmet</p>
              </div>

              {/* Description */}
              <p className="text-gray-700 text-[15px] leading-relaxed mb-6">
                The Smith Vantage MIPS is a premium ski helmet featuring advanced MIPS (Multi-directional Impact Protection System) technology and dual ventilation zones. Perfect for your Val Thorens trip, it offers superior protection and comfort in cold Alpine conditions.
              </p>

              {/* Quick Specs */}
              <div className="space-y-2">
                <div className="flex items-center gap-3 text-[14px]">
                  <Shield className="w-4 h-4 text-gray-500" />
                  <span className="text-gray-600">MIPS advanced safety technology</span>
                </div>
                <div className="flex items-center gap-3 text-[14px]">
                  <Package className="w-4 h-4 text-gray-500" />
                  <span className="text-gray-600">Adjustable ventilation system</span>
                </div>
                <div className="flex items-center gap-3 text-[14px]">
                  <TruckIcon className="w-4 h-4 text-gray-500" />
                  <span className="text-gray-600">Free delivery in 3-5 business days</span>
                </div>
              </div>
            </div>
          </div>

          {/* Confidence Bars */}
          <div className="grid grid-cols-2 gap-6 mb-8">
            {/* Fit Confidence */}
            <div className="bg-white rounded-xl shadow-[0_2px_12px_rgba(0,0,0,0.04)] p-5">
              <div className="flex items-center justify-between mb-3">
                <h3 className="text-black text-[15px]">Profile Fit Confidence</h3>
                <span className="text-[14px] text-green-600 font-[600]">92%</span>
              </div>
              <div className="relative mb-3">
                <Progress value={92} className="h-2.5 bg-gray-100" />
                <div 
                  className="absolute top-0 left-0 h-2.5 rounded-full bg-gradient-to-r from-green-500 to-green-400 transition-all"
                  style={{ width: '92%' }}
                />
              </div>
              <div className="flex items-start gap-2">
                <AlertCircle className="w-4 h-4 text-green-600 mt-0.5 flex-shrink-0" />
                <p className="text-[13px] text-gray-700 leading-relaxed">
                  <span className="font-[600] text-green-700">Excellent match:</span> Based on your profile (178 cm, 72 kg) and Val Thorens trip details, this helmet is highly recommended. Size M will fit perfectly with the adjustable system.
                </p>
              </div>
            </div>

            {/* Return Risk */}
            <div className="bg-white rounded-xl shadow-[0_2px_12px_rgba(0,0,0,0.04)] p-5">
              <div className="flex items-center justify-between mb-3">
                <h3 className="text-black text-[15px]">Return Risk</h3>
                <span className="text-[14px] text-green-600 font-[600]">Low (8%)</span>
              </div>
              <div className="relative mb-3">
                <Progress value={8} className="h-2.5 bg-gray-100" />
                <div 
                  className="absolute top-0 left-0 h-2.5 rounded-full bg-gradient-to-r from-green-500 to-green-400 transition-all"
                  style={{ width: '8%' }}
                />
              </div>
              <div className="flex items-start gap-2">
                <AlertCircle className="w-4 h-4 text-green-600 mt-0.5 flex-shrink-0" />
                <p className="text-[13px] text-gray-700 leading-relaxed">
                  <span className="font-[600] text-green-700">Very low risk:</span> This helmet matches your beginner needs and trip conditions. Similar profiles report 96% satisfaction. No sizing concerns expected.
                </p>
              </div>
            </div>
          </div>

          {/* Personal Fit Summary */}
          <div className="bg-gradient-to-br from-[#B7B1F2]/10 to-[#FDB7EA]/10 rounded-2xl p-6 mb-8">
            <div className="flex items-start gap-3">
              <div className="flex-shrink-0 mt-1">
                <div className="w-8 h-8 rounded-full bg-white flex items-center justify-center shadow-sm">
                  <Sparkles className="w-4 h-4 text-[#B7B1F2]" />
                </div>
              </div>
              <div>
                <h3 className="text-black mb-2">Perfect for Your Trip</h3>
                <p className="text-gray-700 text-[15px] leading-relaxed">
                  Based on your Val Thorens January trip, this helmet is ideal. The dual ventilation system works great in cold Alpine conditions (-5°C to -15°C typical for January), while the MIPS technology provides the advanced safety you need as a beginner. The adjustable fit system accommodates various head shapes, and it's compatible with most goggles for seamless integration with your gear.
                </p>
              </div>
            </div>
          </div>

          {/* Insights Section */}
          <div className="grid grid-cols-2 gap-6 mb-8">
            {/* Key Specs */}
            <div className="bg-white rounded-xl shadow-[0_2px_12px_rgba(0,0,0,0.04)] p-5">
              <h3 className="text-black mb-3">Key Features</h3>
              <ul className="space-y-2.5">
                <li className="text-[14px] text-gray-700 leading-relaxed">
                  <span className="font-[600]">MIPS Protection:</span> Reduces rotational forces during angled impacts
                </li>
                <li className="text-[14px] text-gray-700 leading-relaxed">
                  <span className="font-[600]">Dual Ventilation:</span> 21 vents with adjustable climate control
                </li>
                <li className="text-[14px] text-gray-700 leading-relaxed">
                  <span className="font-[600]">Lightweight:</span> Only 450g for all-day comfort
                </li>
                <li className="text-[14px] text-gray-700 leading-relaxed">
                  <span className="font-[600]">Audio Compatible:</span> Removable ear pads for headphone integration
                </li>
              </ul>
            </div>

            {/* Warranty & Returns */}
            <div className="bg-white rounded-xl shadow-[0_2px_12px_rgba(0,0,0,0.04)] p-5">
              <h3 className="text-black mb-3">Coverage & Returns</h3>
              <div className="space-y-3">
                <div>
                  <p className="text-[14px] text-black font-[600] mb-1">3-Year Warranty</p>
                  <p className="text-[13px] text-gray-600 leading-relaxed">Full manufacturer coverage against defects</p>
                </div>
                <div>
                  <p className="text-[14px] text-black font-[600] mb-1">60-Day Returns</p>
                  <p className="text-[13px] text-gray-600 leading-relaxed">Free returns within 60 days, no questions asked</p>
                </div>
                <div>
                  <p className="text-[14px] text-black font-[600] mb-1">Crash Replacement</p>
                  <p className="text-[13px] text-gray-600 leading-relaxed">50% off replacement if damaged in first year</p>
                </div>
              </div>
            </div>

            {/* Delivery */}
            <div className="bg-white rounded-xl shadow-[0_2px_12px_rgba(0,0,0,0.04)] p-5">
              <h3 className="text-black mb-3">Delivery Options</h3>
              <div className="space-y-3">
                <div className="flex items-start gap-3">
                  <TruckIcon className="w-4 h-4 text-gray-500 mt-0.5" />
                  <div>
                    <p className="text-[14px] text-black font-[600] mb-1">Standard Shipping</p>
                    <p className="text-[13px] text-gray-600">Free • 3-5 business days</p>
                  </div>
                </div>
                <div className="flex items-start gap-3">
                  <TruckIcon className="w-4 h-4 text-gray-500 mt-0.5" />
                  <div>
                    <p className="text-[14px] text-black font-[600] mb-1">Express Shipping</p>
                    <p className="text-[13px] text-gray-600">$15 • 1-2 business days</p>
                  </div>
                </div>
              </div>
            </div>

            {/* Reviews Summary */}
            <div className="bg-white rounded-xl shadow-[0_2px_12px_rgba(0,0,0,0.04)] p-5">
              <h3 className="text-black mb-3">What Customers Say</h3>
              <div className="space-y-2.5">
                <p className="text-[14px] text-gray-700 leading-relaxed italic">
                  "Incredibly comfortable even on long ski days. The ventilation system really works."
                </p>
                <p className="text-[14px] text-gray-700 leading-relaxed italic">
                  "Great fit and feels very secure. Love the goggle integration."
                </p>
                <p className="text-[14px] text-gray-700 leading-relaxed italic">
                  "Worth every penny. My head stays warm but never overheats."
                </p>
              </div>
            </div>
          </div>

          {/* Similar Items */}
          <div className="mb-8">
            <h2 className="text-black mb-4">Similar Helmets</h2>
            <div className="grid grid-cols-3 gap-4">
              {similarItems.map((item) => (
                <div
                  key={item.id}
                  className="bg-white rounded-xl shadow-[0_2px_12px_rgba(0,0,0,0.04)] hover:shadow-[0_4px_20px_rgba(0,0,0,0.08)] transition-all duration-300 overflow-hidden"
                >
                  <div className="aspect-square overflow-hidden bg-gray-50">
                    <ImageWithFallback
                      src={item.image}
                      alt={item.name}
                      className="w-full h-full object-cover"
                    />
                  </div>
                  <div className="p-4">
                    <h4 className="text-black text-[14px] mb-1">{item.name}</h4>
                    <div className="flex items-center gap-1 mb-2">
                      <Star className="w-3 h-3 fill-[#FBF3B9] text-[#FBF3B9]" />
                      <span className="text-[12px] text-gray-600">{item.rating}</span>
                    </div>
                    <div className="flex items-center gap-2 mb-3">
                      <span className="text-gray-400 line-through text-[12px]">${item.originalPrice}</span>
                      <span className="text-black text-[16px]">${item.price}</span>
                    </div>
                    <div className="flex gap-2">
                      <Button 
                        onClick={() => handleCompare(item)}
                        variant="outline"
                        className="flex-1 h-9 text-[12px] rounded-lg border-gray-200 hover:bg-gray-50"
                      >
                        Compare
                      </Button>
                      <Button 
                        className="flex-1 h-9 text-[12px] rounded-lg bg-black text-white hover:bg-gray-800"
                      >
                        Show More
                      </Button>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Add-Ons */}
          <div className="mb-8">
            <h2 className="text-black mb-4">Complete Your Setup</h2>
            <div className="grid grid-cols-3 gap-4">
              {addOns.map((addon) => (
                <div
                  key={addon.id}
                  className="bg-white rounded-xl shadow-[0_2px_12px_rgba(0,0,0,0.04)] hover:shadow-[0_4px_20px_rgba(0,0,0,0.08)] transition-all duration-300 overflow-hidden group"
                >
                  <div className="aspect-square overflow-hidden bg-gray-50">
                    <ImageWithFallback
                      src={addon.image}
                      alt={addon.name}
                      className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
                    />
                  </div>
                  <div className="p-4">
                    <h4 className="text-black text-[14px] mb-2">{addon.name}</h4>
                    <div className="flex items-center justify-between mb-3">
                      <span className="text-black text-[16px]">${addon.price}</span>
                    </div>
                    <div className="flex gap-2">
                      <Button 
                        className="flex-1 h-9 text-[12px] rounded-lg bg-white text-black border border-gray-200 hover:bg-gray-50 flex items-center justify-center gap-1.5"
                      >
                        <ShoppingCart className="w-3 h-3" />
                        Add to Cart
                      </Button>
                      <Button 
                        className="flex-1 h-9 text-[12px] rounded-lg bg-black text-white hover:bg-gray-800"
                      >
                        Show More
                      </Button>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* Comparison Modal */}
      <Dialog open={isCompareOpen} onOpenChange={setIsCompareOpen}>
        <DialogContent className="max-w-4xl max-h-[90vh] overflow-y-auto">
          <DialogHeader>
            <div className="flex items-center gap-3 mb-2">
              <div className="flex items-center gap-2 px-3 py-1.5 bg-gradient-to-r from-[#B7B1F2]/20 to-[#FDB7EA]/20 rounded-full">
                <Sparkles className="w-3.5 h-3.5 text-[#B7B1F2]" />
                <span className="text-[12px] text-gray-700">Generated by Shopping Agent</span>
              </div>
            </div>
            <DialogTitle className="text-left">Product Comparison</DialogTitle>
          </DialogHeader>

          {compareItem && (
            <div className="space-y-6">
              {/* Comparison Table */}
              <div className="overflow-hidden rounded-xl border border-gray-200">
                <table className="w-full">
                  <thead>
                    <tr className="bg-gray-50 border-b border-gray-200">
                      <th className="text-left p-4 text-[14px] text-gray-700 w-1/3">Feature</th>
                      <th className="text-center p-4 text-[14px] text-gray-900 w-1/3">
                        <div className="flex flex-col items-center gap-1">
                          <span>{mainProduct.name}</span>
                          <span className="text-[#B7B1F2] text-[12px]">Current</span>
                        </div>
                      </th>
                      <th className="text-center p-4 text-[14px] text-gray-900 w-1/3">{compareItem.name}</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr className="border-b border-gray-100">
                      <td className="p-4 text-[14px] text-gray-700">Price</td>
                      <td className="p-4 text-center">
                        <div className="flex flex-col items-center gap-1">
                          <span className="text-[16px] text-black">${mainProduct.price}</span>
                          <span className="text-[12px] text-gray-400 line-through">${mainProduct.originalPrice}</span>
                        </div>
                      </td>
                      <td className="p-4 text-center">
                        <div className="flex flex-col items-center gap-1">
                          <span className="text-[16px] text-black">${compareItem.price}</span>
                          <span className="text-[12px] text-gray-400 line-through">${compareItem.originalPrice}</span>
                        </div>
                      </td>
                    </tr>
                    <tr className="border-b border-gray-100 bg-gray-50/50">
                      <td className="p-4 text-[14px] text-gray-700">
                        <div>
                          <p className="font-[600] mb-0.5">Safety Technology</p>
                          <p className="text-[12px] text-gray-500">Impact protection system</p>
                        </div>
                      </td>
                      <td className="p-4 text-center">
                        <div className="flex items-center justify-center gap-2">
                          <Check className="w-4 h-4 text-green-600" />
                          <span className="text-[14px] text-gray-900">MIPS</span>
                        </div>
                      </td>
                      <td className="p-4 text-center">
                        <div className="flex items-center justify-center gap-2">
                          {compareItem.mips ? (
                            <>
                              <Check className="w-4 h-4 text-green-600" />
                              <span className="text-[14px] text-gray-900">MIPS</span>
                            </>
                          ) : compareItem.spin ? (
                            <>
                              <Check className="w-4 h-4 text-green-600" />
                              <span className="text-[14px] text-gray-900">SPIN</span>
                            </>
                          ) : (
                            <X className="w-4 h-4 text-gray-300" />
                          )}
                        </div>
                      </td>
                    </tr>
                    <tr className="border-b border-gray-100">
                      <td className="p-4 text-[14px] text-gray-700">
                        <div>
                          <p className="font-[600] mb-0.5">Ventilation</p>
                          <p className="text-[12px] text-gray-500">Important for Val Thorens cold conditions</p>
                        </div>
                      </td>
                      <td className="p-4 text-center">
                        <span className="text-[14px] text-gray-900">{mainProduct.vents} vents</span>
                      </td>
                      <td className="p-4 text-center">
                        <span className="text-[14px] text-gray-900">{compareItem.vents} vents</span>
                      </td>
                    </tr>
                    <tr className="border-b border-gray-100 bg-gray-50/50">
                      <td className="p-4 text-[14px] text-gray-700">
                        <div>
                          <p className="font-[600] mb-0.5">Weight</p>
                          <p className="text-[12px] text-gray-500">Lighter is better for all-day comfort</p>
                        </div>
                      </td>
                      <td className="p-4 text-center">
                        <span className="text-[14px] text-gray-900">{mainProduct.weight}g</span>
                      </td>
                      <td className="p-4 text-center">
                        <span className="text-[14px] text-gray-900">{compareItem.weight}g</span>
                      </td>
                    </tr>
                    <tr className="border-b border-gray-100">
                      <td className="p-4 text-[14px] text-gray-700">
                        <div>
                          <p className="font-[600] mb-0.5">Warranty</p>
                          <p className="text-[12px] text-gray-500">Peace of mind for your investment</p>
                        </div>
                      </td>
                      <td className="p-4 text-center">
                        <span className="text-[14px] text-gray-900">{mainProduct.warranty} years</span>
                      </td>
                      <td className="p-4 text-center">
                        <span className="text-[14px] text-gray-900">{compareItem.warranty} years</span>
                      </td>
                    </tr>
                    <tr className="border-b border-gray-100 bg-gray-50/50">
                      <td className="p-4 text-[14px] text-gray-700">
                        <div>
                          <p className="font-[600] mb-0.5">Audio Ready</p>
                          <p className="text-[12px] text-gray-500">Compatible with headphones</p>
                        </div>
                      </td>
                      <td className="p-4 text-center">
                        {mainProduct.audioReady ? (
                          <Check className="w-4 h-4 text-green-600 mx-auto" />
                        ) : (
                          <X className="w-4 h-4 text-gray-300 mx-auto" />
                        )}
                      </td>
                      <td className="p-4 text-center">
                        {compareItem.audioReady ? (
                          <Check className="w-4 h-4 text-green-600 mx-auto" />
                        ) : (
                          <X className="w-4 h-4 text-gray-300 mx-auto" />
                        )}
                      </td>
                    </tr>
                    <tr>
                      <td className="p-4 text-[14px] text-gray-700">
                        <div>
                          <p className="font-[600] mb-0.5">Customer Rating</p>
                          <p className="text-[12px] text-gray-500">Based on verified reviews</p>
                        </div>
                      </td>
                      <td className="p-4 text-center">
                        <div className="flex items-center justify-center gap-1">
                          <Star className="w-3.5 h-3.5 fill-[#FBF3B9] text-[#FBF3B9]" />
                          <span className="text-[14px] text-gray-900">{mainProduct.rating}</span>
                        </div>
                      </td>
                      <td className="p-4 text-center">
                        <div className="flex items-center justify-center gap-1">
                          <Star className="w-3.5 h-3.5 fill-[#FBF3B9] text-[#FBF3B9]" />
                          <span className="text-[14px] text-gray-900">{compareItem.rating}</span>
                        </div>
                      </td>
                    </tr>
                  </tbody>
                </table>
              </div>

              {/* AI Summary */}
              <div className="bg-gradient-to-br from-[#B7B1F2]/10 to-[#FDB7EA]/10 rounded-xl p-5">
                <div className="flex items-start gap-3">
                  <div className="flex-shrink-0 mt-1">
                    <div className="w-8 h-8 rounded-full bg-white flex items-center justify-center shadow-sm">
                      <Sparkles className="w-4 h-4 text-[#B7B1F2]" />
                    </div>
                  </div>
                  <div className="flex-1">
                    <h4 className="text-black mb-3">Recommendations for Your Val Thorens Trip</h4>
                    
                    <div className="space-y-3 text-[14px] text-gray-700 leading-relaxed">
                      {compareItem.id === "helmet-2" && (
                        <>
                          <p>
                            <span className="font-[600] text-black">For your trip:</span> The Smith Vantage MIPS is the better choice. Its superior ventilation (21 vs 16 vents) is crucial for January's cold Alpine conditions at Val Thorens, and MIPS technology is slightly more proven than POC's SPIN system. The lighter weight (450g vs 470g) means better comfort during full days on the slopes.
                          </p>
                          <p>
                            <span className="font-[600] text-black">Consider POC Obex Spin if:</span> You want to save $20 and prefer POC's minimalist aesthetic. The SPIN technology still offers excellent protection, just with a different approach than MIPS.
                          </p>
                          <p>
                            <span className="font-[600] text-black">Budget priority:</span> POC Obex Spin saves you $20 with comparable features. <br />
                            <span className="font-[600] text-black">Performance priority:</span> Smith Vantage MIPS offers better ventilation and is 20g lighter.
                          </p>
                        </>
                      )}
                      {compareItem.id === "helmet-3" && (
                        <>
                          <p>
                            <span className="font-[600] text-black">For your trip:</span> The Smith Vantage MIPS is recommended. While both have MIPS protection, Smith offers significantly better ventilation (21 vs 14 vents) and is notably lighter (450g vs 490g). For a beginner doing full days at altitude, these differences matter for comfort.
                          </p>
                          <p>
                            <span className="font-[600] text-black">Consider Giro Range MIPS if:</span> You're on a tighter budget and don't mind the extra weight. It's $30 cheaper and still offers MIPS protection with a solid 3-year warranty.
                          </p>
                          <p>
                            <span className="font-[600] text-black">Budget priority:</span> Giro Range MIPS at $30 less with same warranty. <br />
                            <span className="font-[600] text-black">Comfort priority:</span> Smith Vantage MIPS - 40g lighter with 50% more ventilation.
                          </p>
                        </>
                      )}
                      {compareItem.id === "helmet-4" && (
                        <>
                          <p>
                            <span className="font-[600] text-black">For your trip:</span> The Smith Vantage MIPS edges ahead. Both have MIPS and audio compatibility, but Smith's superior ventilation (21 vs 18 vents), lighter weight, and longer warranty (3 vs 2 years) make it better value despite being $10 more. The adjustable fit system is also crucial for a beginner still figuring out their gear preferences.
                          </p>
                          <p>
                            <span className="font-[600] text-black">Consider Anon Prime MIPS if:</span> You prefer Burton/Anon's style and want to save $10. It's still a solid helmet with MIPS protection.
                          </p>
                          <p>
                            <span className="font-[600] text-black">Budget priority:</span> Anon Prime MIPS saves $10 with similar core features. <br />
                            <span className="font-[600] text-black">Long-term value:</span> Smith Vantage MIPS with longer warranty and adjustable fit system.
                          </p>
                        </>
                      )}
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}
        </DialogContent>
      </Dialog>
    </div>
  );
}
