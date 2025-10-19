"use client"

import * as React from "react"
import * as DialogPrimitive from "@radix-ui/react-dialog"
import { X } from "lucide-react"
import { cn } from "@/utils"

export const Dialog = DialogPrimitive.Root

export const DialogTrigger = DialogPrimitive.Trigger

export function DialogContent({
  children,
  className,
}: {
  children: React.ReactNode
  className?: string
}) {
  return (
    <DialogPrimitive.Portal>
      <DialogPrimitive.Overlay className="fixed inset-0 bg-black/70 z-50" />
      <DialogPrimitive.Content
        className={cn(
          "fixed z-50 bg-neutral-900 text-white p-6 rounded-xl shadow-xl top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-full max-w-xl",
          className
        )}
      >
        {children}
        <DialogPrimitive.Close className="absolute top-4 right-4 text-neutral-400 hover:text-white">
          <X className="h-5 w-5" />
        </DialogPrimitive.Close>
      </DialogPrimitive.Content>
    </DialogPrimitive.Portal>
  )
}

export function DialogHeader({ children }: { children: React.ReactNode }) {
  return <div className="mb-4">{children}</div>
}

export function DialogTitle({ children }: { children: React.ReactNode }) {
  return <h2 className="text-xl font-semibold">{children}</h2>
}