import { useState } from "react"
import { ArrowRight } from "lucide-react"
import { Button } from "./ui/button"
import { Input } from "./ui/input"
import { Carousel, CarouselContent, CarouselItem, CarouselNext, CarouselPrevious } from "./ui/carousel"
import { ProductCard } from "./ProductCard"
import { useNavigate } from "react-router-dom"
import { queryAgent } from "../middleware/query"
import { useChat } from "../context/ChatContext"

const products = [
  {
    id: 1,
    image: "https://images.unsplash.com/photo-1720665977720-6a4b93638645?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w3Nzg4Nzd8MHwxfHNlYXJjaHwxfHxwcm9kdWN0JTIwcGhvdG9ncmFwaHklMjB3YXRjaHxlbnwxfHx8fDE3NjA5Mjg2ODF8MA&ixlib=rb-4.1.0&q=80&w=1080&utm_source=figma&utm_medium=referral",
    title: "Minimalist Silver Watch",
    price: "$189",
  },
  {
    id: 2,
    image: "https://images.unsplash.com/photo-1722891067479-5fd39edbfc3d?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w3Nzg4Nzd8MHwxfHNlYXJjaHwxfHxoZWFkcGhvbmVzJTIwd2hpdGUlMjBiYWNrZ3JvdW5kfGVufDF8fHx8MTc2MTAyMTUxNXww&ixlib=rb-4.1.0&q=80&w=1080&utm_source=figma&utm_medium=referral",
    title: "Wireless Headphones",
    price: "$299",
  },
  {
    id: 3,
    image: "https://images.unsplash.com/photo-1626104853886-8f06aed1bec5?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w3Nzg4Nzd8MHwxfHNlYXJjaHwxfHxzdW5nbGFzc2VzJTIwcHJvZHVjdHxlbnwxfHx8fDE3NjA5NjA3OTh8MA&ixlib=rb-4.1.0&q=80&w=1080&utm_source=figma&utm_medium=referral",
    title: "Classic Aviator Sunglasses",
    price: "$159",
  },
  {
    id: 4,
    image: "https://images.unsplash.com/photo-1579718091289-38794781a3c5?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w3Nzg4Nzd8MHwxfHNlYXJjaHwxfHxiYWNrcGFjayUyMG1pbmltYWxpc3R8ZW58MXx8fHwxNzYxMDIxNTE2fDA&ixlib=rb-4.1.0&q=80&w=1080&utm_source=figma&utm_medium=referral",
    title: "Canvas Travel Backpack",
    price: "$129",
  },
  {
    id: 5,
    image: "https://images.unsplash.com/photo-1720537262372-57e81c4db13c?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w3Nzg4Nzd8MHwxfHNlYXJjaHwxfHxjb2ZmZWUlMjBtdWclMjBjZXJhbWljfGVufDF8fHx8MTc2MDkwOTcwN3ww&ixlib=rb-4.1.0&q=80&w=1080&utm_source=figma&utm_medium=referral",
    title: "Ceramic Coffee Mug",
    price: "$24",
  },
  {
    id: 6,
    image: "https://images.unsplash.com/photo-1719523677291-a395426c1a87?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w3Nzg4Nzd8MHwxfHNlYXJjaHwxfHxydW5uaW5nJTIwc2hvZXMlMjBwcm9kdWN0fGVufDF8fHx8MTc2MDkzNjA2OHww&ixlib=rb-4.1.0&q=80&w=1080&utm_source=figma&utm_medium=referral",
    title: "Performance Running Shoes",
    price: "$145",
  },
];

export default function HomePage() {
  const [searchQuery, setSearchQuery] = useState("")
  const [loading, setLoading] = useState(false)
  const navigate = useNavigate()
  const { addMessage } = useChat()

  async function handleSearch() {
    if (!searchQuery.trim()) return
    setLoading(true)
    try {
      addMessage({ id: crypto.randomUUID(), role: "user", text: searchQuery })
      const res = await queryAgent(searchQuery)
      addMessage({ id: crypto.randomUUID(), role: "agent", text: res.response })
      navigate("/chat")
    } catch (err) {
      console.error("query error", err)
    } finally {
      setLoading(false)
    }
  }

  function handleKeyPress(e: React.KeyboardEvent<HTMLInputElement>) {
    if (e.key === "Enter") handleSearch()
  }

  return (
    <div className="min-h-screen bg-white">
      <main className="max-w-7xl mx-auto px-8 py-12">
        <div className="max-w-3xl mx-auto space-y-8">
          <div className="text-center space-y-4">
            <h1 className="text-black">What's on your wishlist today?</h1>
            <p className="text-gray-600 max-w-xl mx-auto">Say the vibe, and we'll do the shopping.</p>
          </div>

          <div className="relative">
            <Input
              type="text"
              placeholder="Describe what you have in mind"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              onKeyPress={handleKeyPress}
              disabled={loading}
              className="w-full h-14 pl-6 pr-16 rounded-full border-0 bg-white text-gray-800 placeholder:text-gray-400 shadow-[0_4px_20px_rgba(183,177,242,0.15)] focus-visible:ring-0 focus-visible:shadow-[0_4px_24px_rgba(183,177,242,0.3),0_0_0_4px_rgba(183,177,242,0.2)] transition-shadow duration-200 ease-in-out"
            />
            <Button
              onClick={handleSearch}
              size="icon"
              disabled={loading}
              className="absolute right-2 top-1/2 -translate-y-1/2 h-10 w-10 rounded-full text-white bg-gradient-to-r from-[#B7B1F2] to-[#FDB7EA] shadow-lg hover:shadow-xl hover:scale-105 transition-all duration-200 ease-out"
            >
              {loading ? (
                <div className="animate-spin border-2 border-white border-t-transparent rounded-full w-5 h-5" />
              ) : (
                <ArrowRight className="w-5 h-5" />
              )}
            </Button>
          </div>

          <div className="flex items-center justify-center gap-3 flex-wrap">
            <span className="text-gray-500 text-sm">Try:</span>
            {["Vintage leather jacket", "Minimalist desk setup", "Y2K accessories"].map((s) => (
              <button
                key={s}
                onClick={() => setSearchQuery(s)}
                className="px-4 py-2 rounded-full bg-white text-gray-700 shadow-[0_2px_12px_rgba(183,177,242,0.12)] hover:bg-gradient-to-r hover:from-[#FFDCCC] hover:to-[#FBF3B9] hover:shadow-[0_4px_16px_rgba(253,183,234,0.2)] transition-all duration-200 text-sm"
              >
                {s}
              </button>
            ))}
          </div>
        </div>

        <div className="mt-16 space-y-6">
          <div className="flex items-center justify-between">
            <h2 className="text-gray-800">Inspired for you</h2>
          </div>
          <Carousel opts={{ align: "start", loop: true }} className="w-full">
            <CarouselContent className="-ml-4">
              {products.map((p) => (
                <CarouselItem key={p.id} className="pl-4 basis-1/3 md:basis-1/4 lg:basis-1/5 xl:basis-[16.666%]">
                  <ProductCard image={p.image} title={p.title} price={p.price} />
                </CarouselItem>
              ))}
            </CarouselContent>
            <CarouselPrevious className="border-0 bg-white text-gray-700 shadow-[0_2px_16px_rgba(183,177,242,0.15)] hover:bg-gradient-to-r hover:from-[#B7B1F2] hover:to-[#FDB7EA] hover:text-white hover:shadow-lg transition-all duration-200" />
            <CarouselNext className="border-0 bg-white text-gray-700 shadow-[0_2px_16px_rgba(183,177,242,0.15)] hover:bg-gradient-to-r hover:from-[#B7B1F2] hover:to-[#FDB7EA] hover:text-white hover:shadow-lg transition-all duration-200" />
          </Carousel>
        </div>
      </main>
    </div>
  )
}