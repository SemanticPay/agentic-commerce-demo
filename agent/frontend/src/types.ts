export enum WidgetType {
  PRODUCT = 'PRODUCT',
  CART = 'CART',
  PRODUCT_SECTIONS = 'PRODUCT_SECTIONS'
}

export interface ProductWidgetData {
  id: string
  title: string
  description?: string
  price: number
  currency: string
  image_url: string
}

export interface CartWidgetData {
  checkout_url: string
  subtotal_amount: number
  subtotal_amount_currency_code: string
  tax_amount: number
  tax_amount_currency_code: string
  total_amount: number
  total_amount_currency_code: string
}

export interface Widget {
  type: WidgetType
  data: ProductWidgetData | CartWidgetData
  raw_html_string: string
}

export interface ChatMessage {
  role: 'user' | 'agent'
  content: string
  timestamp: string
  widgets?: Widget[]
}
