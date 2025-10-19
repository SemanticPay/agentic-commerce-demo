import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog"
import { Button } from "@/components/ui/button"
import { useState } from "react"

export default function CheckoutModal({
  open,
  onClose,
}: {
  open: boolean
  onClose: () => void
}) {
  const [paymentMethod, setPaymentMethod] = useState("Mastercard")
  const [shippingMethod, setShippingMethod] = useState("Express")
  const [address, setAddress] = useState("123 Luxury Ave, Beverly Hills, CA")

  const paymentOptions = [
    {
      label: "Mastercard – 4482",
      value: "Mastercard",
      icon: "https://upload.wikimedia.org/wikipedia/commons/2/2a/Mastercard-logo.svg",
    },
    {
      label: "Visa – 9210",
      value: "Visa",
      icon: "https://upload.wikimedia.org/wikipedia/commons/5/5e/Visa_Inc._logo.svg",
    },
    {
      label: "Token Network",
      value: "Token",
      icon: null,
    },
  ]

  return (
    <Dialog open={open} onOpenChange={onClose}>
      <DialogContent className="max-w-xl">
        <DialogHeader>
          <DialogTitle>Checkout</DialogTitle>
        </DialogHeader>

        <div className="space-y-4">
          {/* 🛒 Cart Summary */}
          <div>
            <h2 className="text-lg font-semibold mb-2">Cart Summary</h2>
            <ul className="space-y-4 text-sm">
              <li>
                <div className="flex justify-between font-medium">
                  <span>Armani Tuxedo</span>
                  <span>AED 4,400</span>
                </div>
                <div className="text-neutral-400 text-xs">Black · Size 50</div>
              </li>
              <li>
                <div className="flex justify-between font-medium">
                  <span>Gucci Loafers</span>
                  <span>AED 3,250</span>
                </div>
                <div className="text-neutral-400 text-xs">Brown Leather · EU 43</div>
              </li>
              <li>
                <div className="flex justify-between font-medium">
                  <span>Burberry Coat</span>
                  <span>AED 8,800</span>
                </div>
                <div className="text-neutral-400 text-xs">Camel · Size M</div>
              </li>
            </ul>
          </div>

          {/* 💳 Payment Method */}
          <div>
            <label className="block text-sm font-medium mb-1">Payment Method</label>
            <div className="relative">
              <select
                className="w-full border border-neutral-600 bg-neutral-800 rounded px-3 py-2 appearance-none pr-10"
                value={paymentMethod}
                onChange={(e) => setPaymentMethod(e.target.value)}
              >
                {paymentOptions.map((option) => (
                  <option key={option.value} value={option.value}>
                    {option.label}
                  </option>
                ))}
              </select>
              {paymentOptions.find((opt) => opt.value === paymentMethod)?.icon && (
                <img
                  src={
                    paymentOptions.find((opt) => opt.value === paymentMethod)!.icon!
                  }
                  alt={paymentMethod}
                  className="h-5 absolute right-2 top-1/2 -translate-y-1/2 pointer-events-none"
                />
              )}
            </div>
          </div>

          {/* 🚚 Shipping Method */}
          <div>
            <label className="block text-sm font-medium mb-1">Shipping Method</label>
            <select
              className="w-full border border-neutral-600 bg-neutral-800 rounded px-3 py-2"
              value={shippingMethod}
              onChange={(e) => setShippingMethod(e.target.value)}
            >
              <option>Express - AED 90</option>
              <option>Standard - AED 35</option>
              <option>Next Day - AED 140</option>
            </select>
          </div>

          {/* 🏠 Address */}
          <div>
            <label className="block text-sm font-medium mb-1">Shipping Address</label>
            <input
              className="w-full border border-neutral-600 bg-neutral-800 rounded px-3 py-2"
              value={address}
              onChange={(e) => setAddress(e.target.value)}
            />
          </div>

          {/* 📦 Fees & Total */}
          <div className="flex justify-between text-sm border-t border-neutral-700 pt-3">
            <span>Estimated Taxes & Fees</span>
            <span>AED 770</span>
          </div>
          <div className="flex justify-between text-base font-bold">
            <span>Total</span>
            <span>AED 17,270</span>
          </div>

          {/* ✅ Pay Button */}
          <Button className="w-full mt-4 bg-green-600 hover:bg-green-500 text-white">
            Pay Now
          </Button>
        </div>
      </DialogContent>
    </Dialog>
  )
}